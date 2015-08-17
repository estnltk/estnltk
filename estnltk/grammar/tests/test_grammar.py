# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..grammar import Regex, IRegex, Lemmas, Postags, Layer
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
        expected = [Match(0, 4), Match(5, 11), Match(20, 26)]

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
        expected = [Match(0, 4, name='kaslane'), Match(5, 11, name='tegevus'), Match(20, 26, name='tegevus')]

        self.assertListEqual(expected, matches)

    def test_union_renaming(self):
        u = Union(
            self.a_with_name(),
            self.b_with_name(),
            name='ühend'
        )
        matches = u.get_matches(self.text())
        expected = [Match(0, 4, name='ühend'), Match(5, 11, name='ühend'), Match(20, 26, name='ühend')]

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
        expected = [Match(0, 11)]

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
        match = Match(0, 11, 'fraas')
        match.matches['kaslane'] = Match(0, 4, 'kaslane')
        match.matches['tegevus'] = Match(5, 11, 'tegevus')
        return match

