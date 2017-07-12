from estnltk.text import Layer

from nltk.tokenize.regexp import WordPunctTokenizer

tokenizer = WordPunctTokenizer()

class TokensTagger:

    def tag(self, text: 'Text') -> 'Text':        
        spans = list(tokenizer.span_tokenize(text.text))
        words = Layer(name='tokens').from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans],
                                                 rewriting=True)
        text['tokens'] = words
        return text
