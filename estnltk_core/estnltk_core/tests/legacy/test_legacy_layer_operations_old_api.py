#
#  Tests for legacy layer operations, relocated from:
#   https://github.com/estnltk/estnltk/blob/f2dbde4062cb103384b6949b722125543d3fe457/estnltk_core/estnltk_core/tests/test_layer_operations/test_layer_operations.py#L167-L496
#

from estnltk_core.common import load_text_class

from estnltk_core.legacy.layer_operations_old_api import conflicts
from estnltk_core.legacy.layer_operations_old_api import count_by_document
from estnltk_core.legacy.layer_operations_old_api import dict_to_df
from estnltk_core.legacy.layer_operations_old_api import group_by_spans


############################################################
####### TESTS BELOW USE THE OLD API  #######################
############################################################

def first_text():
    return 'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul maanteel tünjat Tallinnfilmi režissööri.'


def second_text():
    return 'Haapsalu (Läänemaa murrakutes varem ka Oablu või Aablu) on linn Eestis Läänemere ääres Haapsalu lahe ' \
           'lõunakaldal, Lääne maakonna halduskeskus. Linna territooriumi hulka kuulub Krimmi holm. Haapsalu ' \
           'linnapea on Urmas Sukles'


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
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text(first_text())
    text.tag_clauses().tag_named_entities()
    return text


def text_sentences():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text(first_text())
    text.sentences
    return text


def text_ner():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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


class TestLayerOperation():
    # TODO: fix
    def broken_test_apply_simple_filter_or(self):
        text = text_ner()
        assert ('named_entities' in text)
        assert ('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities', {'end': 44, 'label': 'LOC'}, 'OR')
        assert text_apply_layer_filter_or() == processed_text

    # TODO: fix
    def broken_test_apply_simple_filter_and(self):
        text = text_ner()
        assert ('named_entities' in text)
        assert ('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities', {'end': 182, 'label': 'LOC'}, 'AND')
        assert text_apply_layer_filter_and() == processed_text

    # TODO: fix
    def broken_test_apply_simple_filter_without_restriction(self):
        text = text_ner()
        assert ('named_entities' in text)
        assert ('text' in text)
        processed_text = apply_simple_filter(text, 'named_entities')
        assert text_apply_simple_filter_without_restriction() == processed_text

    # TODO: fix
    def broken_test_count_by_document(self):
        # Load Text or BaseText class (depending on the available packages)
        Text = load_text_class()
        
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
        assert counter == expected
        counter = count_by_document(text_2, 'test', 'label', counter=counter)
        expected = {(1,): 2, (2,): 2, (3,): 2, (4,): 2}
        assert counter == expected

        counter = count_by_document(text_1, 'test', ['text', 'label'])
        expected = {('Üks', 1): 1, ('kaks', 2): 1, ('kolm', 3): 1, ('neli', 4): 1}
        assert counter == expected
        counter = count_by_document(text_2, 'test', ['text', 'label'], counter=counter)
        expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
        assert counter == expected

    # TODO: fix or remove
    # broken in python 3.6
    def broken_test_dict_to_df(self):
        counter = {(2, 3): 4, (5, 6): 7}
        result = dict_to_df(counter, table_type='keyvalue', attributes=[0, 1]).to_dict()
        expected = {0: {0: 5, 1: 2}, 1: {0: 6, 1: 3}, 'count': {0: 7, 1: 4}}
        assert result == expected

        result = dict_to_df(counter, table_type='cross').to_dict()
        expected = {3: {2: 4.0, 5: 0.0}, 6: {2: 0.0, 5: 7.0}}
        assert result == expected

    def test_group_by_spans(self):
        def fun(duplicates):
            result = {}
            for d in duplicates:
                result.update(d)
            return result

        a = []
        result = list(group_by_spans(a, fun))
        expected = []
        assert result == expected

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
        assert result == expected

    # TODO: fix
    def broken_test_conflicts(self):
        # Load Text or BaseText class (depending on the available packages)
        Text = load_text_class()
        
        text = Text('Üks kaks kolm neli viis kuus seitse.')
                    #012345678901234567890123456789012345
                    #          1         2         3
        a = {}
        result = list(conflicts(text, a, multilayer=True))
        expected = []
        assert result == expected

        a = [{'start':  1, 'end':  3},  # S
             {'start':  4, 'end':  7},  # E
             {'start':  9, 'end': 18},  # O M
             {'start': 14, 'end': 23},  # O M
             {'start': 25, 'end': 33},  # S E O M
             {'start': 29, 'end': 35}]  # O
        result = list(conflicts(text, a))
        expected = [{'start': [1], 'end': [3], 'syndrome': 'S'}, 
                    {'start': [4], 'end': [7], 'syndrome': 'E'}, 
                    {'start': [9, 14], 'end': [18, 23], 'syndrome': 'OM'}, 
                    {'start': [14, 9], 'end': [23, 18], 'syndrome': 'OM'}, 
                    {'start': [25, 29], 'end': [33, 35], 'syndrome': 'SEOM'}, 
                    {'start': [29, 25], 'end': [35, 33], 'syndrome': 'O'}]
        assert result == expected

        text = Text('Üks kaks')
                    #01234567
        a = [{'start':  0, 'end':  2},  # E O
             {'start':  1, 'end':  3},  # S O
             {'start':  4, 'end':  6},  # E O
             {'start':  5, 'end':  8}]  # S O
        result = list(conflicts(text, a))
        expected = [{'start': [0, 1], 'end': [2, 3], 'syndrome': 'EO'}, 
                    {'start': [1, 0], 'end': [3, 2], 'syndrome': 'SO'}, 
                    {'start': [4, 5], 'end': [6, 8], 'syndrome': 'EO'}, 
                    {'start': [5, 4], 'end': [8, 6], 'syndrome': 'SO'}]
        assert result == expected

        a = [{'start': 1, 'end': 6}]  # S E M
        result = list(conflicts(text, a, multilayer=False))
        expected = [{'start': 1, 'end': 6, 'syndrome': 'SEM'}]
        assert result == expected
