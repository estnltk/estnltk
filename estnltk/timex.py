# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.javaprocess import JavaProcess
from estnltk.core import JAVARES_PATH
from estnltk.core import JsonPaths

from pprint import pprint

import os
import json

class TimexDetector(JavaProcess):
    
    def __init__(self):
        JavaProcess.__init__(self, 'Ajavt.jar', ['-pyvabamorf', '-r', os.path.join(JAVARES_PATH, 'reeglid.xml')])

    def __call__(self, corpus):
        return self.detect(corpus)

    def detect(self, corpus):
        for sentence_ptr in JsonPaths.words.find(corpus):
            sentence = sentence_ptr.value
            sentence = {'words': sentence}
            sentence = json.loads(self._process_line(json.dumps(sentence)))['words']
            pprint(sentence)
            
from estnltk import tokenizer
from estnltk import analyzer

t = analyzer(tokenizer('25. veebruaril tuvastasime, et sada aastat vanad toimikud sisaldavaid homseid teadmisi'), phonetic=False)
det = TimexDetector()
det.detect(t)

