from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import WebTagger

from estnltk.taggers.web_taggers.v01.web_tagger import WebTaggerRequestTooLargeError

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
        # Check the Text object size
        # Currently, the size limit is set to 125 words
        number_of_words = len([w for sentence in layers['sentences'] for w in sentence])
        if number_of_words > 125:
            raise WebTaggerRequestTooLargeError('(!) The request Text object exceeds the web service '+\
            'limit 125 words per text. Please use EstNLTK\'s methods extract_sections or split_by to split '+\
            'the Text object into smaller Texts, and proceed by processing smaller Texts with the web service. '+\
            'More information about Text splitting: '+
            'https://github.com/estnltk/estnltk/blob/version_1.6/tutorials/system/layer_operations.ipynb ')
        return super()._make_layer(text, layers, status)

