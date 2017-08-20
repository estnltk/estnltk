from estnltk.text import Layer

from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()

class TokensTagger:
    
    def __init__(self):
        self._layer_name = 'tokens'
        self._attributes = []
        self._depends_on = []

    def tag(self, text: 'Text') -> 'Text':        
        spans = list(tokenizer.span_tokenize(text.text))
        tokens = Layer(name=self._layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        text[self._layer_name] = tokens
        return text

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':''}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)
