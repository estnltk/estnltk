from estnltk.taggers import Tagger
from estnltk.core import DEFAULT_PY2_NER_MODEL_DIR, DEFAULT_PY3_NER_MODEL_DIR
import six
from estnltk.taggers.estner.refac.ner import ModelStorageUtil
from estnltk.taggers.estner.fex import FeatureExtractor
from estnltk.taggers.estner import CrfsuiteTagger
from estnltk.layer.layer import Layer
from estnltk import EnvelopingBaseSpan
from typing import MutableMapping
from estnltk.text import Text
import time

class NerTagger(Tagger):
    """The class for tagging named entities."""
    conf_param = ['modelUtil', 'nersettings', 'fex', 'tagger']
    input_layers = []

    DEFAULT_NER_MODEL_DIR = DEFAULT_PY3_NER_MODEL_DIR if six.PY3 else DEFAULT_PY2_NER_MODEL_DIR

    def __init__(self, model_dir=DEFAULT_NER_MODEL_DIR, output_layer = 'ner', output_attributes = ("nertag", "name")):
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
        begin = time.time()
        self.fex.process([text])
        snt_labels = self.tagger.tag(text)
        flat_labels = []
        for sublist in snt_labels:
            for item in sublist:
                flat_labels.append(item)
        print("CRF lopp")
        print(time.time()-begin)

        # add the labels
        nerlayer = Layer(name=self.output_layer, attributes=self.output_attributes, text_object=text, enveloping="words")
        entity_spans = []
        entity_type = None
        for span, label in zip(text.words, flat_labels):
            if entity_type is None:
                entity_type = label[2:]
            #TODO: pane kaks if-i kokku
            if label == "O":
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans), nertag=entity_type, name="po")
                    entity_spans = []
                continue
            if label[0] == "B" or entity_type != label[2:]:
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans), nertag=entity_type, name="po")
                    entity_spans = []
            entity_type = label[2:]
            entity_spans.append(span.base_span)
        print("kogu lopp")
        print(time.time()-begin)
        return nerlayer