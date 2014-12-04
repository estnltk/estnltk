# -*- coding: utf-8 -*-
'''Module containing functionality for adding morphological analysis
information to corpora.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths, overrides
from estnltk.names import *
from estnltk.textprocessor import TextProcessor
from estnltk.corpus import List
from estnltk.pyvabamorf import analyze, synthesize

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
