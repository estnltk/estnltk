from estnltk.text import Layer

from nltk.tokenize.regexp import WordPunctTokenizer

import re

tokenizer = WordPunctTokenizer()

#  Patterns describing tokenization cases,
#  where punctuation needs further retokenization
punct_split_patterns = re.compile('^(\.,|\.\)\.)$')

class TokensTagger:
    
    def __init__(self):
        self._layer_name = 'tokens'
        self._attributes = []
        self._depends_on = []
        self._apply_punct_postfixes = True

    def tag(self, text: 'Text') -> 'Text':
        spans = list(tokenizer.span_tokenize(text.text))
        if self._apply_punct_postfixes:
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
        tokens = Layer(name=self._layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        text[self._layer_name] = tokens
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

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'apply_punct_postfixes': self._apply_punct_postfixes,
                  'conf':''}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'apply_punct_postfixes', 'conf'])
        return df.to_html(index=False)
