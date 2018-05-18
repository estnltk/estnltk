#
#   ZeroCompoundTokenTagger creates an empty 'compound_tokens' 
#  layer. This can be useful when you need to restore original
#  tokenization of a pre-tokenized text, i.e. when you want to 
#  use exactly the same (whitespace) tokenization as in the 
#  original text without adding any new compound tokens.
# 

import regex as re
import os
from typing import Union

from estnltk import EnvelopingSpan
from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger


class ZeroCompoundTokensTagger(Tagger):
    """Tagger that creates an empty compound_tokens layer.
       This can be useful when you need to restore the original
       tokenization of a pre-tokenized text, i.e. when you want 
       to use exactly the same (whitespace) tokenization as in 
       the original text without adding any new compound tokens.
    """
    output_attributes = ('type', 'normalized')
    input_layers = ['tokens']
    depends_on   = input_layers
    output_layer = 'compound_tokens'
    layer_name   = output_layer


    def __init__(self):
        """Initializes ZeroCompoundTokenTagger. """
        pass


    def _make_layer(self, raw_text: str, layers, status: dict):
        """Creates an empty compound_tokens layer.
        """
        layer = Layer(name=self.output_layer,
                      enveloping='tokens',
                      attributes=self.output_attributes,
                      ambiguous=False)
        return layer

