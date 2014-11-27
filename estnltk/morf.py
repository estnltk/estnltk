# -*- coding: utf-8 -*-
'''Module containing functionality for adding morphological analysis
information to corpora.

Attributes
----------

analyer: PyVabamorfAnalyzer
    Analyzer with default parameters.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths, overrides
from estnltk.names import *
from estnltk.textprocessor import TextProcessor
from estnltk.corpus import List

from pyvabamorf import analyze
from itertools import izip
from pprint import pprint


class PyVabamorfAnalyzer(TextProcessor):
    
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
        '''
        Keyword parameters
        ------------------
        phonetic: boolean
            If true, add phonetic markup to root elements (default: False)
        compound: boolean
            If true, add compound word markup to root elements (default: True)
            
        '''
        for word in wordlist:
            word[ANALYSIS] = analyze(word.text, **kwargs)[0][ANALYSIS]
        return wordlist
