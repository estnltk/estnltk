# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest

from estnltk import Corpus, Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter, VerbChainDetector
from pprint import pprint

text = 'Samas on selge, et senine korraldus jätkuda ei saa.'
an = PyVabamorfAnalyzer()
to = Tokenizer()
se = ClauseSegmenter()
vb = VerbChainDetector()

class VerbChainTest(unittest.TestCase):
    
    def test_corpus(self):
        corpus = vb(se(an(to(text))))
        self.assertEqual(len(corpus.verb_chains), 3)
        
    def test_json(self):
        corpus = Corpus.construct(vb(se(an(to(text))).to_json()))
        self.assertEqual(len(corpus.verb_chains), 3)

if __name__ == '__main__':
    unittest.main()
