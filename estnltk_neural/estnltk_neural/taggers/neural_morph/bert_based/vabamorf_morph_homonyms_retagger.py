"""EstNLTK retagger for correcting form homonymy on a Vabamorf morph layer.

Unlike :class:`MorphHomonymsRetagger`, which refines a Bert-based layer, this
retagger works on a Vabamorf ``morph_analysis`` layer. Such a layer is already
disambiguated -- typically one analysis per word -- so a retagger that only
filters has nothing left to choose from. This component therefore regenerates
Vabamorf's candidate analyses internally and picks from those.

Every correction is a real Vabamorf analysis, complete with lemma/root/ending.
The expert's prediction is never written directly, because a (form,
partofspeech) pair cannot be turned into a Vabamorf analysis.
"""

from __future__ import annotations

from typing import MutableMapping, Optional

from estnltk import Layer, Text
from estnltk.taggers import VabamorfAnalyzer, VabamorfTagger
from estnltk.taggers.standard.morph_analysis.postanalysis_tagger import (
    PostMorphAnalysisTagger,
)
from estnltk.taggers.standard.text_segmentation.compound_token_tagger import (
    CompoundTokenTagger,
)
from estnltk.vabamorf.morf import Vabamorf, VM_LEXICONS
from estnltk.common import (
    DEFAULT_PARAM_COMPOUND,
    DEFAULT_PARAM_PHONETIC,
    DEFAULT_PARAM_STEM,
)

from estnltk_neural.taggers.neural_morph.bert_based.morph_homonyms_retagger import (
    MorphHomonymsRetagger,
)

# Values written to the correction flag attribute.
FLAG_CORRECTED = "corrected"
FLAG_AGREED = "agreed"
FLAG_DISAGREED = "disagreed"
FLAG_NONE = "none"

DEFAULT_FLAG_ATTRIBUTE = "homonym_correction"


class VabamorfMorphHomonymsRetagger(MorphHomonymsRetagger):
    """Correct form homonymy on a Vabamorf morph analysis layer.

    The component reuses :class:`MorphHomonymsRetagger`'s expert machinery --
    the homonym lexicon gate, the skipping of sentences without homonyms and
    the per-sentence expert invocation -- and replaces only the correction
    step.

    For every homonymous word the expert's (form, partofspeech) prediction is
    compared against the word's current analyses and, if it agrees with none of
    them, against Vabamorf's full candidate set for that word. Three outcomes
    are possible, recorded in the ``homonym_correction`` attribute:

    ``'none'``
        The word is not in the homonym lexicon, or the expert returned no
        prediction for it. Left untouched.
    ``'agreed'``
        The expert confirmed one of the word's existing analyses; only the
        matching analyses are kept.
    ``'corrected'``
        The expert disagreed with the existing analyses, and Vabamorf's
        candidate set contained the predicted form. The matching candidates
        replace the existing ones.
    ``'disagreed'``
        The expert disagreed with the existing analyses, but no Vabamorf
        candidate carried the predicted form, so the word was left unchanged.
        The expert is a classifier: it predicts a (form, partofspeech) pair and
        cannot supply the ``lemma``/``root``/``ending`` a Vabamorf analysis
        needs, so its prediction can only ever be *selected* from Vabamorf's
        candidates, never written directly. These are the words worth
        inspecting: the expert wanted a change that the analyser could not
        express.

    Note on candidate regeneration
    ------------------------------
    The candidates must match those the corpus was annotated with, otherwise a
    "correction" can introduce an analysis the original pipeline never
    produced. The defaults here mirror ``VabamorfWithBertTagger``
    (``slang_lex=True``, ``use_postanalysis=True``, ``compound=True``,
    ``phonetic=False``, ``stem=False``), which is what the ENC corpus
    annotation used. Disambiguation is deliberately *not* applied: the point is
    to see every candidate.
    """

    conf_param = MorphHomonymsRetagger.conf_param + (
        "slang_lex",
        "compound",
        "phonetic",
        "stem",
        "use_postanalysis",
        "flag_attribute",
        "candidate_layer_name",
        "_vabamorf_analyzer",
        "_post_morph",
        "check_output_consistency",
    )

    def __init__(
        self,
        output_layer: str = "morph_analysis",
        slang_lex: bool = True,
        use_postanalysis: bool = True,
        compound: bool = DEFAULT_PARAM_COMPOUND,
        phonetic: bool = DEFAULT_PARAM_PHONETIC,
        stem: bool = DEFAULT_PARAM_STEM,
        flag_attribute: str = DEFAULT_FLAG_ATTRIBUTE,
        vm_instance: Optional[Vabamorf] = None,
        **kwargs,
    ):
        """Initialise the retagger.

        Parameters
        ----------
        output_layer:
            Name of the Vabamorf morph analysis layer to correct.
        slang_lex:
            Use Vabamorf's extended ('_nosp') lexicon when regenerating
            candidates. Defaults to ``True``, matching ``VabamorfWithBertTagger``
            and the settings the ENC corpus was annotated with.
        use_postanalysis:
            Apply ``PostMorphAnalysisTagger`` to the regenerated candidates, as
            ``VabamorfWithBertTagger`` does. Uses an empty compound tokens
            layer, again matching that tagger's default.
        compound, phonetic, stem:
            Passed on to ``VabamorfAnalyzer``. These do not affect which
            candidates exist, but they do determine the shape of the
            ``root``/``lemma`` values written back, so they must match the
            corpus.
        flag_attribute:
            Name of the attribute recording what happened to each word.
        vm_instance:
            An explicit Vabamorf instance. Cannot be combined with
            ``slang_lex=True``, mirroring ``VabamorfTagger``'s behaviour.
        **kwargs:
            Forwarded to :class:`MorphHomonymsRetagger`.
        """

        super().__init__(output_layer=output_layer, **kwargs)

        if vm_instance is not None and slang_lex:
            raise ValueError(
                "(!) Cannot use slang_lex=True if vm_instance is already provided"
            )

        self.slang_lex = slang_lex
        self.compound = compound
        self.phonetic = phonetic
        self.stem = stem
        self.use_postanalysis = use_postanalysis
        self.flag_attribute = flag_attribute
        # The retagger extends the layer's attributes on the fly, so estnltk's
        # output consistency check would reject the result.
        self.check_output_consistency = False

        # The expert model's own output attributes are irrelevant here: this
        # retagger never writes the expert's prediction into the layer, it only
        # uses it to select among Vabamorf's analyses. What the retagger does
        # produce is a Vabamorf morph layer plus the correction flag, and
        # estnltk checks the result against this, so it must be declared in
        # full rather than as the flag alone.
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
            input_words_layer=self.words_layer,
            input_sentences_layer=self.sentences_layer,
            compound=compound,
            phonetic=phonetic,
            stem=stem,
            vm_instance=vm_instance,
        )
        self._post_morph = (
            PostMorphAnalysisTagger(
                output_layer=self.candidate_layer_name,
                input_compound_tokens_layer=CompoundTokenTagger.output_layer,
                input_words_layer=self.words_layer,
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
        nosp_lexicons = [lex for lex in VM_LEXICONS if lex.endswith("_nosp")]
        assert nosp_lexicons, (
            "(!) Slang words lexicon with suffix '_nosp' not found from the "
            "default list of lexicons: {!r}".format(VM_LEXICONS)
        )
        return Vabamorf(lexicon_dir=nosp_lexicons[-1])

    def _build_candidate_map(
        self,
        text: Text,
        layers: MutableMapping[str, Layer],
        status: dict,
    ) -> dict[tuple[int, int], list[dict]]:
        """Regenerate Vabamorf's candidate analyses, keyed by span boundaries.

        Disambiguation is not applied, so every analysis Vabamorf considers
        possible is present.
        """

        candidate_layer = self._vabamorf_analyzer.make_layer(text, layers, status)

        if self._post_morph is not None:
            post_layers = dict(layers)
            post_layers[self.candidate_layer_name] = candidate_layer
            if CompoundTokenTagger.output_layer not in post_layers:
                # VabamorfWithBertTagger hands post-analysis an empty compound
                # tokens layer when none is available; match that exactly.
                post_layers[CompoundTokenTagger.output_layer] = Layer(
                    name=CompoundTokenTagger.output_layer,
                    attributes=CompoundTokenTagger.output_attributes,
                    text_object=text,
                    ambiguous=False,
                )
            self._post_morph.change_layer(text, post_layers, status)
            candidate_layer = post_layers[self.candidate_layer_name]

        return {
            (span.start, span.end): [dict(ann) for ann in span.annotations]
            for span in candidate_layer
        }

    def _correct_layer(
        self,
        source_layer: Layer,
        predicted_by_span: dict[tuple[int, int], Layer],
        candidates_by_span: dict[tuple[int, int], list[dict]],
    ) -> Layer:
        """Select the expert-endorsed Vabamorf analysis for homonymous words.

        ``candidates_by_span`` is required rather than optional: an empty
        candidate map would send every disagreement down the disagreed branch
        and silently correct nothing.
        """

        if self.flag_attribute not in source_layer.attributes:
            source_layer.attributes = tuple(source_layer.attributes) + (
                self.flag_attribute,
            )

        inspected_words = 0
        agreed_words = 0
        corrected_words = 0
        disagreed_words = 0

        for source_span in source_layer:
            key = (source_span.start, source_span.end)
            predicted_span = predicted_by_span.get(key)
            is_homonym = self._is_homonym_word(source_span.text)
            predicted_label = (
                self._extract_predicted_label(predicted_span)
                if predicted_span is not None
                else None
            )

            if not is_homonym or predicted_label is None:
                self._rewrite(source_layer, source_span, None, FLAG_NONE)
                continue

            inspected_words += 1
            predicted_form, predicted_pos = predicted_label

            def _matches(annotation) -> bool:
                return (
                    annotation.get("form") == predicted_form
                    and annotation.get("partofspeech") == predicted_pos
                )

            existing_matches = [
                dict(ann) for ann in source_span.annotations if _matches(ann)
            ]
            if existing_matches:
                # The expert confirms an analysis the word already has.
                self._rewrite(source_layer, source_span, existing_matches, FLAG_AGREED)
                agreed_words += 1
                continue

            candidate_matches = [
                dict(ann) for ann in candidates_by_span.get(key, []) if _matches(ann)
            ]
            if candidate_matches:
                # The expert disagrees with the current analysis, and Vabamorf
                # does offer the predicted form: apply the correction.
                self._rewrite(
                    source_layer, source_span, candidate_matches, FLAG_CORRECTED
                )
                corrected_words += 1
                continue

            # The expert disagrees, but Vabamorf has no analysis carrying the
            # predicted form, so there is nothing valid to switch to and the
            # word is left as it is. Recorded separately from 'agreed': the
            # expert wanted a change and could not get one, which is exactly the
            # case worth inspecting in a corpus.
            self._rewrite(source_layer, source_span, None, FLAG_DISAGREED)
            disagreed_words += 1

        source_layer.meta["vabamorf_morph_homonyms_retagger"] = {
            "inspected_words": inspected_words,
            "agreed_words": agreed_words,
            "corrected_words": corrected_words,
            "disagreed_words": disagreed_words,
            "homonym_list_size": len(self.homonym_words),
            "output_layer": self.output_layer,
        }
        return source_layer

    def _rewrite(
        self,
        layer: Layer,
        span,
        annotations: Optional[list[dict]],
        flag: str,
    ) -> None:
        """Replace a span's annotations and stamp the correction flag.

        When ``annotations`` is ``None`` the existing annotations are kept and
        only the flag is added.
        """

        if annotations is None:
            annotations = [dict(ann) for ann in span.annotations]
        for annotation in annotations:
            annotation[self.flag_attribute] = flag
        span.clear_annotations()
        for annotation in annotations:
            span.add_annotation(annotation)

    def _copy_morph_layer(self, morph_layer: Layer) -> Layer:
        """Copy a morph layer, preserving its structure and metadata."""

        copied_layer = Layer(
            name=morph_layer.name,
            attributes=morph_layer.attributes,
            text_object=morph_layer.text_object,
            parent=morph_layer.parent,
            enveloping=morph_layer.enveloping,
            ambiguous=morph_layer.ambiguous,
            default_values=morph_layer.default_values.copy(),
        )
        for span in morph_layer:
            for annotation in span.annotations:
                copied_layer.add_annotation(span.base_span, **annotation)
        copied_layer.meta.update(morph_layer.meta)
        return copied_layer

    def _make_layer(
        self,
        text: Text,
        layers: MutableMapping[str, Layer],
        status: dict = None,
    ) -> Layer:
        """Produce a corrected copy of the morph layer, leaving the source as is."""

        source_layer = layers[self.output_layer]
        new_layer = self._copy_morph_layer(source_layer)
        new_layer.name = self.output_layer

        working_layers = dict(layers)
        working_layers[self.output_layer] = new_layer
        self._change_layer(text, working_layers, status or {})
        return working_layers[self.output_layer]

    def _change_layer(
        self,
        text: Text,
        layers: MutableMapping[str, Layer],
        status: dict = None,
    ) -> None:
        """Correct the Vabamorf morph analysis layer in place."""

        assert self.output_layer in layers
        assert self.sentences_layer in layers
        assert self.words_layer in layers

        status = status if status is not None else {}
        morph_layer = layers[self.output_layer]
        predicted_by_span = self._build_predicted_span_map(text, layers, status)
        candidates_by_span = self._build_candidate_map(text, layers, status)
        self._correct_layer(
            source_layer=morph_layer,
            predicted_by_span=predicted_by_span,
            candidates_by_span=candidates_by_span,
        )
        layers[self.output_layer] = morph_layer
