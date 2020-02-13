from estnltk.taggers import Tagger
from estnltk.core import DEFAULT_PY2_NER_MODEL_DIR, DEFAULT_PY3_NER_MODEL_DIR
import six
from estnltk.taggers.estner.refac.ner import ModelStorageUtil
from estnltk.taggers.estner.fex import FeatureExtractor
from estnltk.taggers.estner import CrfsuiteTagger
from estnltk import Layer
from estnltk import EnvelopingBaseSpan
from typing import MutableMapping
from estnltk.text import Text

class NerTagger(Tagger):
    """The class for tagging named entities."""
    conf_param = ['modelUtil', 'nersettings', 'fex', 'tagger']
    input_layers = []

    DEFAULT_NER_MODEL_DIR = DEFAULT_PY3_NER_MODEL_DIR if six.PY3 else DEFAULT_PY2_NER_MODEL_DIR

    def __init__(self, model_dir=DEFAULT_NER_MODEL_DIR, output_layer = 'wordner', output_attributes = ("nertag",)):
        """Initialize a new NerTagger instance.

        Parameters
        ----------
        model_dir: st
            A directory containing a trained ner model and a settings file.
        """
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        modelUtil = ModelStorageUtil(model_dir)
        nersettings = modelUtil.load_settings()
        self.fex = FeatureExtractor(nersettings)
        self.tagger = CrfsuiteTagger(settings=nersettings,
                                     model_filename=modelUtil.model_filename)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        # prepare input for nertagger
        #nerdoc = json_document_to_estner_document(text)
        self.fex.process([text])
        snt_labels = self.tagger.tag(text)

        nerlayer = Layer(name="wordner", attributes=self.output_attributes, text_object=text, enveloping="words")
        for span, label in zip(text.words, snt_labels):
            nerlayer.add_annotation(span, nertag=label[0])
        return nerlayer