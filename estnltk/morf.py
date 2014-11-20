# -*- coding: utf-8 -*-
'''
Module containing functionality for adding morphological analysis
information to corpora.

Attributes
----------

analyer: PyVabamorfAnalyzer
    Analyzer with default parameters.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths
from pyvabamorf import analyze
from itertools import izip
from pprint import pprint


class PyVabamorfAnalyzer(object):
    
    def __call__(self, *args, **kwargs):
        return self.analyze(*args, **kwargs)
    
    def analyze(self, corpus, phonetic=False, compound=True):
        '''Annotate a JSON-style corpus with morphological information
        from vabamorf.
        
        Parameters
        ----------
        corpus: dict or list
            The tokenized corpus.
            
        Keyword parameters
        ------------------
        phonetic: boolean
            If true, add phonetic markup to root elements (default: False)
        compound: boolean
            If true, add compound word markup to root elements (default: True)
            
        Returns
        -------
        dict or list
            The inputted dictionary, but with additional annotations.
        '''
        for words in JsonPaths.words.find(corpus):
            for idx in range(len(words.value)):
                analysis = analyze(words.value[idx]['text'], phonetic=phonetic, compound=compound)[0]['analysis']
                words.value[idx]['analysis'] = analysis
        return corpus

analyzer = PyVabamorfAnalyzer()
