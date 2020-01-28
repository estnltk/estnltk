# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..morf import syllabify_word
from ..morf import _split_word_for_syllabification
from ..morf import _split_compound_word_heuristically
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
        pprint (actual)
        expected = [{'accent': 1, 'quantity': 1, 'syllable': 'e'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'la'},
                     {'accent': 0, 'quantity': 1, 'syllable': 'gu'}]
        #self.assertListEqual(expected, actual)

    def test_split_word_for_syllabification(self):
        # Case 1
        actual = _split_word_for_syllabification('jagamata')
        expected = ['jagamata']
        self.assertListEqual(expected, actual)
        # Case 2
        actual = _split_word_for_syllabification('ja/da-ma/ga///----ja-jah-')
        expected = ['ja', '/', 'da', '-', 'ma', '/', 'ga', '/', '/', '/', '-', '-', '-', '-', 'ja', '-', 'jah', '-']
        self.assertListEqual(expected, actual)
        # Case 3
        actual = _split_word_for_syllabification('-')
        expected = ['-']
        self.assertListEqual(expected, actual)

    def test_syllabification_on_dash_and_slash_symbols(self):
        # Case 1
        actual = syllabify_word('vana-ema')
        expected = \
        [{'accent': 1, 'quantity': 1, 'syllable': 'va'},
         {'accent': 0, 'quantity': 1, 'syllable': 'na'},
         {'accent': 1, 'quantity': 3, 'syllable': '-'},
         {'accent': 1, 'quantity': 1, 'syllable': 'e'},
         {'accent': 0, 'quantity': 1, 'syllable': 'ma'}]
        self.assertListEqual(expected, actual)
        # Case 2
        actual = syllabify_word('/')
        expected = \
          [{'accent': 1, 'quantity': 3, 'syllable': '/'}]
        self.assertListEqual(expected, actual)
        # Case 3
        actual = syllabify_word('igavene-tuha/juhan')
        expected = \
         [{'accent': 1, 'quantity': 1, 'syllable': 'i'},
          {'accent': 0, 'quantity': 1, 'syllable': 'ga'},
          {'accent': 0, 'quantity': 1, 'syllable': 've'},
          {'accent': 0, 'quantity': 1, 'syllable': 'ne'},
          {'accent': 1, 'quantity': 3, 'syllable': '-'},
          {'accent': 1, 'quantity': 1, 'syllable': 'tu'},
          {'accent': 0, 'quantity': 1, 'syllable': 'ha'},
          {'accent': 1, 'quantity': 3, 'syllable': '/'},
          {'accent': 1, 'quantity': 1, 'syllable': 'ju'},
          {'accent': 0, 'quantity': 2, 'syllable': 'han'}]
        self.assertListEqual(expected, actual)

    def test_split_compound_word_heuristically(self):
        # Case 0
        actual = _split_compound_word_heuristically('')
        expected = ['']
        self.assertListEqual(expected, actual)
        # Case 1
        actual = _split_compound_word_heuristically('ema')
        expected = ['ema']
        self.assertListEqual(expected, actual)
        # Case 2
        actual = _split_compound_word_heuristically('vanaema')
        expected = ['vana', 'ema']
        self.assertListEqual(expected, actual)
        # Case 3
        actual = _split_compound_word_heuristically('vanaemadele')
        expected = ['vana', 'emadele']
        self.assertListEqual(expected, actual)
        # Case 4
        actual = _split_compound_word_heuristically('lasteaialastelegi')
        expected = ['laste', 'aia', 'lastelegi']
        self.assertListEqual(expected, actual)
        # Case 5
        actual = _split_compound_word_heuristically('noorsandideks')
        expected = ['noor', 'sandideks']
        self.assertListEqual(expected, actual)
        # Case 6
        actual = _split_compound_word_heuristically('--')
        expected = ['--']
        self.assertListEqual(expected, actual)
        actual = _split_compound_word_heuristically('-------')
        expected = ['-------']
        self.assertListEqual(expected, actual)