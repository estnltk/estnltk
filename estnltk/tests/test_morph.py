# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk.core import JsonPaths
from estnltk.names import *

import unittest
import os


class PyVabamorfAnalyzerTest(unittest.TestCase):
    
    def setUp(self):
        self.to = Tokenizer()
        self.an = PyVabamorfAnalyzer()
    
    def test_morphoanalysis_corpus(self):
        result = self.an(self.to(self.text()))
        # we only check if each word has an analysis element, not
        # the exact output
        for word in result.words:
            self.assertTrue(ANALYSIS in word)
    
    def test_morphoanalysis_json(self):
        result = self.an(self.to(self.text()).to_json())
        # we only check if each word has an analysis element, not
        # the exact output
        for words in JsonPaths.words.find(result):
            for word in words.value:
                self.assertTrue(ANALYSIS in word)
        
    
    def text(self):
        return 'Kui ära minna, ei saa me enam mett!'


if __name__ == '__main__':
    unittest.main()

