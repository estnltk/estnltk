# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text


class ZipBuilderTest(unittest.TestCase):

    def test_as_zip(self):
        text = self.text()
        built_zip = text.get.word_texts.lemmas.postags.endings.as_zip
        expected = self.zip()
        self.assertListEqual(list(expected), list(built_zip))

    def text(self):
        return Text('Tuleb minna vanast raudteeülesõidukohast edasi ja pöörata paremale.')

    def zip(self):
        text = self.text()
        return zip(text.word_texts, text.lemmas, text.postags, text.endings)

    def test_as_list(self):
        text = self.text()
        built_list = text.get.word_texts.lemmas.postags.endings.as_list
        expected = self.list()
        self.assertListEqual(expected, built_list)

    def list(self):
        text = self.text()
        return [text.word_texts, text.lemmas, text.postags, text.endings]

    def test_as_dict(self):
        text = self.text()
        built_dict = text.get.word_texts.lemmas.postags.endings.as_dict
        expected = self.dict()
        self.assertDictEqual(expected, built_dict)

    def test_as_dataframe(self):
        text = self.text()
        df = text.get.word_texts.lemmas.as_dataframe
        self.assertListEqual(text.word_texts, list(df.word_texts))
        self.assertListEqual(text.lemmas, list(df.lemmas))

    def dict(self):
        text = self.text()
        return {
            "word_texts": text.word_texts,
            "lemmas": text.lemmas,
            "postags": text.postags,
            "endings": text.endings
        }

    def test_zipbuilder_call(self):
        text = self.text()
        built_list = text.get(['word_texts', 'lemmas', 'postags', 'endings']).as_list
        expected = self.list()
        self.assertListEqual(expected, built_list)