from estnltk.taggers.legacy_tokenizers import EstWordTokenizer
from estnltk.text import Text, Layer


class WordTokenizer:
    Tokenizer = EstWordTokenizer()

    def tag(self, text: Text) -> Text:
        spans = self.Tokenizer.span_tokenize(text.text)
        words = Layer(name='words').from_records([{
                                                      'start': start,
                                                      'end': end
                                                  } for start, end in spans], rewriting=True)
        text['words'] = words

        return text
