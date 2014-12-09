# -*- coding: utf-8 -*-
import unittest
from estnltk import Corpus, Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
from pprint import pprint


class ClauseSegmenterTest(unittest.TestCase):
    
    def test_segmenter_corpus(self):
        text = 'Kui Arno oli isaga koolimajja jõudnud, olid tunnid juba alanud'
        an = PyVabamorfAnalyzer()
        to = Tokenizer()
        seg = ClauseSegmenter()
        corpus = seg(an(to(text)))
        self.assertEqual(len(corpus.clauses), 2)
        
    def test_segmenter_json(self):
        text = 'Kui Arno oli isaga koolimajja jõudnud, olid tunnid juba alanud'
        an = PyVabamorfAnalyzer()
        to = Tokenizer()
        seg = ClauseSegmenter()
        corpus = seg(an(to(text)).to_json())
        corpus = Corpus.construct(corpus)
        self.assertEqual(len(corpus.clauses), 2)

                
if __name__ == '__main__':
    unittest.main()
