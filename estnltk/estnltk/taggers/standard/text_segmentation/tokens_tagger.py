#
#  TokensTagger splits text into tokens, based on whitespace
#  and/or punctuation. 
#  This is the most automic segmentation: in later analysis, 
#  tokens won't be broken into any smaller parts, but only 
#  joined if necessary.
# 

from typing import MutableMapping
import re

from estnltk import Layer
from estnltk.taggers import Tagger
from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()


class TokensTagger(Tagger):
    """Tags tokens in raw text."""
    output_layer      = 'tokens'
    output_attributes = ()
    conf_param   = ['apply_punct_postfixes',
                    '_punct_split_patterns',
                    '_punct_no_split_patterns']
    
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

        self.apply_punct_postfixes = apply_punct_postfixes
        #  Pattern describing tokens that should be 
        #  retokenized and split into individual symbols
        self._punct_split_patterns    = re.compile(r'^[!"#$%&\'()*+,-./:;<=>?@^_`{|}~\[\]«»”“]{2,}$')
        #  Pattern describing tokens that match punct_split_patterns,
        #  but should not be split into individual symbols
        self._punct_no_split_patterns = re.compile(r'^(\.{2,}|[\?!]+)$')
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
        spans = list(tokenizer.span_tokenize(text.text))
        if self.apply_punct_postfixes:
            #  WordPunctTokenizer may leave tokenization of punctuation 
            #  incomplete, for instance:
            #      'e.m.a.,'  -->  'e', '.', 'm', '.', 'a', '.,'
            #      '1989.a.).' --> '1989', '.', 'a', '.).'
            #  We will gather these cases and split separately:
            spans_to_split = []
            for (start, end) in spans:
                token = text.text[start:end]
                if self._punct_split_patterns.match( token ) and \
                   not self._punct_no_split_patterns.match( token ):
                    spans_to_split.append( (start, end) )
            if spans_to_split:
                spans = self._split_into_symbols( spans, spans_to_split )
        layer = self._make_layer_template()
        for start, end in spans:
            layer.add_annotation( (start, end) )
        layer.text_object = text
        return layer

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

