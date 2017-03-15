# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from estnltk.legacy.text import Text
from ...layer_operations import apply_simple_filter
# from ...layer_operations import compute_layer_intersection
from ...layer_operations import conflicts
from ...layer_operations import count_by
from ...layer_operations import count_by_document
# from ...layer_operations import delete_layer
from ...layer_operations import dict_to_df
from ...layer_operations import diff_layer
# from ...layer_operations import get_text
from ...layer_operations import group_by_spans
# from ...layer_operations import keep_layer
from ...layer_operations import merge_layer
from ...layer_operations import new_layer_with_regex
from ...layer_operations import unique_texts


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
        
        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': []}
        result = keep_layer(text, [])        
        self.assertDictEqual(result, expected)
        self.assertDictEqual(text, expected)

        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': []}
        result = keep_layer(text, ['text'])        
        self.assertDictEqual(text, expected)

        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': [], 'words': [], 'sentences': []}
        result = keep_layer(text, ['words', 'sentences'])        
        self.assertDictEqual(result, expected)
        self.assertDictEqual(text, expected)

    def test_delete_layer(self):
        text = text_tok()
        self.assertTrue('words' in text)
        self.assertTrue('clauses' in text)
        processed_text = delete_layer(text, ['words', 'clauses'])
        self.assertEqual(text_delete_layer(), processed_text)

        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': [], 'words': [], 'sentences': []}
        result = delete_layer(text, [])        
        self.assertDictEqual(result, expected)
        self.assertDictEqual(text, expected)

        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': [], 'words': [], 'sentences': []}
        result = delete_layer(text, ['text'])        
        self.assertDictEqual(text, expected)

        text = {'text': [], 'words': [], 'sentences': []}
        expected = {'text': []}
        result = delete_layer(text, ['words', 'sentences'])        
        self.assertDictEqual(result, expected)
        self.assertDictEqual(text, expected)

    
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
    
    def test_get_text(self):
        text = Text('Üks kaks kolm neli.')
        result = get_text(text)        
        expected = 'Üks kaks kolm neli.'
        self.assertEqual(result, expected)

        result = get_text(text, start=4, end=8)        
        expected = 'kaks'
        self.assertEqual(result, expected)

        result = get_text(text, layer_element={'start':4, 'end':8})        
        self.assertEqual(result, expected)

        result = get_text(text, span=(4,8))        
        self.assertEqual(result, expected)

        result = get_text(text, start=5, end=7, marginal=1)        
        self.assertEqual(result, expected)

        result = get_text(text, start=4, end=8, marginal=20)        
        expected = 'Üks kaks kolm neli.'
        self.assertEqual(result, expected)
        
    def test_unique_texts(self):
        text = Text('Üks kaks kolm neli. Neli kolm kaks üks.')
        text.tokenize_words()

        result = unique_texts(text, 'words', sep=' ', order=None)
        expected = {'.', 'kaks', 'kolm', 'neli', 'Neli', 'üks', 'Üks'}
        self.assertSetEqual(set(result), expected)

        text = Text('Üks kaks kolm neli.')
        text.tokenize_words()
        
        result = unique_texts(text, 'words', sep=' ', order='asc')
        expected = ['.', 'kaks', 'kolm', 'neli', 'Üks']
        self.assertListEqual(result, expected)

        result = unique_texts(text, 'words', sep=' ', order='desc')
        expected = ['Üks', 'neli', 'kolm', 'kaks', '.']
        self.assertListEqual(result, expected)
        
    def test_count_by(self):
        text_1 = Text('Üks kaks kolm neli kaks.')
        text_1['test'] = [{'start': 0, 'end': 3, 'label':1}, 
                          {'start': 4, 'end': 8, 'label':2},
                          {'start': 9, 'end':13, 'label':3},
                          {'start':14, 'end':18, 'label':4},
                          {'start':19, 'end':23, 'label':2}]

        text_2 = Text('Neli kolm kaks üks kaks.')
        text_2['test'] = [{'start': 0, 'end': 4, 'label':4}, 
                          {'start': 5, 'end': 9, 'label':3},
                          {'start':10, 'end':14, 'label':2},
                          {'start':15, 'end':18, 'label':1},
                          {'start':19, 'end':23, 'label':2}]

        counter = count_by(text_1, 'test', 'label')
        expected = {(1,): 1, (2,): 2, (3,): 1, (4,): 1}
        self.assertDictEqual(counter, expected)
        counter = count_by(text_2, 'test', 'label', counter=counter)
        expected = {(1,): 2, (2,): 4, (3,): 2, (4,): 2}
        self.assertDictEqual(counter, expected)

        counter = count_by(text_1, 'test', ['text', 'label'])
        expected = {('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 1, ('neli', 4): 1}
        self.assertDictEqual(counter, expected)
        counter = count_by(text_2, 'test', ['text', 'label'], counter=counter)
        expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 4, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
        self.assertDictEqual(counter, expected)

    def test_count_by_document(self):
        text_1 = Text('Üks kaks kolm neli kaks.')
        text_1['test'] = [{'start': 0, 'end': 3, 'label':1}, 
                          {'start': 4, 'end': 8, 'label':2},
                          {'start': 9, 'end':13, 'label':3},
                          {'start':14, 'end':18, 'label':4},
                          {'start':19, 'end':23, 'label':2}]

        text_2 = Text('Neli kolm kaks üks kaks.')
        text_2['test'] = [{'start': 0, 'end': 4, 'label':4}, 
                          {'start': 5, 'end': 9, 'label':3},
                          {'start':10, 'end':14, 'label':2},
                          {'start':15, 'end':18, 'label':1},
                          {'start':19, 'end':23, 'label':2}]

        counter = count_by_document(text_1, 'test', 'label')
        expected = {(1,): 1, (2,): 1, (3,): 1, (4,): 1}
        self.assertDictEqual(counter, expected)
        counter = count_by_document(text_2, 'test', 'label', counter=counter)
        expected = {(1,): 2, (2,): 2, (3,): 2, (4,): 2}
        self.assertDictEqual(counter, expected)

        counter = count_by_document(text_1, 'test', ['text', 'label'])
        expected = {('Üks', 1): 1, ('kaks', 2): 1, ('kolm', 3): 1, ('neli', 4): 1}
        self.assertDictEqual(counter, expected)
        counter = count_by_document(text_2, 'test', ['text', 'label'], counter=counter)
        expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
        self.assertDictEqual(counter, expected)

    def test_dict_to_df(self):
        counter = {(2, 3): 4, (5, 6): 7}
        result = dict_to_df(counter, table_type='keyvalue', attributes=[0,1]).to_dict()
        expected = {0: {0: 5, 1: 2}, 1: {0: 6, 1: 3}, 'count': {0: 7, 1: 4}}
        self.assertDictEqual(result, expected)

        result = dict_to_df(counter, table_type='cross').to_dict()
        expected = {3: {2: 4.0, 5: 0.0}, 6: {2: 0.0, 5: 7.0}}
        self.assertDictEqual(result, expected)

    def test_diff_layer(self):
        a = []
        b = []
        result = list(diff_layer(a, b))
        expected = []
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end':  3}]
        b = []
        result = list(diff_layer(a, b))
        expected = [({'start': 0, 'end': 3}, None)]
        self.assertListEqual(result, expected)

        result = list(diff_layer(b, a))
        expected = [(None, {'start': 0, 'end': 3})]
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end':  3},
             {'start':  6, 'end':  9},
             {'start': 12, 'end': 15},
             {'start': 18, 'end': 21}]
        b = [{'start':  1, 'end':  3},
             {'start':  6, 'end':  9},
             {'start': 12, 'end': 15},
             {'start': 18, 'end': 20}]
        result = list(diff_layer(a, b))
        expected = [({'start':  0, 'end':  3}, None),
                    (None, {'start':  1, 'end':  3}),
                    (None, {'start': 18, 'end': 20}),
                    ({'start': 18, 'end': 21}, None)]
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end': 3, 'label':1}]
        b = [{'start':  0, 'end': 3, 'label':2}]
        result = list(diff_layer(a, b))
        expected = [({'start':  0, 'end': 3, 'label':1}, {'start':  0, 'end': 3, 'label':2})]
        self.assertListEqual(result, expected)
        
        a = [{'start':  0, 'end': 3, 'label':1},
             {'start':  5, 'end': 7, 'label':1}]
        b = [{'start':  0, 'end': 3, 'label':2},
             {'start':  6, 'end': 7, 'label':1}]
        def fun(x, y):
            return True
        result = list(diff_layer(a, b, fun))
        expected = [({'start':  5, 'end': 7, 'label':1}, None),
                    (None, {'start':  6, 'end': 7, 'label':1})]
        self.assertListEqual(result, expected)

    def test_merge_layer(self):
        def fun(x, y):
            if x == None:
                return y
            return x
        
        a = []
        b = []
        result = list(merge_layer(a, b, fun))
        expected = []
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end':  3}]
        b = []
        result = list(merge_layer(a, b, fun))
        expected = [{'start': 0, 'end': 3}]
        self.assertListEqual(result, expected)

        result = list(merge_layer(b, a, fun))
        expected = [{'start': 0, 'end': 3}]
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end':  3, 'label':1},
             {'start':  6, 'end':  9, 'label':2},
             {'start': 12, 'end': 15, 'label':3},
             {'start': 18, 'end': 21, 'label':4}]
        b = [{'start':  1, 'end':  3, 'label':5},
             {'start':  6, 'end':  9, 'label':6},
             {'start': 12, 'end': 15, 'label':7},
             {'start': 18, 'end': 20, 'label':8}]
        result = list(merge_layer(a, b, fun))
        expected = [{'start':  0, 'end':  3, 'label':1},
                    {'start':  1, 'end':  3, 'label':5},
                    {'start':  6, 'end':  9, 'label':2},
                    {'start': 12, 'end': 15, 'label':3},
                    {'start': 18, 'end': 20, 'label':8},
                    {'start': 18, 'end': 21, 'label':4}]
        self.assertListEqual(result, expected)
        
    def test_group_by_spans(self):
        def fun(duplicates):
            result = {}
            for d in duplicates:
                result.update(d)
            return result

        a = []
        result = list(group_by_spans(a, fun))
        expected = []
        self.assertListEqual(result, expected)

        a = [{'start':  0, 'end':  2, 'label':1},
             {'start':  0, 'end':  3, 'label':2},
             {'start':  0, 'end':  3, 'label':3},
             {'start':  0, 'end':  3, 'label':4},
             {'start':  0, 'end':  3, 'label':5},
             {'start':  6, 'end':  9, 'label':6},
             {'start':  6, 'end': 10, 'label':7},
             {'start': 18, 'end': 20, 'label':8},
             {'start': 18, 'end': 20, 'label':9}]
        result = list(group_by_spans(a, fun))
        expected = [{'start':  0, 'end':  2, 'label':1},
                    {'start':  0, 'end':  3, 'label':5},
                    {'start':  6, 'end':  9, 'label':6},
                    {'start':  6, 'end': 10, 'label':7},
                    {'start': 18, 'end': 20, 'label':9}]
        self.assertListEqual(result, expected)

    def test_conflicts(self):
        text = Text('Üks kaks kolm neli viis kuus seitse.')
                    #012345678901234567890123456789012345
                    #          1         2         3
        a = {}
        result = list(conflicts(text, a, multilayer=True))
        expected = []
        self.assertListEqual(result, expected)

        a = [{'start':  1, 'end':  3}, # S
             {'start':  4, 'end':  7}, # E
             {'start':  9, 'end': 18}, # O M
             {'start': 14, 'end': 23}, # O M
             {'start': 25, 'end': 33}, # S E O M
             {'start': 29, 'end': 35}] # O
        result = list(conflicts(text, a))
        expected = [{'start': [1], 'end': [3], 'syndrome': 'S'}, 
                    {'start': [4], 'end': [7], 'syndrome': 'E'}, 
                    {'start': [9, 14], 'end': [18, 23], 'syndrome': 'OM'}, 
                    {'start': [14, 9], 'end': [23, 18], 'syndrome': 'OM'}, 
                    {'start': [25, 29], 'end': [33, 35], 'syndrome': 'SEOM'}, 
                    {'start': [29, 25], 'end': [35, 33], 'syndrome': 'O'}]
        self.assertListEqual(result, expected)
 
        text = Text('Üks kaks')
                    #01234567
        a = [{'start':  0, 'end':  2}, # E O
             {'start':  1, 'end':  3}, # S O
             {'start':  4, 'end':  6}, # E O
             {'start':  5, 'end':  8}] # S O
        result = list(conflicts(text, a))
        expected = [{'start': [0, 1], 'end': [2, 3], 'syndrome': 'EO'}, 
                    {'start': [1, 0], 'end': [3, 2], 'syndrome': 'SO'}, 
                    {'start': [4, 5], 'end': [6, 8], 'syndrome': 'EO'}, 
                    {'start': [5, 4], 'end': [8, 6], 'syndrome': 'SO'}]
        self.assertListEqual(result, expected)

        a = [{'start':  1, 'end':  6}] # S E M
        result = list(conflicts(text, a, multilayer=False))
        expected = [{'start': 1, 'end': 6, 'syndrome': 'SEM'}]
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
