from estnltk.text import Layer
from estnltk.taggers import Tagger

from nltk.tokenize.regexp import WordPunctTokenizer

import re

tokenizer = WordPunctTokenizer()

#  Patterns describing tokenization cases,
#  where punctuation needs further retokenization
punct_split_patterns = re.compile('^(\.,|\.\)\.)$')

class TokensTagger(Tagger):
    description   = 'Tags tokens in raw text.'
    layer_name    = 'tokens'
    attributes    = []
    depends_on    = []
    configuration = {}
    apply_punct_postfixes = True

    def tag(self, text: 'Text') -> 'Text':
        spans = list(tokenizer.span_tokenize(text.text))
        if self.apply_punct_postfixes:
            #  WordPunctTokenizer may leave tokenization of punctuation 
            #  incomplete, for instance:
            #      'e.m.a,'  -->  'e', '.', 'm', '.', 'a', '.,'
            #      '1989.a.).' --> '1989', '.', 'a', '.).'
            #  We will gather these cases and split separately:
            spans_to_split = []
            for (start, end) in spans:
                token = text.text[start:end]
                if punct_split_patterns.match( token ):
                    spans_to_split.append( (start, end) )
            if spans_to_split:
                spans = self._split_into_symbols( spans, spans_to_split )
        tokens = Layer(name=self.layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        text[self.layer_name] = tokens
        return text

    def _split_into_symbols( self, spans, spans_to_split ):
        new_spans = []
        for start, end in spans:
            if spans_to_split and (start, end) in spans_to_split:
                for i in range(start, end):
                    new_spans.append( (i, i+1) )
            else:
                new_spans.append( (start, end) )
        return new_spans

