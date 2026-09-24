"""Retagger that corrects morphological forms using replacement-based analysis.

Applies ``WordReplacementAnalyzer`` to selected words of a Vabamorf
``morph_analysis`` layer and, where the analysis disagrees with what is there,
replaces the annotation with the matching Vabamorf candidate.

Which words to analyse is left to the caller, because the analysis costs a model
call per word and is only worth spending where a form is genuinely in doubt --
words in conflict with the syntax, say. The caller supplies a predicate over
spans; every other word is left alone.

Corrections are always selected from Vabamorf's own candidate analyses, never
written from the predicted form directly. A form on its own cannot be turned into
a Vabamorf annotation, which needs a lemma, root and ending as well. A useful
side effect is that the additive/illative split resolves itself: a distribution
may put most of its weight on ``sg ill``, but if Vabamorf offers only ``adt`` for
the word in hand, ``adt`` is what the correction can and does use.
"""

from __future__ import annotations

from typing import Callable, Dict, List, MutableMapping, Optional, Tuple

from estnltk import Layer, Text
from estnltk.common import (
    DEFAULT_PARAM_COMPOUND,
    DEFAULT_PARAM_PHONETIC,
    DEFAULT_PARAM_STEM,
)
from estnltk.taggers import Retagger, VabamorfAnalyzer, VabamorfTagger
from estnltk.taggers.standard.morph_analysis.postanalysis_tagger import (
    PostMorphAnalysisTagger,
)
from estnltk.taggers.standard.text_segmentation.compound_token_tagger import (
    CompoundTokenTagger,
)
from estnltk.vabamorf.morf import VM_LEXICONS, Vabamorf

from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_analyzer import (
    WordReplacementAnalyzer,
)

# Values written to the correction flag attribute. Deliberately the same
# vocabulary as MorphHomonymsRetagger's homonym_correction, so a reader does not
# have to learn two schemes.
FLAG_CORRECTED = "corrected"
FLAG_AGREED = "agreed"
FLAG_DISAGREED = "disagreed"
FLAG_NONE = "none"

DEFAULT_FLAG_ATTRIBUTE = "llm_morph_correction"


class LLMmorphCorrectionsRetagger(Retagger):
    """Correct selected words of a Vabamorf morph layer via replacement analysis.

    Outcomes are recorded per word in the flag attribute:

    ``'none'``
        The word was not selected for analysis, or no candidate could be analysed.
    ``'agreed'``
        The most likely form is one the word already carries; only the matching
        analyses are kept.
    ``'corrected'``
        The most likely form available from Vabamorf's candidates differs from
        what the word carried, and replaces it.
    ``'disagreed'``
        The analysis put its weight on forms Vabamorf offers no candidate for, so
        nothing could be selected and the word is unchanged. These are the words
        worth inspecting.
    """

    conf_param = (
        "analyzer",
        "select",
        "flag_attribute",
        "sentences_layer",
        "words_layer",
        "slang_lex",
        "compound",
        "phonetic",
        "stem",
        "use_postanalysis",
        "candidate_layer_name",
        "_vabamorf_analyzer",
        "_post_morph",
        "check_output_consistency",
    )

    def __init__(
        self,
        analyzer: WordReplacementAnalyzer,
        select: Callable[[object], bool],
        output_layer: str = "morph_analysis",
        sentences_layer: str = "sentences",
        words_layer: str = "words",
        flag_attribute: str = DEFAULT_FLAG_ATTRIBUTE,
        slang_lex: bool = True,
        use_postanalysis: bool = True,
        compound: bool = DEFAULT_PARAM_COMPOUND,
        phonetic: bool = DEFAULT_PARAM_PHONETIC,
        stem: bool = DEFAULT_PARAM_STEM,
        vm_instance: Optional[Vabamorf] = None,
    ):
        """Initialise the retagger.

        Parameters
        ----------
        analyzer:
            Produces the form distribution for a word.
        select:
            Called with each span of the layer; return ``True`` to analyse that
            word. Keep it narrow -- each ``True`` costs a model call.
        flag_attribute:
            Name of the attribute recording what happened to each word.
        slang_lex, use_postanalysis, compound, phonetic, stem:
            Settings for regenerating Vabamorf's candidates. The defaults mirror
            ``VabamorfWithBertTagger``, which is what the ENC corpus was
            annotated with; they must match the corpus, or a correction can
            introduce an analysis the original pipeline never produced.
        """
        if vm_instance is not None and slang_lex:
            raise ValueError(
                "(!) Cannot use slang_lex=True if vm_instance is already provided"
            )

        self.analyzer = analyzer
        self.select = select
        self.output_layer = output_layer
        self.sentences_layer = sentences_layer
        self.words_layer = words_layer
        self.flag_attribute = flag_attribute
        self.slang_lex = slang_lex
        self.use_postanalysis = use_postanalysis
        self.compound = compound
        self.phonetic = phonetic
        self.stem = stem
        self.input_layers = [sentences_layer, words_layer, output_layer]
        # The layer's attributes are extended at run time, so estnltk's output
        # consistency check would otherwise reject the result.
        self.check_output_consistency = False

        base_attributes = tuple(
            attr
            for attr in VabamorfTagger.output_attributes
            if not (stem and attr == "lemma")
        )
        self.output_attributes = base_attributes + (flag_attribute,)

        if vm_instance is None:
            vm_instance = self._make_vm_instance(slang_lex)
        self.candidate_layer_name = f"{output_layer}__vm_candidates"
        self._vabamorf_analyzer = VabamorfAnalyzer(
            output_layer=self.candidate_layer_name,
            input_words_layer=words_layer,
            input_sentences_layer=sentences_layer,
            compound=compound,
            phonetic=phonetic,
            stem=stem,
            vm_instance=vm_instance,
        )
        self._post_morph = (
            PostMorphAnalysisTagger(
                output_layer=self.candidate_layer_name,
                input_compound_tokens_layer=CompoundTokenTagger.output_layer,
                input_words_layer=words_layer,
                stem=stem,
            )
            if use_postanalysis
            else None
        )

    @staticmethod
    def _make_vm_instance(slang_lex: bool) -> Vabamorf:
        """Build the Vabamorf instance, mirroring VabamorfTagger's own logic."""
        if not slang_lex:
            return Vabamorf.instance()
        nosp = [lex for lex in VM_LEXICONS if lex.endswith("_nosp")]
        assert nosp, (
            "(!) Slang words lexicon with suffix '_nosp' not found from the "
            "default list of lexicons: {!r}".format(VM_LEXICONS)
        )
        return Vabamorf(lexicon_dir=nosp[-1])

    def _build_candidate_map(
        self, text: Text, layers: MutableMapping[str, Layer], status: dict
    ) -> Dict[Tuple[int, int], List[dict]]:
        """Regenerate Vabamorf's candidate analyses, keyed by span boundaries.

        Disambiguation is not applied, so every analysis Vabamorf considers
        possible is available to select from.
        """
        candidate_layer = self._vabamorf_analyzer.make_layer(text, layers, status)
        if self._post_morph is not None:
            post_layers = dict(layers)
            post_layers[self.candidate_layer_name] = candidate_layer
            if CompoundTokenTagger.output_layer not in post_layers:
                post_layers[CompoundTokenTagger.output_layer] = Layer(
                    name=CompoundTokenTagger.output_layer,
                    attributes=CompoundTokenTagger.output_attributes,
                    text_object=text,
                    ambiguous=False,
                )
            self._post_morph.change_layer(text, post_layers, status)
            candidate_layer = post_layers[self.candidate_layer_name]
        return {
            (span.start, span.end): [dict(a) for a in span.annotations]
            for span in candidate_layer
        }

    def _sentence_tokens(self, layers: MutableMapping[str, Layer]) -> List[List[str]]:
        """Tokens of each sentence, so the analyzer gets a sentence at a time."""
        return [[w.text for w in sentence] for sentence in layers[self.sentences_layer]]

    def _rewrite(self, span, annotations: Optional[List[dict]], flag: str) -> None:
        """Replace a span's annotations and stamp the flag.

        ``annotations=None`` keeps what is there and only adds the flag.
        """
        if annotations is None:
            annotations = [dict(a) for a in span.annotations]
        for annotation in annotations:
            annotation[self.flag_attribute] = flag
        span.clear_annotations()
        for annotation in annotations:
            span.add_annotation(annotation)

    def _change_layer(
        self, text: Text, layers: MutableMapping[str, Layer], status: dict = None
    ) -> None:
        assert self.output_layer in layers
        assert self.sentences_layer in layers
        assert self.words_layer in layers
        status = status if status is not None else {}

        morph_layer = layers[self.output_layer]
        if self.flag_attribute not in morph_layer.attributes:
            morph_layer.attributes = tuple(morph_layer.attributes) + (
                self.flag_attribute,
            )
        candidates_by_span = self._build_candidate_map(text, layers, status)

        # Map every word span to its sentence and its index within it, so a
        # selected word can be handed to the analyzer with its context.
        location: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for s_index, sentence in enumerate(layers[self.sentences_layer]):
            for w_index, word in enumerate(sentence):
                location[(word.start, word.end)] = (s_index, w_index)
        sentences = self._sentence_tokens(layers)

        analysed = agreed = corrected = disagreed = 0
        for span in morph_layer:
            key = (span.start, span.end)
            if not self.select(span):
                self._rewrite(span, None, FLAG_NONE)
                continue
            where = location.get(key)
            if where is None:
                self._rewrite(span, None, FLAG_NONE)
                continue

            s_index, w_index = where
            distribution = self.analyzer.analyze(sentences[s_index], w_index)
            if not distribution:
                self._rewrite(span, None, FLAG_NONE)
                continue
            analysed += 1

            # Only forms Vabamorf actually offers for this word can be selected.
            available = candidates_by_span.get(key, [])
            offered = {a.get("form") for a in available}
            usable = [(form, share) for form, share in distribution if form in offered]
            if not usable:
                self._rewrite(span, None, FLAG_DISAGREED)
                disagreed += 1
                continue

            best_form = usable[0][0]
            existing = [dict(a) for a in span.annotations if a.get("form") == best_form]
            if existing:
                self._rewrite(span, existing, FLAG_AGREED)
                agreed += 1
            else:
                self._rewrite(
                    span,
                    [dict(a) for a in available if a.get("form") == best_form],
                    FLAG_CORRECTED,
                )
                corrected += 1

        morph_layer.meta["llm_morph_corrections_retagger"] = {
            "analysed_words": analysed,
            "agreed_words": agreed,
            "corrected_words": corrected,
            "disagreed_words": disagreed,
            "output_layer": self.output_layer,
        }
        layers[self.output_layer] = morph_layer
