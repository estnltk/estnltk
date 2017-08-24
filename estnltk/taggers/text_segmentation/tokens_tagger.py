from estnltk.text import Layer
from estnltk.taggers import Tagger

from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()

class TokensTagger(Tagger):
    description = 'Tags tokens in raw text.'
    layer_name = 'tokens'
    attributes = []
    depends_on = []
    configuration = {}

    def tag(self, text: 'Text') -> 'Text':        
        spans = list(tokenizer.span_tokenize(text.text))
        tokens = Layer(name=self.layer_name).from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        text[self.layer_name] = tokens
        return text
