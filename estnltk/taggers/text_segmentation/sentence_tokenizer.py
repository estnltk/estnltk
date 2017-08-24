from typing import Iterator, Tuple

import nltk as nltk

from estnltk.text import Layer
from estnltk.taggers import Tagger

class SentenceTokenizer(Tagger):
    description = 'Tags adjacent words that form a sentence.'
    layer_name = 'sentences'
    attributes = []
    depends_on = ['compound_tokens', 'words']
    configuration = {}

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
                      name=self.layer_name,
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

        text[self.layer_name] = layer
        return text
