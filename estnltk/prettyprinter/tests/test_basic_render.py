# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from pprint import pprint

from ...names import CLAUSES
from ...text import Text
from ..prettyprinter import PrettyPrinter


class TestRender(unittest.TestCase):

    def test_no_aesthetics(self):
        text = Text('See tekst on lihtsalt tühi')
        pp = PrettyPrinter()
        html = pp.render(text, False)
        self.assertEqual(text.text, html)

    def test_simple_annotations(self):
        text = Text('Siin tekstis on märgend siin ja teine on siin')
        text.tag_with_regex('annotations', 'siin')

        pp = PrettyPrinter(background='annotations')
        html = pp.render(text, False)

        expected = 'Siin tekstis on märgend <mark class="background">siin</mark> ja teine on <mark class="background">siin</mark>'
        self.assertEqual(expected, html)

    def test_multi_annotations(self):
        text = Text('Mees, kes oli tuttav, teretas meid.')
        text.tag_clauses()
        text['annotations'] = [text[CLAUSES][0]] # use the first clause only

        pp = PrettyPrinter(background='annotations')
        html = pp.render(text, False)

        expected = '<mark class="background">Mees</mark>, kes oli tuttav, <mark class="background">teretas meid.</mark>'
        self.assertEqual(expected, html)

    def test_two_layers_simple(self):
        text = Text('Esimene ja teine märgend')
        text.tag_with_regex('A', 'Esimene')
        text.tag_with_regex('B', 'teine')

        pp = PrettyPrinter(color='A', background='B')
        html = pp.render(text, False)

        expected = '<mark class="color">Esimene</mark> ja <mark class="background">teine</mark> märgend'
        self.assertEqual(expected, html)

    def test_two_layers_overlapping(self):
        text = Text('Esimene ja teine märgend')
        text.tag_with_regex('A', 'Esimene ja')
        text.tag_with_regex('B', 'ja teine')

        pp = PrettyPrinter(color='A', background='B')
        html = pp.render(text, False)

        expected = '<mark class="color">Esimene </mark><mark class="background color">ja</mark><mark class="background"> teine</mark> märgend'
        self.assertEqual(expected, html)

    def test_complex_overlapping(self):
        text = Text(                      'a b c d e f g h i j k')
        text.tag_with_regex('color',        'b c d e f g')
        text.tag_with_regex('background',   'b c d e')
        text.tag_with_regex('font',           'c d e f g h')
        text.tag_with_regex('size',           'c d e')
        text.tag_with_regex('tracking',             'f g h i')
        text.tag_with_regex('italics',                        'k')

        pp = PrettyPrinter(color='color',
                           background='background',
                           font='font',
                           size='size',
                           tracking='tracking',
                           italics='italics')
        html = pp.render(text, False)

        expected = ['a ',
                    '<mark class="background color">b </mark>',
                    '<mark class="background color font size">c d e</mark>',
                    '<mark class="color font"> </mark>',
                    '<mark class="color font tracking">f g</mark>',
                    '<mark class="font tracking"> h</mark>',
                    '<mark class="tracking"> i</mark>',
                    ' j ',
                    '<mark class="italics">k</mark>']
        self.assertEqual(''.join(expected), html)