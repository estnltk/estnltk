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

from estnltk.text import Layer
from estnltk.taggers import Tagger
from nltk.tokenize.regexp import WhitespaceTokenizer

tokenizer = WhitespaceTokenizer()


class WhiteSpaceTokensTagger(Tagger):
    """Splits text into tokens by whitespaces. 
       Use this tagger only if you have a text that has been already 
       correctly tokenized by whitespaces, and you do not need to apply 
       any extra tokenization rules. """
    attributes   = ()
    conf_param   = ['depends_on', 'layer_name',  # <- For backward compatibility ...
                   ]

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
        self.layer_name   = self.output_layer  # <- For backward compatibility
        self.depends_on   = []                 # <- For backward compatibility
        self.output_attributes = ()

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
        return Layer(name=self.output_layer, text_object=text).from_records(
                                                [{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
