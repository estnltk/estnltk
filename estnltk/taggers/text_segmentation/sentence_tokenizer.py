from typing import Iterator, Tuple

import nltk as nltk

from estnltk.text import Layer


class SentenceTokenizer:
    def __init__(self):
        self._layer_name = 'sentences'
        self._attributes = []
        self._depends_on = ['compound_tokens', 'words']

    # use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
    sentence_tokenizer = None

    try:
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
    except LookupError:
        import nltk.downloader
        nltk.downloader.download('punkt')
    finally:
        if sentence_tokenizer is None:
            sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')

    def _tokenize(self, text: 'Text') -> Iterator[Tuple[int, int]]:
        return self.sentence_tokenizer.span_tokenize(text.text)

    def tag(self, text: 'Text', fix=True) -> 'Text':
        layer = Layer(enveloping='words',
                      name=self._layer_name,
                      ambiguous=False)

        sentence_ends = {end for _, end in self._tokenize(text)}
        if fix:
            for ct in text.compound_tokens:
                if ct.type == 'non_ending_abbreviation':
                    sentence_ends -= {span.end for span in ct}
                else:
                    sentence_ends -= {span.end for span in ct[0:-1]}
        start = 0
        sentence_ends.add(text.words[-1].end)
        for i, token in enumerate(text.words):
            if token.end in sentence_ends:
                layer.add_span(text.words[start:i+1])
                start = i + 1

        text[self._layer_name] = layer
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