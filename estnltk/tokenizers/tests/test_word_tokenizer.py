# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..word_tokenizer import EstWordTokenizer

tokenizer = EstWordTokenizer()


class WordTokenizerTest(unittest.TestCase):

    def test_ordinals(self):
        text = '19. sajandil toimus 19. sajandil toimus 19.'
        expected_tokens = ['19.', 'sajandil', 'toimus', '19.', 'sajandil', 'toimus', '19.']
        expected_spans = [(0, 3), (4, 12), (13, 19), (20, 23), (24, 32), (33, 39), (40, 43)]

        tokens, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)

        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)

    def test_hyphen(self):
        text = '25-26 D-vitaamini esma- ja -järel 8.-12.'
        expected_tokens = ['25-26', 'D-vitaamini', 'esma-', 'ja', '-järel', '8.-12.']
        expected_spans = [(0, 5), (6, 17), (18, 23), (24, 26), (27, 33), (34, 40)]

        tokens, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)

        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)

    def test_unusual_hyphens(self):
        # Tests for utf8 minus, dash and other hypen-like symbols, which can be used 
        # instead of the regular hypen symbol
        text = '25­26 D—vitaamini esma– ja −järel 8.—12.'
        expected_tokens = ['25­26', 'D—vitaamini', 'esma–', 'ja', '−järel', '8.—12.']
        expected_spans = [(0, 5), (6, 17), (18, 23), (24, 26), (27, 33), (34, 40)]
        
        tokens, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        
        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)

    def test_fractions(self):
        text = '3.14 3,14 3/4'
        expected_tokens = ['3.14', '3,14', '3/4']
        expected_spans = [(0, 4), (5, 9), (10, 13)]

        tokens, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)

        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)

    def test_abbreviations(self):
        text = 'v.a dekaan M. Munak XI sajandist e.Kr m.a.j'
        expected_tokens = ['v.a', 'dekaan', 'M.', 'Munak', 'XI', 'sajandist', 'e.Kr', 'm.a.j']
        expected_spans = [(0, 3), (4, 10), (11, 13), (14, 19), (20, 22), (23, 32), (33, 37), (38, 43)]
        
        tokens, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)

        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)

    def test_mistakenly_conjoined_sentences(self):
        text1 = 'Iga päev teeme valikuid.Valime kõike.'
        expected_tokens = ['Iga', 'päev', 'teeme', 'valikuid', '.', 'Valime', 'kõike', '.']
        expected_spans  = [(0, 3), (4, 8), (9, 14), (15, 23), (23, 24), (24, 30), (31, 36), (36, 37)]
        tokens, spans = tokenizer.tokenize(text1), tokenizer.span_tokenize(text1)
        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)
        
        text2 = 'Ja siis veel ühe.Ja veel ühe.'
        expected_tokens = ['Ja', 'siis', 'veel', 'ühe', '.', 'Ja', 'veel', 'ühe', '.'] 
        expected_spans  = [(0, 2), (3, 7), (8, 12), (13, 16), (16, 17), (17, 19), (20, 24), (25, 28), (28, 29)]
        tokens, spans = tokenizer.tokenize(text2), tokenizer.span_tokenize(text2)
        self.assertListEqual(expected_tokens, tokens)
        self.assertListEqual(expected_spans, spans)
