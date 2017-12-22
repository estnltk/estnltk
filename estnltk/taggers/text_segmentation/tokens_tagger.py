#
#  TokensTagger splits text into tokens, based on whitespace 
#  and/or punctuation. 
#  This is the most automic segmentation: in later analysis, 
#  tokens won't be broken into any smaller parts, but only 
#  joined if necessary.
# 

from typing import Union
import re

from estnltk.text import Layer
from estnltk.taggers import Tagger
from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()

#  Pattern describing tokens that should be 
#  retokenized and split into individual symbols
_punct_split_patterns    = re.compile('^[!"#$%&\'()*+,-./:;<=>?@^_`{|}~\[\]]{2,}$')
#  Pattern describing tokens that match punct_split_patterns,
#  but should not be split into individual symbols
_punct_no_split_patterns = re.compile('^(\.{2,}|[\?!]+)$')

class TokensTagger(Tagger):
    description   = 'Tags tokens in raw text.'
    layer_name    = 'tokens'
    attributes    = []
    depends_on    = []
    configuration = None
    
    def __init__(self, apply_punct_postfixes:bool=True):
        """Initializes TokensTagger.
        
        Parameters
        ----------
        apply_punct_postfixes: boolean (default: True)
            If True, post-fixes will be applied to WordPunctTokenizer's
            tokenization results: if a sequence of punctuation symbols 
            forms a single token, then the token will be split into 
            smaller tokens, so that there is one token for each 
            punctuation symbol.
        """
        self._apply_punct_postfixes = apply_punct_postfixes
        self.configuration = {'apply_punct_postfixes': self._apply_punct_postfixes}

    def tag(self, text:'Text', return_layer:bool=False) -> Union['Text', Layer]:
        """Segments given Text into tokens. 
        
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
        if self._apply_punct_postfixes:
            #  WordPunctTokenizer may leave tokenization of punctuation 
            #  incomplete, for instance:
            #      'e.m.a.,'  -->  'e', '.', 'm', '.', 'a', '.,'
            #      '1989.a.).' --> '1989', '.', 'a', '.).'
            #  We will gather these cases and split separately:
            spans_to_split = []
            for (start, end) in spans:
                token = text.text[start:end]
                if _punct_split_patterns.match( token ) and \
                   not _punct_no_split_patterns.match( token ):
                    spans_to_split.append( (start, end) )
            if spans_to_split:
                spans = self._split_into_symbols( spans, spans_to_split )
        tokens = Layer(name=self.layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        if return_layer:
            return tokens
        text[self.layer_name] = tokens
        return text

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

