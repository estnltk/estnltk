from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import BatchProcessingWebTagger

class StanzaSyntaxWebTagger( BatchProcessingWebTagger ):
    """Tags dependency syntactic analysis using EstNLTK StanzaSyntaxTagger's webservice.

    See also StanzaSyntaxTagger's documentation:
    https://nbviewer.jupyter.org/github/estnltk/estnltk/blob/devel_1.6/tutorials/syntax/syntax.ipynb
    """

    def __init__(self, url, output_layer='stanza_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['words', 'sentences', 'morph_extended']
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 125
        self.batch_enveloping_layer = self.input_layers[1]


