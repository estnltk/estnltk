# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..match import Match, concatenate_matches, copy_rename


class MatchConcatTest(unittest.TestCase):

    def a(self):
        return Match(0, 10, 'A')

    def a_without_name(self):
        return Match(0, 10)

    def b(self):
        return Match(10, 20, 'B')

    def c(self):
        m = Match(0, 20, 'C')
        m.matches['A'] = self.a()
        m.matches['B'] = self.b()
        return m

    def c_without_a(self):
        m = Match(0, 20, 'C')
        m.matches['B'] = self.b()
        return m

    def test_concatenation_with_names(self):
        match = concatenate_matches(self.a(), self.b(), 'C')
        expected = self.c()
        self.assertEqual(expected, match)

    def test_concatenation_without_names(self):
        match = concatenate_matches(self.a_without_name(), self.b(), 'C')
        expected = self.c_without_a()
        self.assertEqual(expected, match)
