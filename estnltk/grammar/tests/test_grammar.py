# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..grammar import Regex, IRegex, Lemmas, Postags, Layer, Intersection, Suffix, LayerRegex
from ..grammar import Union, Concatenation
from ..match import Match
from ...text import Text


class UnionTest(unittest.TestCase):

    def text(self):
        return Text('Kass hüppas ja hiir kargas!')

    def a(self):
        return Lemmas('Kass')

    def b(self):
        return Postags('V')

    def test_union_without_names(self):
        u = Union(
            self.a(),
            self.b()
        )
        matches = u.get_matches(self.text())
        expected = [Match(0, 4, 'Kass'), Match(5, 11, 'hüppas'), Match(20, 26, 'kargas')]

        self.assertListEqual(expected, matches)

    def a_with_name(self):
        return Lemmas('kass', name='kaslane')

    def b_with_name(self):
        return Postags('V', name='tegevus')

    def test_union_with_names(self):
        u = Union(
            self.a_with_name(),
            self.b_with_name()
        )
        matches = u.get_matches(self.text())
        expected = [Match(0, 4, 'Kass', name='kaslane'), Match(5, 11, 'hüppas', name='tegevus'), Match(20, 26, 'kargas', name='tegevus')]

        self.assertListEqual(expected, matches)

    def test_union_renaming(self):
        u = Union(
            self.a_with_name(),
            self.b_with_name(),
            name='ühend'
        )
        matches = u.get_matches(self.text())
        expected = [Match(0, 4, 'Kass', name='ühend'), Match(5, 11, 'hüppas', name='ühend'), Match(20, 26, 'kargas', name='ühend')]

        self.assertListEqual(expected, matches)


class ConcatTest(unittest.TestCase):

    def text(self):
        return Text('Kass hüppas ja hiir kargas!')

    def space(self):
        return IRegex('\s+')

    def a(self):
        return Lemmas('Kass')

    def b(self):
        return Postags('V')

    def a_with_name(self):
        return Lemmas('kass', name='kaslane')

    def b_with_name(self):
        return Postags('V', name='tegevus')

    def test_concat_without_names(self):
        c = Concatenation(
            self.a(),
            self.space(),
            self.b()
        )

        matches = c.get_matches(self.text())
        expected = [Match(0, 11, 'Kass hüppas')]

        self.assertListEqual(expected, matches)

    def test_concat_with_names(self):
        c = Concatenation(
            self.a_with_name(),
            self.space(),
            self.b_with_name(),
            name='fraas'
        )

        matches = c.get_matches(self.text())
        expected = [self.c_with_names()]

        self.assertListEqual(expected, matches)

    def c_with_names(self):
        match = Match(0, 11, 'Kass hüppas', 'fraas')
        match.matches['kaslane'] = Match(0, 4, 'Kass', 'kaslane')
        match.matches['tegevus'] = Match(5, 11, 'hüppas', 'tegevus')
        return match


class IntersectionTest(unittest.TestCase):

    def text(self):
        return Text('Suured kollased viisnurklikud meritähed')

    def adjectives(self):
        return Postags('A')

    def ed_suffix(self):
        return Suffix('ed')

    def ed_suffix_regex(self):
        return IRegex('\\b[^\s].*?ed\\b')

    def expected(self):
        return [Match(0, 6, 'Suured'), Match(7, 15, 'kollased')]

    def test_intersection_with_suffix(self):
        i = Intersection(
            self.adjectives(),
            self.ed_suffix()
        )
        matches = i.get_matches(self.text())
        self.assertListEqual(self.expected(), matches)

    def test_intersection_with_suffix_regex(self):
        i = Intersection(
            self.adjectives(),
            self.ed_suffix_regex()
        )
        matches = i.get_matches(self.text())
        self.assertListEqual(self.expected(), matches)

    def test_intersection_more_elements(self):
        i = Intersection(
            self.adjectives(),
            self.ed_suffix_regex(),
            Layer('words'),
            self.ed_suffix()
        )
        matches = i.get_matches(self.text())
        self.assertListEqual(self.expected(), matches)


class LayerRegexTest(unittest.TestCase):

    def test_layer_regex(self):
        text = Text('Janne ja Hendrik käisid Ilvese rabas jalutamas')
        text.tag_named_entities()
        lr = LayerRegex('named_entities', 'Ilv.*')
        matches = lr.get_matches(text)
        expected = [Match(24, 30, 'Ilvese')]
        self.assertListEqual(expected, matches)

