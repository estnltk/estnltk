# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..grammar import Regex, IRegex, Lemmas, Postags, Layer
from ..grammar import Union, Concatenation
from ...text import Text


class RegexTest(unittest.TestCase):

    def test_regex_cover(self):
        r = Regex('RR \d\d\d?')
        t = Text('RR 120 RR 50 rr 30')

        cover = r.get_cover(t)
        expected = [(0, 6), (7, 12)]

        self.assertListEqual(expected, cover)

    def test_iregex_cover(self):
        r = IRegex('RR \d\d\d?')
        t = Text('RR 120 RR 50 rr 30')

        cover = r.get_cover(t)
        expected = [(0, 6), (7, 12), (13, 18)]

        self.assertListEqual(expected, cover)


class LemmaTest(unittest.TestCase):

    def test_lemma_cover(self):
        l = Lemmas('jooksma', 'kargama', 'hüppama')
        t = Text('Kass kargas ja hiir hüppas')

        cover = l.get_cover(t)
        expected = [(5, 11), (20, 26)]

        self.assertListEqual(expected, cover)


class PostagTest(unittest.TestCase):

    def test_postag_cover(self):
        p = Postags('V')
        t = Text('Kass kargas ja hiir hüppas')

        cover = p.get_cover(t)
        expected = [(5, 11), (20, 26)]

        self.assertListEqual(expected, cover)


class LayerTest(unittest.TestCase):

    def test_layer_cover(self):
        l = Layer('annotation')
        t = Text('123 on annoteeritud')
        t.tag_with_regex('annotation', '\d+')

        cover = l.get_cover(t)
        expected = [(0, 3)]

        self.assertListEqual(expected, cover)


class UnionTest(unittest.TestCase):

    def test_union_cover(self):
        t = Text('Kass kargas ja hiir hüppas')
        u = Union(
            Postags('S'),
            Lemmas('kargama', 'hüppama')
        )

        cover = u.get_cover(t)
        expected = [(0, 4), (5, 11), (15, 19), (20, 26)]

        self.assertListEqual(expected, cover)


class ConcatenationTest(unittest.TestCase):

    def test_concatenation(self):
        t = Text('Kass kargas ja hiir hüppas')
        space = Regex('\s+')
        concat = Concatenation(
            Lemmas('kass'),
            space,
            Lemmas('kargama')
        )
        cover = concat.get_cover(t)
        expected = [(0, 11)]

        self.assertListEqual(expected, cover)
