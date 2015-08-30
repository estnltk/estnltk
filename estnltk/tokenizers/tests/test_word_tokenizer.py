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
        text = '25-26 D-vitaamini esma- ja -järel'
        expected_tokens = ['25-26', 'D-vitaamini', 'esma-', 'ja', '-järel']
        expected_spans = [(0, 5), (6, 17), (18, 23), (24, 26), (27, 33)]

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
