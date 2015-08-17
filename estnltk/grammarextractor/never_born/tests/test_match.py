# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from copy import deepcopy
from ..match import *


class MatchTest(unittest.TestCase):

    def test_encapsulate(self):
        match = Match('mymatch', 0, 4, 'tere')
        expected = Match('parent', 0, 4, 'tere', match)
        actual = encapsulate_match('parent', match)
        self.assertEqual(expected, actual)

    def test_link(self):
        a = Match('A', 0, 7, 'esimene')
        b = Match('B', 7, 12, 'teine')
        actual = a.link(b)
        expected = Match('A', 0, 7, 'esimene', None, Match('B', 7, 12, 'teine'))
        expected.chain_end = 12
        expected.chain_content = 'esimeneteine'

        self.assertEqual(expected, actual)
