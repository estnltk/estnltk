# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ...text import Text
from ..database import prepare_text
from pprint import pprint

def text():
    text = Text('Esimene lause. Teine lause.')
    text.tokenize_sentences()
    return text


def expected():
    return {'layers': {'paragraphs': {'lemmas': ['esimene lause . teine lause .'],
                           'texts': ['Esimene lause. Teine lause.']},
                       'sentences': {'lemmas': ['esimene lause .', 'teine lause .'],
                           'texts': ['Esimene lause.', 'Teine lause.']}},
            'text': {'paragraphs': [{'end': 27, 'start': 0}],
                     'sentences': [{'end': 14, 'start': 0}, {'end': 27, 'start': 15}],
                     'text': 'Esimene lause. Teine lause.'}}


class TestPrepare(unittest.TestCase):

    def test_prepare(self):
        prepared = prepare_text(text())
        self.assertTrue('layers' in prepared)
        self.assertTrue('text' in prepared)
        self.assertDictEqual(prepared['text'], text())
        self.assertDictEqual(expected(), prepared)

