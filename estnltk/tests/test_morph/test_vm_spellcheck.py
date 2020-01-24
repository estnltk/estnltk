import pytest

from estnltk import Text
from estnltk import Annotation
from estnltk.taggers import SpellCheckRetagger
from estnltk.taggers import VabamorfAnalyzer

from estnltk.converters import dict_to_layer, layer_to_dict


def test_spellcheck_retagger_1():
    # Test SpellCheckRetagger on providing normalizations to misspelled words
    spelling_tagger=SpellCheckRetagger()
    # Case 1
    text=Text('Ma tahax minna järve äärde ja püda hauge, katikaid ja karpe.')
    text.tag_layer(['words'])
    spelling_tagger.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict(text.words))
    # Validate the results
    expected_layer_dict = \
    {'ambiguous': True,
     'attributes': ('normalized_form',),
     'enveloping': None,
     'meta': {},
     'name': 'words',
     'parent': None,
     'serialisation_module': None,
     'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 2)},
               {'annotations': [{'normalized_form': 'tahaks'},
                                {'normalized_form': 'taha'},
                                {'normalized_form': 'tahad'}],
                'base_span': (3, 8)},
               {'annotations': [{'normalized_form': None}], 'base_span': (9, 14)},
               {'annotations': [{'normalized_form': None}], 'base_span': (15, 20)},
               {'annotations': [{'normalized_form': None}], 'base_span': (21, 26)},
               {'annotations': [{'normalized_form': None}], 'base_span': (27, 29)},
               {'annotations': [{'normalized_form': 'püüda'}],
                'base_span': (30, 34)},
               {'annotations': [{'normalized_form': None}], 'base_span': (35, 40)},
               {'annotations': [{'normalized_form': None}], 'base_span': (40, 41)},
               {'annotations': [{'normalized_form': 'kaikaid'},
                                {'normalized_form': 'latikaid'},
                                {'normalized_form': 'karikaid'},
                                {'normalized_form': 'katikaiad'}],
                'base_span': (42, 50)},
               {'annotations': [{'normalized_form': None}], 'base_span': (51, 53)},
               {'annotations': [{'normalized_form': None}], 'base_span': (54, 59)},
               {'annotations': [{'normalized_form': None}], 'base_span': (59, 60)}]}
    assert text.words == dict_to_layer(expected_layer_dict)
    
    # Case 2
    text=Text('Metsawahi obusele on uus laut ehitet.')
    text.tag_layer(['words'])
    spelling_tagger.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict(text.words))
    # Validate the results
    expected_layer_dict = \
     {'ambiguous': True,
     'attributes': ('normalized_form',),
     'enveloping': None,
     'meta': {},
     'name': 'words',
     'parent': None,
     'serialisation_module': None,
     'spans': [{'annotations': [{'normalized_form': 'Metsavahi'},
                                {'normalized_form': 'Metsaahi'}],
                'base_span': (0, 9)},
               {'annotations': [{'normalized_form': 'hobusele'}],
                'base_span': (10, 17)},
               {'annotations': [{'normalized_form': None}], 'base_span': (18, 20)},
               {'annotations': [{'normalized_form': None}], 'base_span': (21, 24)},
               {'annotations': [{'normalized_form': None}], 'base_span': (25, 29)},
               {'annotations': [{'normalized_form': 'ehite'}],
                'base_span': (30, 36)},
               {'annotations': [{'normalized_form': None}], 'base_span': (36, 37)}]}
    assert text.words == dict_to_layer(expected_layer_dict)
    
    # Case 3: Add the original word.text to normalized_form
    spelling_tagger=SpellCheckRetagger(keep_original_word=True)
    text=Text('Metsawahi obusele on uus laut ehitet.')
    text.tag_layer(['words'])
    spelling_tagger.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict(text.words))
    # Validate the results
    expected_layer_dict = \
     {'ambiguous': True,
     'attributes': ('normalized_form',),
     'enveloping': None,
     'meta': {},
     'name': 'words',
     'parent': None,
     'serialisation_module': None,
     'spans': [{'annotations': [{'normalized_form': 'Metsavahi'},
                                {'normalized_form': 'Metsaahi'},
                                {'normalized_form': 'Metsawahi'}],
                'base_span': (0, 9)},
               {'annotations': [{'normalized_form': 'hobusele'},
                                {'normalized_form': 'obusele'},],
                'base_span': (10, 17)},
               {'annotations': [{'normalized_form': None}], 'base_span': (18, 20)},
               {'annotations': [{'normalized_form': None}], 'base_span': (21, 24)},
               {'annotations': [{'normalized_form': None}], 'base_span': (25, 29)},
               {'annotations': [{'normalized_form': 'ehite'},
                                {'normalized_form': 'ehitet'}],
                'base_span': (30, 36)},
               {'annotations': [{'normalized_form': None}], 'base_span': (36, 37)}]}
    assert text.words == dict_to_layer(expected_layer_dict)



def test_spellcheck_retagger_2():
    # Test SpellCheckRetagger on marking misspelled words and providing them normalizations
    spelling_tagger=SpellCheckRetagger(add_spellcheck=True)
    # Case 1
    text=Text('Ma tahax minna järve äärde ja püda hauge, katikaid ja karpe.')
    text.tag_layer(['words'])
    spelling_tagger.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict(text.words))
    # Validate the results
    expected_layer_dict = \
    {'ambiguous': True,
     'attributes': ('normalized_form', 'spelling'),
     'enveloping': None,
     'meta': {},
     'name': 'words',
     'parent': None,
     'serialisation_module': None,
     'spans': [{'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (0, 2)},
               {'annotations': [{'normalized_form': 'tahaks', 'spelling': False},
                                {'normalized_form': 'taha', 'spelling': False},
                                {'normalized_form': 'tahad', 'spelling': False}],
                'base_span': (3, 8)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (9, 14)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (15, 20)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (21, 26)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (27, 29)},
               {'annotations': [{'normalized_form': 'püüda', 'spelling': False}],
                'base_span': (30, 34)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (35, 40)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (40, 41)},
               {'annotations': [{'normalized_form': 'kaikaid', 'spelling': False},
                                {'normalized_form': 'latikaid', 'spelling': False},
                                {'normalized_form': 'karikaid', 'spelling': False},
                                {'normalized_form': 'katikaiad',
                                 'spelling': False}],
                'base_span': (42, 50)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (51, 53)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (54, 59)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (59, 60)}]}
    assert text.words == dict_to_layer(expected_layer_dict)
    
    # Case 2
    text=Text('Metsawahi obusele on uus laut ehitet.')
    text.tag_layer(['words'])
    spelling_tagger.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict(text.words))
    # Validate the results
    expected_layer_dict = \
    {'ambiguous': True,
     'attributes': ('normalized_form', 'spelling'),
     'enveloping': None,
     'meta': {},
     'name': 'words',
     'parent': None,
     'serialisation_module': None,
     'spans': [{'annotations': [{'normalized_form': 'Metsavahi', 'spelling': False},
                                {'normalized_form': 'Metsaahi', 'spelling': False}],
                'base_span': (0, 9)},
               {'annotations': [{'normalized_form': 'hobusele', 'spelling': False}],
                'base_span': (10, 17)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (18, 20)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (21, 24)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (25, 29)},
               {'annotations': [{'normalized_form': 'ehite', 'spelling': False}],
                'base_span': (30, 36)},
               {'annotations': [{'normalized_form': None, 'spelling': True}],
                'base_span': (36, 37)}]}
    assert text.words == dict_to_layer(expected_layer_dict)

