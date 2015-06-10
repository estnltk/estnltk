# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text


class ClausesTest(unittest.TestCase):

    def test_divide_multi(self):
        text = Text('Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.')
        clauses = text.divide('words', 'clauses')
        korred, _1, millel, on, toitunud, viljasaase, vastsed, _2, jaavad, ohukeseks, _3 = text.words
        self.assertListEqual([korred, jaavad, ohukeseks, _3], clauses[0])
        self.assertListEqual([_1, millel, on, toitunud, viljasaase, vastsed, _2], clauses[1])
        self.assertEqual(len(clauses), 2)

    def test_split_by_clauses(self):
        text = Text('Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.')
        outer = Text('Kõrred jäävad õhukeseks.').tag_clauses()
        inner = Text(', millel on toitunud väljasääse vastsed,').tag_clauses()
        outer_split, inner_split = text.split_by('clauses')
        self.assertListEqual(inner.word_spans, inner_split.word_spans)
        self.assertListEqual(outer.word_spans, outer_split.word_spans)
