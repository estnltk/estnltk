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

    def tag(self, text: 'Text') -> 'Text':
        sentences = Layer(enveloping='words',
                          name='sentences')

        text._add_layer(sentences)

        # TODO fix dumb manual loop
        i = 0
        new_sentences = []
        for sentence in self._tokenize(text.words.text):
            sent = []
            for _ in sentence:
                sent.append(text.words[i])
                i += 1
            new_sentences.append(sent)

        for sentence in new_sentences:
            sentences._add_spans_to_enveloping(sentence)

        return text
