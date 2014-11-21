# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk.core import JsonPaths

import unittest
import os

# also include pyvabamorf tests as they are part of estnltk
from pyvabamorf.tests.test_analyze import *
from pyvabamorf.tests.test_synthesize import *
from pyvabamorf.tests.test_multi import *

class PyVabamorfAnalyzerTest(unittest.TestCase):
    
    def test_morphoanalysis(self):
        to = Tokenizer()
        an = PyVabamorfAnalyzer()
        result = an(to(self.text()))
        # we only check if each word has an analysis element, not
        # the exact output
        for words in JsonPaths.words.find(result):
            for word in words.value:
                self.assertTrue('analysis' in word)
        
    
    def text(self):
        return 'Kui ära minna, ei saa me enam mett!'


if __name__ == '__main__':
    unittest.main()

