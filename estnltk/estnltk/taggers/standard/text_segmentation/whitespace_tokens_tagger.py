#
#  WhiteSpaceTokensTagger splits text into tokens based on 
#  whitespaces (and whitespaces only).
#  Use this tagger if you have a text that has been already 
#  correctly split into tokens by whitespaces, and you do 
#  not need to apply any extra tokenization rules.
#  ( e.g. if you need to load/restore original tokenization 
#         of some pretokenized corpus )
#

from typing import MutableMapping

from estnltk import Layer
from estnltk.taggers import Tagger
from nltk.tokenize.regexp import WhitespaceTokenizer

tokenizer = WhitespaceTokenizer()


class WhiteSpaceTokensTagger(Tagger):
    """Splits text into tokens by whitespaces. 
       Use this tagger only if you have a text that has been already 
       correctly tokenized by whitespaces, and you do not need to apply 
       any extra tokenization rules. """
    output_attributes = ()
    conf_param        = ()

    def __init__(self, output_layer: str = 'tokens'):
        """
        Initializes WhiteSpaceTokensTagger.
        
        Parameters
        ----------
        output_layer: str (default: 'tokens')
            Name of the layer where tokenization results will
            be stored;
        """
        self.output_layer = output_layer
        self.input_layers = []
        self.output_attributes = ()

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, text_object=None)

    def _make_layer(self, text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        """Segments given Text into tokens. 
           Returns tokens layer.
        
           Parameters
           ----------
           text: str
              Text object which will be tokenized;
              
           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the name 
              of the layer to the Layer object.
              
           status: dict
              This can be used to store metadata on layer tagging.
        """
        assert text.text is not None, '(!) {} has no textual content to be analysed.'.format(text)
        raw_text = text.text
        spans = list(tokenizer.span_tokenize(raw_text))
        layer = self._make_layer_template()
        for start, end in spans:
            layer.add_annotation( (start, end) )
        layer.text_object = text
        return layer
