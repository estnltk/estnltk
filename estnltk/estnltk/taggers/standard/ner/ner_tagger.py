from estnltk import Text, Layer, EnvelopingBaseSpan
from estnltk.taggers import Tagger
from estnltk.common import DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.standard.ner.model_storage_util import ModelStorageUtil
from estnltk.taggers.standard.ner.fex import FeatureExtractor
from estnltk.taggers.standard.ner import CrfsuiteModel
from typing import MutableMapping



class NerTagger(Tagger):
    """The class for tagging named entities."""
    conf_param = ['modelUtil', 'nersettings', 'fex', 'crf_model']

    def __init__(self, model_dir=DEFAULT_PY3_NER_MODEL_DIR, output_layer='ner', morph_layer_input='morph_analysis', words_layer_input='words', sentences_layer_input='sentences'):
        """Initialize a new NerTagger instance.

        Parameters
        ----------
        model_dir: st
            A directory containing a trained ner model and a settings file.
        output_layer: str
            Name of the layer that will be added to the text object
        morph_layer_input: tuple
            Names of the morphological analysis layers used in feature extraction

        """
        self.output_layer = output_layer
        self.output_attributes = ["nertag"]
        self.modelUtil = ModelStorageUtil(model_dir)
        self.nersettings = self.modelUtil.load_settings()
        self.input_layers = (morph_layer_input, words_layer_input, sentences_layer_input)
        self.fex = FeatureExtractor(self.nersettings, self.input_layers)
        self.crf_model = CrfsuiteModel(settings=self.nersettings,
                                       model_filename=self.modelUtil.model_filename)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, attributes=self.output_attributes, text_object=None,
                     enveloping=self.input_layers[1])

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        # prepare input for nertagger
        self.fex.process([text])
        snt_labels = self.crf_model.tag(text, self.input_layers)
        flattened = (word for snt in snt_labels for word in snt)

        words = self.input_layers[1]

        # add the labels
        nerlayer = self._make_layer_template()
        nerlayer.text_object=text
        entity_spans = []
        entity_type = None

        for span, label in zip(getattr(text, words), flattened):
            if entity_type is None:
                entity_type = label[2:]
            if label == "O":
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                            **{self.output_attributes[0]: entity_type})
                    entity_spans = []
                continue
            if label[0] == "B" or entity_type != label[2:]:
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                            **{self.output_attributes[0]: entity_type})
                    entity_spans = []
            entity_type = label[2:]
            entity_spans.append(span.base_span)
        text.pop_layer("ner_features")
        return nerlayer
