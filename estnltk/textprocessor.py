# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.corpus import Corpus
from copy import deepcopy


class TextProcessor(object):
    '''Base class for text processors.'''
    
    def __call__(self, *args, **kwargs):
        '''Shorthand way of using TextProcessors.'''
        return self.process(*args, **kwargs)
    
    def process(self, corpus, inplace=False, **kwargs):
        '''Process the corpus.
        
        Parameters
        ----------
        corpus: estnltk.corpus.Corpus
            The corpus to process.
        inplace: boolean
            If True, modifies the corpus inplace. Otherwise creates
            a copy first when applying modifications.
        
        Keyword parameters are subclass specific.
        '''
        if not inplace:
            corpus = deepcopy(corpus)
        if isinstance(corpus, Corpus):
            return self.process_corpus(corpus, **kwargs)
        return self.process_json(corpus, **kwargs)
    
    def process_json(self, corpus, **kwargs):
        raise NotImplementedError()
        
    def process_corpus(self, corpus, **kwargs):
        raise NotImplementedError()
