# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.javaprocess import JavaProcess, JAVARES_PATH
from estnltk.textprocessor import TextProcessor
from estnltk.core import JsonPaths
from estnltk.names import *

from pprint import pprint

import os
import json


RENAMING_MAP = {
    'temporalFunction': TMX_TEMP_FUNCTION,
    'anchorTimeID': TMX_ANCHOR,
    'beginPoint': TMX_BEGINPOINT,
    'endPoint': TMX_ENDPOINT,
}

class TimexDetector(JavaProcess, TextProcessor):
    
    def __init__(self):
        JavaProcess.__init__(self, 'Ajavt.jar', ['-pyvabamorf', '-r', os.path.join(JAVARES_PATH, 'reeglid.xml')])

    def process_json(self, corpus, **kwargs):
        for sentence_ptr in JsonPaths.words.find(corpus):
            sentence_ptr.value = self.process_words(sentence_ptr.value)
        return corpus

    def process_corpus(self, corpus, **kwargs):
        for sentence in corpus.sentences:
            sentence[WORDS] = self.process_words(sentence[WORDS])
        return corpus
    
    def process_words(self, words):
        sentence = {WORDS: words}
        return self.rename_attributes(json.loads(self.process_line(json.dumps(sentence)))[WORDS])
    
    def rename_attributes(self, sentence):
        for word in sentence:
            if TIMEXES in word:
                for timex in word[TIMEXES]:
                    for k, v in timex.items():
                        # rename javaStyle to python_style
                        if k in RENAMING_MAP:
                            timex[RENAMING_MAP[k]] = v
                            del timex[k]
                        # trim "t" from id and anchor time
                        if k in [TMX_ID, TMX_ANCHOR] and v.startswith('t'):
                            timex[k] = int(v[1:])
        return sentence
            
from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()

t = analyzer(tokenizer('Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'), phonetic=False)
det = TimexDetector()
pprint(det(t).to_json())

