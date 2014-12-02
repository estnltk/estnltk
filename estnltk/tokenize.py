# -*- coding: utf-8 -*-
'''Whenever you need to work with new plaintext data, you typically first need
to separate it into sentences/words or any other meaningful structure
for the task at hand.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import as_unicode
from estnltk.names import *
from estnltk.corpus import Corpus

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer
import nltk.data


class Tokenizer(object):
    '''Class for performing tokenization of plain text.
    
    First, it creates paragraph, then tokenizes each paragraph to sentences
    and then tokenizes the words of each sentence.
    How the tokenization will happen, can be specified by the user
    by supplying :class:`ntlk.tokenize.api.StringTokenizer` instance
    for a particular tokenizer.
    
    Parameters
    ----------
    
    paragraph_tokenizer : :class:`ntlk.tokenize.api.StringTokenizer`, optional
        Default paragraph tokenizer uses newlines to separate paragraphs.
    sentence_tokenizer : :class:`ntlk.tokenize.api.StringTokenizer`, optional
        Default sentence tokenizer is NLTK default PunktSentenceTokenizer for Estonian.
    word_tokenizer : :class:`ntlk.tokenize.api.StringTokenizer`, optional
        Default is NLTK PunktWordTokenizer.
    '''
        
    
    def __init__(self, **kwargs):
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
        text : str
            The text to be tokenized.
            
        Returns
        -------
        :class:`estnltk.corpus.Document`
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
        '''Shorthand function for :method:`estnltk.tokenize.Tokenizer.tokenize` '''
        return self.tokenize(text)


def tokenize(text, tokenizer, start=0):
    '''Function that tokenizes given text with given tokenizer
    and returns JSON-style output.
    
    Parameters
    ----------
    
    text: str
        The text to be tokenized.
    tokenizer: :class:`ntlk.tokenize.api.StringTokenizer`
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
