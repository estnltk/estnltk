# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..match import Match, concatenate_matches, copy_rename


class MatchConcatTest(unittest.TestCase):

    def a(self):
        return Match(0, 10, '1234567890', 'A')

    def a_without_name(self):
        return Match(0, 10, '1234567890')

    def b(self):
        return Match(10, 20, '1234567890', 'B')

    def c(self):
        m = Match(0, 20, '12345678901234567890', 'C')
        m.matches['A'] = self.a()
        m.matches['B'] = self.b()
        return m

    def c_without_a(self):
        m = Match(0, 20, '12345678901234567890', 'C')
        m.matches['B'] = self.b()
        return m

    def test_concatenation_with_names(self):
        match = concatenate_matches(self.a(), self.b(), '12345678901234567890', 'C')
        expected = self.c()
        self.assertEqual(expected, match)

    def test_concatenation_without_names(self):
        match = concatenate_matches(self.a_without_name(), self.b(), '12345678901234567890', 'C')
        expected = self.c_without_a()
        self.assertEqual(expected, match)
