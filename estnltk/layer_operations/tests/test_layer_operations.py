# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from pprint import pprint

import unittest
from ...text import Text
from ..operations import keep_layer
from ..operations import delete_layer
from ..operations import new_layer_with_regex
from ..operations import apply_simple_filter
from ..operations import compute_layer_intersection


def first_text():
    return 'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul maanteel tünjat Tallinnfilmi režissööri.'


def second_text():
    return 'Haapsalu (Läänemaa murrakutes varem ka Oablu või Aablu) on linn Eestis Läänemere ääres Haapsalu lahe ' \
           'lõunakaldal, Lääne maakonna halduskeskus. Linna territooriumi hulka kuulub Krimmi holm. Haapsalu ' \
           'linnapea on Urmas Sukles'


# Text object to test union, intersection and exact operations
def third_text():
    return {'Tartu': [{'end': 5, 'start': 0, 'text': 'Tartu'},
                      {'end': 291, 'start': 286, 'text': 'Tartu'},
                      {'end': 434, 'start': 429, 'text': 'Tartu'},
                      {'end': 485, 'start': 480, 'text': 'Tartu'},
                      {'end': 527, 'start': 522, 'text': 'Tartu'},
                      # Added lines here that are not correct
                      {'end': 333, 'start': 287, 'text': 'Tartu'},
                      {'end': 330, 'start': 284, 'text': 'Tartu'},
                      {'end': 331, 'start': 286, 'text': 'Tartu'}],
            'Tartu Tehnoloogia ja Rakenduste Arenduskeskus': [{'end': 331,
                                                               'start': 286,
                                                               'text': 'Tartu '
                                                                       'Tehnoloogia '
                                                                       'ja Rakenduste '
                                                                       'Arenduskeskus'},
                                                              # Added lines here that are not correct
                                                              {'end': 474,
                                                               'start': 429,
                                                               'text': 'Tartu '
                                                                       'Tehnoloogia '
                                                                       'ja Rakenduste '
                                                                       'Arenduskeskus'}],
            'text': 'Tartu Ulikooli, Tallinna Tehnikaulikooli ja ettevotete koostoos '
                    'initsialiseeritud tehnoloogia arenduskeskus Tarkvara TAK pakub '
                    'ettevotetele ja teistele partneritele teadus- ja arendustoo ning '
                    'alus ja rakendusuuringute teenuseid. Uurimisvaldkondadeks on '
                    'andmekaeve ning tarkvaratehnika. Tartu Tehnoloogia ja Rakenduste '
                    'Arenduskeskuste programm (link is external) on Euroopa '
                    'Regionaalarengu fondist EAS kaudu rahastatav programm.  Tartu '
                    'Tehnoloogia ja Rakenduste Arenduskeskus asub Tartus juba 5 aastat. '
                    'Koostood tehakse ja Tartu ettevottega Cybernetica.'}


def text_tok():
    text = Text(first_text())
    text.tag_clauses().tag_named_entities()
    return text


def text_sentences():
    text = Text(first_text())
    text.sentences
    return text


def text_ner():
    text = Text(second_text())
    text.tag_named_entities()
    return text


def text_keep_layer():
    return {'named_entities': [{'end': 90, 'label': 'LOC', 'start': 78}],
            'text': 'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul '
                    'maanteel tünjat Tallinnfilmi režissööri.'}


def text_delete_layer():
    return {'named_entities': [{'end': 90, 'label': 'LOC', 'start': 78}],
            'paragraphs': [{'end': 102, 'start': 0}],
            'sentences': [{'end': 14, 'start': 0},
                          {'end': 30, 'start': 15},
                          {'end': 102, 'start': 31}],
            'text': 'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul '
                    'maanteel tünjat Tallinnfilmi režissööri.'}


def text_new_layer_with_regex():
    return {'new': [{'end': 90, 'start': 78, 'text': 'Tallinnfilmi'},
                    {'end': 101, 'start': 91, 'text': 'režissööri'}],
            'paragraphs': [{'end': 102, 'start': 0}],
            'sentences': [{'end': 14, 'start': 0},
                          {'end': 30, 'start': 15},
                          {'end': 102, 'start': 31}],
            'text': 'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul '
                    'maanteel tünjat Tallinnfilmi režissööri.'}


def text_apply_layer_filter_or():
    return [{'end': 8, 'label': 'LOC', 'start': 0},
            {'end': 18, 'label': 'LOC', 'start': 10},
            {'end': 44, 'label': 'PER', 'start': 39},
            {'end': 70, 'label': 'LOC', 'start': 64},
            {'end': 80, 'label': 'LOC', 'start': 71},
            {'end': 100, 'label': 'LOC', 'start': 87},
            {'end': 128, 'label': 'LOC', 'start': 114},
            {'end': 182, 'label': 'LOC', 'start': 176},
            {'end': 197, 'label': 'LOC', 'start': 189}]


def text_apply_layer_filter_and():
    return [{'label': 'LOC', 'end': 182, 'start': 176}]


def text_apply_simple_filter_without_restriction():
    return [{'end': 8, 'label': 'LOC', 'start': 0},
            {'end': 18, 'label': 'LOC', 'start': 10},
            {'end': 44, 'label': 'PER', 'start': 39},
            {'end': 54, 'label': 'PER', 'start': 49},
            {'end': 70, 'label': 'LOC', 'start': 64},
            {'end': 80, 'label': 'LOC', 'start': 71},
            {'end': 100, 'label': 'LOC', 'start': 87},
            {'end': 128, 'label': 'LOC', 'start': 114},
            {'end': 182, 'label': 'LOC', 'start': 176},
            {'end': 197, 'label': 'LOC', 'start': 189},
            {'end': 222, 'label': 'PER', 'start': 210}]


def layer_operations_result_exact():
    return [{'end': 331, 'start': 286}]


def layer_operations_result_intersection():
    return [{'end': 291, 'start': 286},
            {'end': 434, 'start': 429},
            {'end': 331, 'start': 287},
            {'end': 330, 'start': 286},
            {'end': 331, 'start': 286}]


def layer_operations_result_union():
    return [{'end': 331, 'start': 286},
            {'end': 474, 'start': 429},
            {'end': 333, 'start': 286},
            {'end': 331, 'start': 284},
            {'end': 331, 'start': 286}]


class LayerOperationTest(unittest.TestCase):
    def test_keep_layer(self):
        text = text_tok()
        self.assertTrue('text' in text)
        self.assertTrue('words' in text)
        processed_text = keep_layer(text, ['named_entities'])
        self.assertEqual(text_keep_layer(), processed_text)

    def test_delete_layer(self):
        text = text_tok()
        self.assertTrue('words' in text)
        self.assertTrue('clauses' in text)
        processed_text = delete_layer(text, ['words', 'clauses'])
        self.assertEqual(text_delete_layer(), processed_text)

    def test_new_layer_with_regex(self):
        text = text_sentences()
        self.assertTrue('text' in text)
        self.assertTrue('sentences' in text)
        processed_text = new_layer_with_regex(text, 'new', ['Tallinnfilmi', 'režissööri'])
        self.assertEqual(text_new_layer_with_regex(), processed_text)

    def test_apply_simple_filter_or(self):
        text = text_ner()
        self.assertTrue('named_entities' in text)
        self.assertTrue('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities', {'end': 44, 'label': 'LOC'}, 'OR')
        self.assertEquals(text_apply_layer_filter_or(), processed_text)

    def test_apply_simple_filter_and(self):
        text = text_ner()
        self.assertTrue('named_entities' in text)
        self.assertTrue('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities', {'end': 182, 'label': 'LOC'}, 'AND')
        self.assertEquals(text_apply_layer_filter_and(), processed_text)

    def test_apply_simple_filter_without_restriction(self):
        text = text_ner()
        self.assertTrue('named_entities' in text)
        self.assertTrue('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities')
        self.assertEquals(text_apply_simple_filter_without_restriction(), processed_text)

    def test_layer_operations(self):
        text = third_text()
        exact = compute_layer_intersection(text, 'Tartu', 'Tartu Tehnoloogia ja Rakenduste Arenduskeskus',
                                           method='EXACT')

        union = compute_layer_intersection(text, 'Tartu',
                                           'Tartu Tehnoloogia ja Rakenduste Arenduskeskus',
                                           method='UNION')
        intersection = compute_layer_intersection(text, 'Tartu',
                                                  'Tartu Tehnoloogia ja Rakenduste Arenduskeskus',
                                                  method='INTERSECTION')

        self.assertEqual(exact, layer_operations_result_exact())
        self.assertEqual(union, layer_operations_result_union())
        self.assertEqual(intersection, layer_operations_result_intersection())


if __name__ == '__main__':
    unittest.main()
