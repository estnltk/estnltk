from typing import List, Iterator

import nltk as nltk

from estnltk.text import Layer


class SentenceTokenizer:

    def __init__(self):
        pass

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

    def _tokenize(self, words: List[str]) -> Iterator[List[str]]:
        # Apply sentences_from_tokens method (if available)
        sentences = self.sentence_tokenizer.sentences_from_tokens(words)
        return sentences

    def tag(self, text: 'Text', fix=True) -> 'Text':
        sentences = Layer(enveloping='words',
                          name='sentences')

        text._add_layer(sentences)

        sentence_borders = [0]
        words = text.words.text
        for sentence in self._tokenize(words):
            sentence_borders.append(sentence_borders[-1]+len(sentence))
        if fix:
            new_sentence_borders = []
            for i in sentence_borders:
                if i < 2:
                    new_sentence_borders.append(i)
                    continue
                if words[i-2].lower() in {'a', 'dr', 'hr', 'hrl', 'ibid', 'jr',
                                          'kod', 'koost', 'lp', 'lüh', 'mr', 'mrs',
                                          'nn', 'nt', 'pr', 's.o', 's.t', 'saj',
                                          'sealh', 'sh', 'sm', 'so', 'st', 'tlk',
                                          'tn', 'toim', 'vrd'}:
                    continue
                new_sentence_borders.append(i)
            sentence_borders = new_sentence_borders
        for s, e in zip(sentence_borders, sentence_borders[1:]):            
            sentences._add_spans_to_enveloping(text.words[s:e])

        return text
