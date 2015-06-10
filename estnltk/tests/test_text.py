# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..names import *
from pprint import pprint

import datetime
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

    def test_empty(self):
        Text('').tag_analysis()

    def text(self):
        return {TEXT: 'Tere maailm!'}


class TokenizationTest(unittest.TestCase):

    def test_tokenization(self):
        text = Text('''Lugejal vöib ette tulla , at korraehitamine on iseenesest arusaadav ide , mis juba eelnevalt teada oli . Mullat oli aga ainult se isik kes sellist L.V. omadust tõestanud ??''')
        text.tag_analysis()


class TextSplittingTest(unittest.TestCase):

    def test_split_by_sentences(self):
        text = Text('Esimene lause. Teine lause.')
        text.tokenize_words()
        del text[PARAGRAPHS]
        sentences = text.split_by_sentences()
        expected = [
            self.sentence('Esimene lause.'),
            self.sentence('Teine lause.')
        ]
        self.assertListEqual(expected, sentences)

    def sentence(self, text):
        t = Text(text).tokenize_sentences().tokenize_words()
        del t[PARAGRAPHS]
        return t

    def test_split_by_words(self):
        text = Text('Kirjakeel koosneb sõnadest.')
        text.tag_analysis()
        words = text.split_by_words()
        expected = [
            self.word('Kirjakeel'),
            self.word('koosneb'),
            self.word('sõnadest'),
            self.word('.')
        ]
        self.assertListEqual(expected, words)

    def word(self, word):
        word = Text(word).tag_analysis()
        word['sentences'] = []
        word['paragraphs'] = []
        return word

    def test_split_by_regex(self):
        text = Text("SUUR väike SUUR väike SUUR")
        regex = '[A-Z ]+'
        texts = text.split_by_regex(regex)
        expected = [Text('väike'), Text('väike')]
        self.assertListEqual(expected, texts)

    def test_split_by_regex_notcaps(self):
        text = Text("SUUR väike SUUR")
        regex = re.compile('[A-Z]+')
        texts = text.split_by_regex(regex, gaps=False)
        expected = [Text('SUUR'), Text('SUUR')]
        self.assertListEqual(expected, texts)


class TextDivideTest(unittest.TestCase):

    def test_divide(self):
        text = self.text
        divisions = text.divide()
        self.assertListEqual(self.divisions, divisions)

    def test_modifying_reference(self):
        text = self.text
        divisions = text.divide()
        divisions[2][1]['text'] = 'LAUSE'
        self.assertEqual(text.words[7]['text'], 'LAUSE')

    @property
    def text(self):
        return Text('Esimene lause. Teine lause. Kolmas lause!')

    @property
    def divisions(self):
        text = self.text.tokenize_words()
        words = text.words
        return [
            [words[0], words[1], words[2]],
            [words[3], words[4], words[5]],
            [words[6], words[7], words[8]]
        ]

