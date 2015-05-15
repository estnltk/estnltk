# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest

from estnltk import Corpus, Tokenizer, PyVabamorfAnalyzer, TimexTagger
from pprint import pprint

text = 'Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'
an = PyVabamorfAnalyzer()
to = Tokenizer()
ta = TimexTagger()

class TimexTest(unittest.TestCase):
    
    def test_corpus(self):
        corpus = ta(an(to(text)))
        self.assertEqual(len(corpus.timexes), 3)
        
    def test_json(self):
        corpus = Corpus.construct(ta(an(to(text)).to_json()))
        self.assertEqual(len(corpus.timexes), 3)

if __name__ == '__main__':
    unittest.main()
