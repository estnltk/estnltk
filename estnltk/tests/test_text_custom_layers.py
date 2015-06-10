# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..names import *


class CustomLayerTest(unittest.TestCase):

    @property
    def custom_layer(self):
        return [{START: 4, END: 9}, {START: 17, END: 24}]

    @property
    def custom_multilayer(self):
        return [{START: [1, 8], END: [5, 15]}, {START: [20, 25], END: [22, 30]}]

    @property
    def text(self):
        text = Text('See tekst on suhteliselt igav ning ei tähenda midagi')
        text['layer'] = self.custom_layer
        text['multilayer'] = self.custom_multilayer
        return text

    def test_texts(self):
        text = self.text
        self.assertEqual(text.texts('layer'), ['tekst', 'eliselt'])
        self.assertEqual(text.texts('multilayer'), ['ee t t on su', 'se igav '])

    def test_spans(self):
        text = self.text
        self.assertEqual(text.spans('layer'), [(e[START], e[END]) for e in self.custom_layer])
        self.assertEqual(text.spans('multilayer'), [(e[START], e[END]) for e in self.custom_multilayer])

    def test_layer_splitting(self):
        text = self.text
        texts = text.split_by('layer')
        self.assertEqual(2, len(texts))
        self.assertEqual('tekst', texts[0].text)
        self.assertEqual('eliselt', texts[1].text)

    def test_multilayer_splitting(self):
        text = self.text
        texts = text.split_by('multilayer')
        self.assertEqual('ee t t on su', texts[0].text)
        self.assertEqual('se igav ', texts[1].text)
