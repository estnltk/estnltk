from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import BatchProcessingWebTagger

class BertEmbeddingsWebTagger( BatchProcessingWebTagger ):
    """Tags BERT embeddings using EstNLTK web service.

    See also BertTagger documentation.
    """

    def __init__(self, url, output_layer='bert_embeddings'):
        self.url = url
        self.input_layers = ('words', 'sentences',)
        self.output_attributes = ['token', 'bert_embedding']
        self.output_layer = output_layer
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 125
        self.batch_enveloping_layer = self.input_layers[1]


