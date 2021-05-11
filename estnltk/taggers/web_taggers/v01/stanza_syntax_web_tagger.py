from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import WebTagger

class StanzaSyntaxWebTagger(WebTagger):
    """Tags dependency syntactic analysis using EstNLTK StanzaSyntaxTagger's webservice.

    See also StanzaSyntaxTagger's documentation:
    https://nbviewer.jupyter.org/github/estnltk/estnltk/blob/devel_1.6/tutorials/syntax/syntax.ipynb
    """

    def __init__(self, url, output_layer='stanza_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['sentences', 'morph_extended', 'words']

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        return super()._make_layer(text, layers, status)

