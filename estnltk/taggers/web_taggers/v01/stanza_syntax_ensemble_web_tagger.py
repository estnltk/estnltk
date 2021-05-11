from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import WebTagger

class StanzaSyntaxEnsembleWebTagger(WebTagger):
    """Tags dependency syntactic analysis using EstNLTK StanzaSyntaxEnsembleTagger's webservice.

    See also StanzaSyntaxEnsembleTagger's documentation:
    https://nbviewer.jupyter.org/github/estnltk/estnltk/blob/devel_1.6/tutorials/syntax/syntax.ipynb
    ( TODO: update the documentation )
    """

    def __init__(self, url, output_layer='stanza_ensemble_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['sentences', 'morph_extended', 'words']

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        return super()._make_layer(text, layers, status)

