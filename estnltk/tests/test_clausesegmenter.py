# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest
from estnltk import Corpus, Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
from pprint import pprint

an = PyVabamorfAnalyzer()
to = Tokenizer()

text1 = 'Kui Arno oli isaga koolimajja jõudnud, olid tunnid juba alanud'
seg1 = ClauseSegmenter()

text2 = 'Pritsimehed leidsid eest lõõmava kapotialusega auto mida läheduses parkinud masinate sohvrid eemale üritasid lükata kuid esialgu see ei õnnestunud sest autol oli käik sees.'
seg2 = ClauseSegmenter(ignore_missing_commas=True)
        
class ClauseSegmenterTest(unittest.TestCase):
    
    def test_segmenter_corpus(self):        
        corpus = seg1(an(to(text1)))
        self.assertEqual(len(corpus.clauses), 2)
        
    def test_segmenter_json(self):
        corpus = seg1(an(to(text1)).to_json())
        corpus = Corpus.construct(corpus)
        self.assertEqual(len(corpus.clauses), 2)

    def test_segmenter_corpus_ignore_missing_commas(self):        
        corpus = seg2(an(to(text2)))
        self.assertEqual(len(corpus.clauses), 4)

    def test_segmenter_json_ignore_missing_commas(self):
        corpus = seg2(an(to(text2)).to_json())
        corpus = Corpus.construct(corpus)
        self.assertEqual(len(corpus.clauses), 4)

if __name__ == '__main__':
    unittest.main()
