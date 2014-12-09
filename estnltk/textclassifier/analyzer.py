# -*- coding: utf-8 -*-
'''
Module containing functionality for processing Estonian.
'''
from __future__ import unicode_literals, print_function

from estnltk.textclassifier.synunifier import SynUnifier
from estnltk import analyze
import re

def get_stopwords():
    '''Function for obtaining Estonian stopwords.
    
    Returns
    -------
    set[str]
        Estonian stopwords.
    '''
    stopwords = 'ja ning ega ehk või kui ka aga ning sest on ole olema kes mis'
    return frozenset(stopwords.split())


class SimpleTextAnalyzer(object):
    '''Analyzer for preprocessing Estonian texts.
    
    Performs stopword removal, lemmatization and synonym unification
    '''

    def __init__(self, synunifier):
        '''Initialize the analyzer.
        
        Parameters
        ----------
        synunifier: SynUnifier
            Technical synonym unifier obraind from Settings instance of the classification task.
        '''
        assert isinstance(synunifier, SynUnifier)
        self._splitre = re.compile('\W+', flags = re.UNICODE | re.MULTILINE)
        self._digitre = re.compile('\d')
        self._stopwords = get_stopwords()
        self._unifier = synunifier

    def __call__(self, sentence):
        '''Analyze the given sentence.
        
        Parameters
        ----------
        sentence: str
            The sentence describing a record.
        
        Returns
        -------
        list[str]
            List of unique lemmas in the sentence. Note that their order is random.
        '''
        sentence = self._splitre.split(sentence.lower())
        sentence = self._remove_digits(sentence)
        sentence = self._lemmatize(sentence)
        sentence = self._remove_stopwords(sentence)
        sentence = self._perform_unification(sentence)
        return sentence

    def _lemmatize(self, sentence):
        return list(set([analysis['lemma'] for wa in analyze(sentence) for analysis in wa['analysis']]))

    def _perform_unification(self, sentence):
        return [self._unifier.unify(word) for word in sentence]

    def _remove_stopwords(self, sentence):
        return [word for word in sentence if word not in self._stopwords]

    def _remove_digits(self, sentence):
        return [word for word in sentence if not self._contains_digits(word)]
    
    def _contains_digits(self, word):
        return bool(self._digitre.search(word)) 
