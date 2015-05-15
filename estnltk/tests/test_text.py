# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from ..text import Text

import unittest
import regex as re


class TextInitializationTest(unittest.TestCase):

    def test_initialization(self):
        # initialize from a dictionary
        text = Text(self.text())
        self.assertDictEqual(text, self.text())

        # initialize from plain text
        text = Text('Tere maailm!')
        self.assertDictEqual(text, self.text())

    def test_initialization_fails(self):
        def create():
            Text({'something': 'else'})

        self.assertRaises(Exception, create)

    def text(self):
        return {'text': 'Tere maailm!'}


class TextSplittingTest(unittest.TestCase):

    def test_split_by_sentences(self):
        text = Text('Esimene lause. Teine lause. Kolmas lause. See on neljas.')
        text.compute_words()
        sentences = text.split_by_sentences()
        expected = [
            self.sentence('Esimene lause.'),
            self.sentence('Teine lause.'),
            self.sentence('Kolmas lause.'),
            self.sentence('See on neljas.')
        ]
        self.assertListEqual(expected, sentences)

    def sentence(self, text):
        return Text(text).compute_sentences().compute_words()

    def test_split_by_words(self):
        text = Text('Kirjakeel koosneb sõnadest.')
        text.compute_analysis()
        words = text.split_by_words()
        expected = [
            self.word('Kirjakeel'),
            self.word('koosneb'),
            self.word('sõnadest'),
            self.word('.')
        ]
        self.assertListEqual(expected, words)

    def word(self, word):
        return Text(word).compute_analysis()

    def test_split_by_regex(self):
        text = Text("SUUR väike SUUR väike SUUR")
        regex = '[A-Z ]+'
        texts = text.split_by_regex(regex)
        expected = [Text('väike'), Text('väike')]
        self.assertListEqual(expected, texts)

    def test_split_by_regex_notcaps(self):
        text = Text("SUUR väike SUUR")
        regex = '[A-Z]+'
        texts = text.split_by_regex(regex, gaps=False)
        expected = [Text('SUUR'), Text('SUUR')]
        self.assertListEqual(expected, texts)

