# -*- coding: utf-8 -*-
'''Module containing functionality for adding morphological analysis
information to corpora.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths, overrides
from estnltk.names import *
from estnltk.textprocessor import TextProcessor
from estnltk.corpus import List

import pyvabamorf

from pprint import pprint


def analyze(text, guess=True, phonetic=False, compound=True):
    '''Perform morphological analysis on input.
    
    Parameters
    ----------
    words: list of str or str
        Either a list of pretokenized words or a string. In case of a string, it will be splitted using
        default behaviour of string.split() function.
    guess: boolean, optional
        If True, then use guessing, when analyzing unknown words (default: True)
    phonetic: boolean, optional
        If True, add phonetic information to the root forms (default: False).
    compound: boolean, optional
        if True, add compound word markers to root forms (default: True)

    Returns
    -------
    list of (list of dict)
        List of analysis for each word in input. One word usually contains more than one analysis as the
        analyser does not perform disambiguation. 
    '''
    return pyvabamorf.analyze(text, guess=guess, phonetic=phonetic, compound=compound)


def synthesize(lemma, guess=True, phonetic=False, **kwargs):
    '''Given lemma, pos tag and a form, synthesize the word.

    Parameters
    ----------
    lemma: str
        The lemma of the word to be synthesized.
    partofspeech: str, optional
        The POS tag of the word to be synthesized.
    form: str, optional
        The form of the word to be synthesized.
    hint: str, optional
        The hint used by vabamorf to synthesize the word.
    guess: bool, optional
        If True, use guessing for unknown words (default: True)
    phonetic: bool, optional
        If True, add phonetic markers to synthesized words (default: True).

    Returns
    -------
    list of str
        The list of synthesized words.
    '''
    return pyvabamorf.synthesize(lemma, guess=guess, phonetic=phonetic, **kwargs)


class PyVabamorfAnalyzer(TextProcessor):
    '''Class using vabamorf library for morphological analysis.'''
    
    @overrides(TextProcessor)
    def process_json(self, corpus, **kwargs):
        for words in JsonPaths.words.find(corpus):
            words.value = self.analyze(words.value, **kwargs)
        return corpus
    
    @overrides(TextProcessor)    
    def process_corpus(self, corpus, **kwargs):
        for sentence in corpus.sentences:
            sentence[WORDS] = List(self.analyze(sentence.words, **kwargs))
        return corpus
    
    def analyze(self, wordlist, **kwargs):
        for word in wordlist:
            word[ANALYSIS] = analyze(word[TEXT], **kwargs)[0][ANALYSIS]
        return wordlist
