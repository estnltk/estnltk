# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ...names import CLAUSES
from ...text import Text
from ..prettyprinter import PrettyPrinter


class TestRender(unittest.TestCase):

    def test_no_aesthetics(self):
        text = Text('See tekst on lihtsalt tühi')
        pp = PrettyPrinter()
        html = pp.render(text)
        self.assertEqual(text.text, html)

    def test_simple_annotations(self):
        text = Text('Siin tekstis on märgend siin ja teine on siin')
        text.annotate_with_regex('annotations', 'siin')

        pp = PrettyPrinter(background='annotations')
        html = pp.render(text)

        expected = 'Siin tekstis on märgend <mark class="background">siin</mark> ja teine on <mark class="background">siin</mark>'
        self.assertEqual(expected, html)

    def test_multi_annotations(self):
        text = Text('Mees, kes oli tuttav, teretas meid.')
        text.tag_clauses()
        text['annotations'] = [text[CLAUSES][0]] # use the first clause only

        pp = PrettyPrinter(background='annotations')
        html = pp.render(text)

        expected = '<mark class="background">Mees</mark>, kes oli tuttav, <mark class="background">teretas meid.</mark>'
        self.assertEqual(expected, html)

    def test_two_layers_simple(self):
        text = Text('Esimene ja teine märgend')
        text.annotate_with_regex('A', 'Esimene')
        text.annotate_with_regex('B', 'teine')

        pp = PrettyPrinter(color='A', background='B')
        html = pp.render(text)

        expected = '<mark class="color">Esimene</mark> ja <mark class="background">teine</mark> märgend'
        self.assertEqual(expected, html)

    def test_two_layers_overlapping(self):
        text = Text('Esimene ja teine märgend')
        text.annotate_with_regex('A', 'Esimene ja')
        text.annotate_with_regex('B', 'ja teine')

        pp = PrettyPrinter(color='A', background='B')
        html = pp.render(text)

        expected = '<mark class="color">Esimene </mark><mark classes="background color">ja</mark><mark class="background"> teine</mark> märgend'
        self.assertEqual(expected, html)
