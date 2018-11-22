#
#  TokensTagger splits text into tokens, based on whitespace
#  and/or punctuation. 
#  This is the most automic segmentation: in later analysis, 
#  tokens won't be broken into any smaller parts, but only 
#  joined if necessary.
# 

from typing import MutableMapping, Sequence
import re

from estnltk.text import Layer
from estnltk.taggers import Tagger
from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()

class TokensTagger(Tagger):
    """Tags tokens in raw text."""
    output_layer = 'tokens'
    attributes   = ()
    conf_param   = ['depends_on', 'layer_name',  # <- For backward compatibility ...
                    'apply_punct_postfixes',
                    '_punct_split_patterns',
                    '_punct_no_split_patterns' ]
    
    def __init__(self, 
                 output_layer:str='tokens',
                 apply_punct_postfixes:bool=True):
        """Initializes TokensTagger.
        
        Parameters
        ----------
        output_layer: str (default: 'tokens')
            Name of the layer where tokenization results will
            be stored;
        apply_punct_postfixes: boolean (default: True)
            If True, post-fixes will be applied to WordPunctTokenizer's
            tokenization results: if a sequence of punctuation symbols 
            forms a single token, then the token will be split into 
            smaller tokens, so that there is one token for each 
            punctuation symbol.
        """
        self.output_layer = output_layer
        self.input_layers = []
        self.layer_name   = self.output_layer  # <- For backward compatibility
        self.depends_on   = []                 # <- For backward compatibility

        self.apply_punct_postfixes = apply_punct_postfixes
        #  Pattern describing tokens that should be 
        #  retokenized and split into individual symbols
        self._punct_split_patterns    = re.compile('^[!"#$%&\'()*+,-./:;<=>?@^_`{|}~\[\]]{2,}$')
        #  Pattern describing tokens that match punct_split_patterns,
        #  but should not be split into individual symbols
        self._punct_no_split_patterns = re.compile('^(\.{2,}|[\?!]+)$')


    def _make_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        """Segments given Text into tokens. 
           Returns tokens layer.
        
           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which will be 
              tokenized;
              
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.
              
           status: dict
              This can be used to store metadata on layer tagging.
        """
        spans = list(tokenizer.span_tokenize(raw_text))
        if self.apply_punct_postfixes:
            #  WordPunctTokenizer may leave tokenization of punctuation 
            #  incomplete, for instance:
            #      'e.m.a.,'  -->  'e', '.', 'm', '.', 'a', '.,'
            #      '1989.a.).' --> '1989', '.', 'a', '.).'
            #  We will gather these cases and split separately:
            spans_to_split = []
            for (start, end) in spans:
                token = raw_text[start:end]
                if self._punct_split_patterns.match( token ) and \
                   not self._punct_no_split_patterns.match( token ):
                    spans_to_split.append( (start, end) )
            if spans_to_split:
                spans = self._split_into_symbols( spans, spans_to_split )
        return Layer(name=self.output_layer).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)


    def _split_into_symbols( self, spans, spans_to_split ):
        '''Splits a subset of spans from the list spans into 
           single symbol spans. For instance, if 
             spans = ['(', 'a', '.).']
             spans_to_split = [ (2,5) ]
           then we get:
             ['(', 'a', '.', ')', '.']
           '''
        new_spans = []
        for start, end in spans:
            if spans_to_split and (start, end) in spans_to_split:
                for i in range(start, end):
                    new_spans.append( (i, i+1) )
            else:
                new_spans.append( (start, end) )
        return new_spans

