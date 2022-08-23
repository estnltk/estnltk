from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk.web_taggers import BatchProcessingWebTagger

class StanzaSyntaxWebTagger( BatchProcessingWebTagger ):
    """Tags dependency syntactic analysis using EstNLTK StanzaSyntaxTagger's webservice.

    See also StanzaSyntaxTagger's documentation:
    https://github.com/estnltk/estnltk/blob/113cec7af026597d8e45ec9bf06e8492ab3d24e9/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb
    """

    def __init__(self, url, output_layer='stanza_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['words', 'sentences', 'morph_extended']
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 125
        self.batch_enveloping_layer = self.input_layers[1]


