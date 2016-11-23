# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..morf import syllabify_word
import unittest
from pprint import pprint


class SyllabificationTest(unittest.TestCase):

    def test_elagu(self):
        actual = syllabify_word('elagu')
        expected = [{'accent': 1, 'quantity': 1, 'syllable': 'e'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'la'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'gu'}]
        self.assertListEqual(expected, actual)

    def test_luuad(self):
        actual = syllabify_word('luuad')
        expected = [{'accent': 1, 'quantity': 2, 'syllable': 'luu'},
                    {'accent': 0, 'quantity': 2, 'syllable': 'ad'}]
        self.assertListEqual(expected, actual)

    def test_lasteaialaps(self):
        # ilmselt toimiks kui iga liits6na komponent eraldi silbitada
        actual = syllabify_word('lasteaialaps')
        expected = [{'accent': 1, 'quantity': 1, 'syllable': 'e'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'la'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'gu'}]
        #self.assertListEqual(expected, actual)
