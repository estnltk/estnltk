# -*- coding: utf-8 -*-

from estnltk.core import JsonPaths

from pyvabamorf import analyze_sentence
from itertools import izip

class PyVabamorfAnalyzer(object):
    
    def __call__(self, corpus):
        '''Annotate an EstNltkCorpus with morphological information.'''
        for words in JsonPaths.words.find(corpus):
            words_texts = [word['text'] for word in words.value]
            for idx, analysis in enumerate(analyze_sentence(words_texts)):
                words.value[idx]['analysis'] = analysis['analysis']
        return corpus
