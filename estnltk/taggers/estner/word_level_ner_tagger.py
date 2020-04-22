from estnltk.taggers import Tagger
from estnltk.core import DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.estner.refac.ner import ModelStorageUtil
from estnltk.taggers.estner.fex import FeatureExtractor
from estnltk.taggers.estner import CrfsuiteTagger
from estnltk.layer.layer import Layer
from typing import MutableMapping
from estnltk.text import Text

class WordLevelNerTagger(Tagger):
    """The class for tagging named entities."""
    conf_param = ['modelUtil', 'nersettings', 'fex', 'crfsuite_tagger']
    input_layers = []

    def __init__(self, model_dir=DEFAULT_PY3_NER_MODEL_DIR, output_layer = 'wordner'):
        """Initialize a new NerTagger instance.

        Parameters
        ----------
        model_dir: st
            A directory containing a trained ner model and a settings file.
        """
        self.output_layer = output_layer
        self.output_attributes = ["nertag"]
        modelUtil = ModelStorageUtil(model_dir)
        nersettings = modelUtil.load_settings()
        self.fex = FeatureExtractor(nersettings)
        self.crfsuite_tagger = CrfsuiteTagger(settings=nersettings,
                                     model_filename=modelUtil.model_filename)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        self.fex.process([text])
        snt_labels = self.crfsuite_tagger.tag(text)
        flattened = (word for snt in snt_labels for word in snt)

        nerlayer = Layer(name=self.output_layer, attributes=self.output_attributes, text_object=text, enveloping="words")
        for span, label in zip(text.words, flattened):
            nerlayer.add_annotation(span, nertag=label)
        text.pop_layer("ner_features")
        return nerlayer