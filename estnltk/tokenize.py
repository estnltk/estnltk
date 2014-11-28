# -*- coding: utf-8 -*-
'''Module containing functionality to perform basic tokenization
of plaintext data.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import as_unicode
from estnltk.names import *
from estnltk.corpus import Corpus

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer
import nltk.data


class Tokenizer(object):
    '''Class for performing basic tokenization on plain text.'''
    
    def __init__(self, **kwargs):
        '''Initialize the tokenizer.
        
        Keyword parameters
        ------------------
        
        paragraph_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Default paragraph tokenizer uses newlines to separate paragraphs.
        sentence_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Default sentence tokenizer is NLTK default PunktSentenceTokenizer for Estonian.
        word_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Default is NLTK PunktWordTokenizer.
        '''
        self._paragraph_tokenizer = kwargs.get('paragraph_tokenizer',
            RegexpTokenizer('\s*\n\n\s*', gaps=True, discard_empty=True))
        self._sentence_tokenizer = kwargs.get('sentence_tokenizer',
            nltk.data.load('tokenizers/punkt/estonian.pickle'))
        self._word_tokenizer = kwargs.get('word_tokenizer',
            PunktWordTokenizer())

    def tokenize(self, text):
        '''Tokenize the text into paragraphs, sentences and words.
        
        Parameters
        ----------
        text: str
            The text to be tokenized.
            
        Returns
        -------
        dict
            Dictionary of tokenized paragraphs, sentences and words
            with following structure:
            {
                text, start, end, rel_start, rel_end
                paragraphs:
                [
                    {
                        text, start, end, rel_start, rel_end
                        sentences:
                        [
                            {
                                text, start, end, rel_start, rel_end
                                words:
                                [
                                    {
                                        text, start, end, rel_start, rel_end
                                    },
                                    ...
                                ]
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        '''
        text = as_unicode(text)
        paras = tokenize(text, self._paragraph_tokenizer)
        for para in paras:
            sentences = tokenize(para[TEXT], self._sentence_tokenizer, para[START])
            for sent in sentences:
                sent[WORDS] = tokenize(sent[TEXT], self._word_tokenizer, sent[START])
            para[SENTENCES] = sentences
        document = {TEXT: text,
                    PARAGRAPHS: paras,
                    START: 0,
                    REL_START: 0,
                    END: len(text),
                    REL_END: len(text)}
        return Corpus.construct(document)

    def __call__(self, text):
        '''Tokenize the text into paragraphs, sentences and words.'''
        return self.tokenize(text)


def tokenize(text, tokenizer, start=0):
    '''Function that tokenizes given text with given tokenizer
    and returns JSON-style output.
    
    Parameters
    ----------
    
    text: str
        The text to be tokenized.
    tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
        The tokenizer to use.
    start: int
        the absolute start position of the given text. Only required when this text is a substring
        of a larger text. Such as a sentence in a paragraph.
        
    Returns
    -------
    list of dict
        List of tokens, described by "text", "start", "end", "rel_start", "rel_end" elements.
    '''
    end = start + len(text)
    toks = tokenizer.tokenize(text)
    spans = tokenizer.span_tokenize(text)
    results = []
    for tok, (tokstart, tokend) in zip(toks, spans):
        d = {TEXT: tok,
             START: start + tokstart,
             END: start + tokend,
             REL_START: tokstart,
             REL_END: tokend}
        assert text[d[REL_START]:d[REL_END]] == d[TEXT]
        results.append(d)
    return results
