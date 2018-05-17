#
#  WhiteSpaceTokensTagger splits text into tokens based on 
#  whitespaces (and whitespaces only).
#  Use this tagger if you have a text that has been already 
#  correctly split into tokens by whitespaces, and you do 
#  not need to apply any extra tokenization rules.
#  ( e.g. if you need to load/restore original tokenization 
#         of some pretokenized corpus )
#

from typing import Union
import re

from estnltk.text import Layer
from estnltk.taggers import TaggerOld
from nltk.tokenize.regexp import WhitespaceTokenizer

tokenizer = WhitespaceTokenizer()

class WhiteSpaceTokensTagger(TaggerOld):
    description   = 'Splits text into tokens by whitespaces (and whitespaces only).'+\
                    'Use this tagger only if you have a text that has been already '+\
                    'correctly tokenized by whitespaces, and you do not need to apply '+\
                    'any extra tokenization rules. '
    layer_name    = 'tokens'
    attributes    = ()
    depends_on    = []
    configuration = None
    
    def __init__(self):
        """Initializes WhiteSpaceTokensTagger.
        """
        self.configuration = {}

    def tag(self, text:'Text', return_layer:bool=False) -> Union['Text', Layer]:
        """Segments given Text into tokens by whitespaces. 
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be tokenized;

        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and 
            the Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
        spans = list(tokenizer.span_tokenize(text.text))
        tokens = Layer(name=self.layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        if return_layer:
            return tokens
        text[self.layer_name] = tokens
        return text
