from estnltk.taggers import Tagger
from estnltk.common import DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.standard.ner.model_storage_util import ModelStorageUtil
from estnltk.taggers.standard.ner.fex import FeatureExtractor
from estnltk.taggers.standard.ner import CrfsuiteModel
from estnltk import Layer, Text
from typing import MutableMapping


class WordLevelNerTagger(Tagger):
    """The class for tagging named entities."""
    conf_param = ['modelUtil', 'nersettings', 'fex', 'crf_model']
    input_layers = []

    def __init__(self, model_dir=DEFAULT_PY3_NER_MODEL_DIR, output_layer='wordner', morph_layer_input='morph_analysis', words_layer_input='words', sentences_layer_input='sentences'):
        """Initialize a new WordLevelNerTagger instance.

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
        modelUtil = ModelStorageUtil(model_dir)
        nersettings = modelUtil.load_settings()
        self.input_layers = (morph_layer_input, words_layer_input, sentences_layer_input)
        self.fex = FeatureExtractor(nersettings, self.input_layers)
        self.crf_model = CrfsuiteModel(settings=nersettings,
                                       model_filename=modelUtil.model_filename)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, attributes=self.output_attributes, 
                     text_object=None, parent=self.input_layers[1])

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        self.fex.process([text])
        snt_labels = self.crf_model.tag(text, self.input_layers)
        flattened = (word for snt in snt_labels for word in snt)

        words = self.input_layers[1]

        nerlayer = self._make_layer_template()
        nerlayer.text_object=text
        for span, label in zip(getattr(text, words), flattened):
            nerlayer.add_annotation(span, nertag=label)
        text.pop_layer("ner_features")
        return nerlayer