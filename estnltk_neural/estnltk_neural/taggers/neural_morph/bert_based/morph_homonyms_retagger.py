"""EstNLTK retagger for correcting morphological homonyms.

The retagger uses a homonym lexicon as a gate and a BERT-based expert model
to re-evaluate only the words that are known homonymous forms. It leaves the
rest of the morphological layer untouched.
"""

from __future__ import annotations

from pathlib import Path
from typing import Collection, MutableMapping, Optional, Tuple, Union

from estnltk import Layer, Text
from estnltk.downloader import get_resource_paths
from estnltk.taggers import Retagger
from estnltk_core.layer_operations import extract_section

from estnltk_neural.common import neural_abs_path
from estnltk_neural.taggers.neural_morph.bert_based.bert_morph_tagger import (
    BertMorphTagger,
)

# Alias of the form homonymy expert model in estnltk_resources, used when the
# caller does not provide an explicit model_location. This must name the
# *expert* model: BertMorphTagger's own default resolves the alias
# 'bert_morph_tagging', which points to the general-purpose model and would
# therefore silently disable the expert.
DEFAULT_EXPERT_MODEL = "bert_morph_expert"

# The homonymous word forms lexicon is shipped inside the package. Resolve it
# with neural_abs_path so that it is found wherever the package happens to be
# installed.
DEFAULT_HOMONYM_LIST_PATH = Path(
    neural_abs_path(
        "taggers/neural_morph/bert_based/homonymous_word_forms/homonymous_words.txt"
    )
)


def _load_homonym_words(path: Path, ignore_case: bool = True) -> set[str]:
    """Load homonymous words from a plain text file.

    Parameters
    ----------
    path:
        Path to a file containing one homonymous word per line.
    ignore_case:
        If ``True``, the words are normalised to lowercase for matching.

    Returns
    -------
    set[str]
        The loaded homonymous words.
    """

    if not path.exists():
        raise FileNotFoundError(f"Could not find homonym list file at {path!s}.")

    with path.open("r", encoding="utf-8") as file_handle:
        if ignore_case:
            return {line.strip().lower() for line in file_handle if line.strip()}
        return {line.strip() for line in file_handle if line.strip()}


class MorphHomonymsRetagger(Retagger):
    """Retagger that corrects morphological homonyms with a BERT expert.

    The retagger assumes that the input text has already been morphologically
    analysed. It then applies a homonym lexicon gate and only re-evaluates
    words that belong to that lexicon. If the expert model predicts a label
    that already exists among the word's analyses, the retagger keeps only the
    matching analyses. If the expert disagrees with all of them, its own
    prediction replaces them, so the expert's correction is always applied.

    Words outside the homonym lexicon, and words the expert was not asked
    about, are left exactly as they were.
    """

    conf_param = (
        "model_location",
        "homonym_list_path",
        "homonym_words",
        "ignore_case",
        "get_top_n_predictions",
        "prediction_layer_name",
        "token_level",
        "split_pos_form",
        "sentences_layer",
        "words_layer",
        "device",
        "input_layers",
        "_bert_morph_tagger",
        "output_attributes",
    )

    def __init__(
        self,
        model_location: Optional[str] = None,
        homonym_list_path: Optional[Union[str, Path]] = None,
        homonym_words: Optional[Collection[str]] = None,
        ignore_case: bool = True,
        get_top_n_predictions: int = 1,
        output_layer: str = "bert_morph_tagging",
        token_level: bool = False,
        split_pos_form: bool = True,
        sentences_layer: str = "sentences",
        words_layer: str = "words",
        device: str = "cpu",
        **kwargs,
    ):
        """Initialise the retagger.

        Parameters
        ----------
        model_location:
            Path to the BERT expert model directory. If omitted, the homonymy
            expert model is looked up from estnltk's resources and downloaded
            if missing.
        homonym_list_path:
            Path to a newline-separated list of homonymous word forms.
            Used when ``homonym_words`` is not provided.
        homonym_words:
            Optional in-memory collection of homonymous words. If supplied,
            this takes precedence over ``homonym_list_path``.
        ignore_case:
            If ``True``, homonym matching is done in lowercase.
        get_top_n_predictions:
            Number of expert labels to request from the BERT model.
            The first matching analysis is used for retagging.
        output_layer:
            Name of the existing morphological layer that will be modified in
            place.
        sentences_layer:
            Name of the sentence layer.
        words_layer:
            Name of the word layer.
        device:
            The device to run the expert model on ('cpu' or 'cuda'). Defaults
            to 'cpu'. Passed on to the underlying BertMorphTagger.
        **kwargs:
            Additional tokenizer kwargs forwarded to the internal BERT tagger.

        Raises
        ------
        Exception
            Raised when the expert model's resources are missing and they
            cannot be downloaded.
        """

        if model_location is None:
            # Try to get the resources path for the homonymy expert model.
            # Attempt to download, if missing.
            resources_path = get_resource_paths(
                DEFAULT_EXPERT_MODEL, only_latest=True, download_missing=True
            )
            if resources_path is None:
                raise Exception(
                    "MorphHomonymsRetagger's expert model resources have not been "
                    f"downloaded. Use estnltk.download({DEFAULT_EXPERT_MODEL!r}) to "
                    "get the missing resources. Alternatively, you can specify the "
                    "directory containing the model via parameter model_location at "
                    "creating the retagger."
                )
            self.model_location = str(resources_path)
        else:
            self.model_location = model_location

        self.homonym_list_path = (
            str(homonym_list_path) if homonym_list_path is not None else None
        )
        self.ignore_case = ignore_case
        self.get_top_n_predictions = get_top_n_predictions
        self.output_layer = output_layer
        self.sentences_layer = sentences_layer
        self.words_layer = words_layer
        self.device = device
        self.input_layers = [sentences_layer, words_layer, output_layer]
        self.token_level = token_level
        self.split_pos_form = split_pos_form

        if homonym_words is not None:
            self.homonym_words = {
                word.lower() if ignore_case else str(word)
                for word in homonym_words
                if str(word).strip()
            }
        else:
            resolved_path = (
                Path(homonym_list_path)
                if homonym_list_path is not None
                else DEFAULT_HOMONYM_LIST_PATH
            )
            self.homonym_list_path = str(resolved_path)
            self.homonym_words = _load_homonym_words(
                resolved_path, ignore_case=ignore_case
            )
        self.output_attributes = (
            ["bert_tokens", "form", "partofspeech", "probability"]
            if self.split_pos_form
            else ["bert_tokens", "morph_label", "probability"]
        )
        prediction_output_layer = f"{self.output_layer}__homonym_predictions"
        self.prediction_layer_name = prediction_output_layer
        self._bert_morph_tagger = BertMorphTagger(
            model_location=self.model_location,
            get_top_n_predictions=get_top_n_predictions,
            output_layer=prediction_output_layer,
            sentences_layer=sentences_layer,
            words_layer=words_layer,
            token_level=token_level,
            split_pos_form=split_pos_form,
            device=device,
            **kwargs,
        )

    def _is_homonym_word(self, word_text: str) -> bool:
        """Check whether a surface form belongs to the homonym lexicon."""

        candidate = word_text.lower() if self.ignore_case else word_text
        return candidate in self.homonym_words

    def _extract_predicted_label(self, predicted_span) -> Optional[Tuple[str, str]]:
        """Return the expert's best form/POS pair for a predicted word."""

        if not predicted_span.annotations:
            return None

        predicted_annotation = predicted_span.annotations[0]
        form = predicted_annotation.get("form")
        partofspeech = predicted_annotation.get("partofspeech")
        if form is None or partofspeech is None:
            return None
        return str(form), str(partofspeech)

    def _build_expert_annotation(
        self,
        predicted_span,
        target_attributes: Collection[str],
    ) -> dict:
        """Build a replacement annotation for the target layer from the expert.

        Used when the expert disagrees with every existing analysis of a
        homonymous word: the expert's own prediction then replaces them.

        Parameters
        ----------
        predicted_span:
            The expert's span for the word being retagged.
        target_attributes:
            Attribute names of the layer being retagged. Every one of them must
            be supplied by the expert's layer, otherwise the replacement would
            silently blank out attributes that the expert knows nothing about.

        Returns
        -------
        dict
            The annotation to write into the target layer.

        Raises
        ------
        ValueError
            If the target layer expects attributes the expert cannot provide.
            This happens when the retagger is pointed at a Vabamorf-based morph
            analysis layer, whose ``lemma``/``root``/``ending`` values cannot be
            derived from a (form, partofspeech) prediction. Such a layer can
            only be disambiguated, not overridden.
        """

        expert_attributes = set(predicted_span.layer.attributes)
        missing = [attr for attr in target_attributes if attr not in expert_attributes]
        if missing:
            raise ValueError(
                "(!) Cannot replace annotations in layer {!r}: the expert model does "
                "not provide the attribute(s) {!r}. Overriding is only possible when "
                "every attribute of the retagged layer comes from the model. Point "
                "the retagger at a BERT-based morph layer, or use it as a "
                "disambiguator only.".format(self.output_layer, missing)
            )

        expert_annotation = predicted_span.annotations[0]
        return {attr: expert_annotation.get(attr) for attr in target_attributes}

    def _build_predicted_span_map(
        self,
        text: Text,
        layers: MutableMapping[str, Layer],
        status: dict,
    ) -> dict[tuple[int, int], Layer]:
        """Build a lookup table from span boundaries to expert predictions.

        The BERT helper is only invoked for sentences that contain at least one
        homonymous word. Sentences without homonyms are skipped entirely.

        Both the sentences layer and the source layer are ordered by span start,
        so the source layer is walked with a single moving index rather than
        being rescanned in full for every sentence.
        """

        predicted_by_span: dict[tuple[int, int], Layer] = {}
        sentences_layer = layers[self.sentences_layer]
        source_layer = layers[self.output_layer]

        expert_input_layers = list(self._bert_morph_tagger.input_layers)
        span_count = len(source_layer)
        span_index = 0

        for sentence in sentences_layer:
            # Spans belonging to previous sentences are never revisited.
            while (
                span_index < span_count
                and source_layer[span_index].start < sentence.start
            ):
                span_index += 1

            # Only look at the spans that fall inside the current sentence.
            sentence_has_homonym = False
            scan_index = span_index
            while scan_index < span_count:
                span = source_layer[scan_index]
                if sentence.end <= span.start:
                    break
                if self._is_homonym_word(span.text):
                    sentence_has_homonym = True
                    break
                scan_index += 1

            if not sentence_has_homonym:
                continue

            # Reuse the existing tokenisation instead of retokenising the
            # sentence string: a fresh tokenisation is not guaranteed to match
            # the original one if estnltk's tokenisation rules have changed in
            # the meantime.
            sentence_text = extract_section(
                text=text,
                start=sentence.start,
                end=sentence.end,
                layers_to_keep=expert_input_layers,
            )
            expert_layer = self._bert_morph_tagger.make_layer(
                text=sentence_text,
                layers=sentence_text.layers,
                status=status,
            )

            for span in expert_layer:
                predicted_by_span[
                    (span.start + sentence.start, span.end + sentence.start)
                ] = span

        return predicted_by_span

    def _correct_layer(
        self,
        source_layer: Layer,
        predicted_by_span: dict[tuple[int, int], Layer],
    ) -> Layer:
        """Apply homonym corrections in place on the source layer."""

        agreed_words = 0
        corrected_words = 0
        inspected_words = 0
        target_attributes = list(source_layer.attributes)
        # Iterate over the source layer and check each span against the predicted spans
        for source_span in source_layer:
            # Check if the source span has a corresponding predicted span
            predicted_span = predicted_by_span.get((source_span.start, source_span.end))
            # If there is no predicted span or the source span is not a homonym, skip it
            if predicted_span is None or not self._is_homonym_word(source_span.text):
                continue
            # If the predicted span exists and the source span is a homonym, we need to check if the predicted label matches any of the existing annotations in the source span
            inspected_words += 1
            predicted_label = self._extract_predicted_label(predicted_span)
            # If the predicted label is None, we skip this span
            if predicted_label is None:
                continue
            # Check if the predicted label matches any of the existing annotations in the source span
            predicted_form, predicted_pos = predicted_label
            matching_annotations = [
                annotation
                for annotation in source_span.annotations
                if annotation.get("form") == predicted_form
                and annotation.get("partofspeech") == predicted_pos
            ]
            # If the expert confirms one of the existing analyses, we keep only
            # the matching ones. Otherwise the expert disagrees with everything
            # present, and its own prediction replaces the existing annotations:
            # every attribute of this layer is model output, so there is nothing
            # in the original analysis worth preserving.
            if matching_annotations:
                annotations_to_copy = [
                    dict(annotation) for annotation in matching_annotations
                ]
                agreed_words += 1
            else:
                annotations_to_copy = [
                    self._build_expert_annotation(predicted_span, target_attributes)
                ]
                corrected_words += 1
            # Clear the existing annotations in the source span and copy the selected annotations back into it
            source_span.clear_annotations()
            for annotation in annotations_to_copy:
                source_span.add_annotation(annotation)
        # Store some statistics about the retagging process in the source layer's metadata
        source_layer.meta["morph_homonyms_retagger"] = {
            "inspected_words": inspected_words,
            "agreed_words": agreed_words,
            "corrected_words": corrected_words,
            "homonym_list_size": len(self.homonym_words),
            "output_layer": self.output_layer,
        }
        return source_layer

    def _change_layer(
        self,
        text: Text,
        layers: MutableMapping[str, Layer],
        status: dict,
    ) -> None:
        """Retag the existing morphological layer in place."""

        assert self.output_layer in layers
        assert self.sentences_layer in layers
        assert self.words_layer in layers

        morph_layer = layers[self.output_layer]
        predicted_by_span = self._build_predicted_span_map(text, layers, status)
        self._correct_layer(
            source_layer=morph_layer,
            predicted_by_span=predicted_by_span,
        )
        layers[self.output_layer] = morph_layer
