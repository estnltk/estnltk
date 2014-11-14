# -*- coding: utf-8 -*-
'''
Module containing functionality for adding morphological analysis
information to corpora.
'''
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths
from pyvabamorf import analyze
from itertools import izip


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
            words_texts = [word['text'] for word in words.value]
            for idx, analysis in enumerate(analyze(words_texts)):
                words.value[idx]['analysis'] = analysis['analysis']
        return corpus
