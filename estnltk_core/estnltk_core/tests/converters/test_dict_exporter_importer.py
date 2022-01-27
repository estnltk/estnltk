import pytest

from estnltk_core.converters import text_to_dict, dict_to_text
from estnltk_core.converters import dict_to_layer, layer_to_dict
from estnltk_core.converters import layer_to_records
from estnltk_core.converters import records_to_layer

from estnltk_core.tests import new_text

from estnltk_core.common import load_text_class


T_1 = "Tere, maailm!"
T_2 = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''

def test_dict_export_import():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('')
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text
    assert dict_text == text_to_dict(text_import)

    text = Text(T_2)
    words_layer = dict_to_layer({'name': 'words',
     'attributes': ('normalized_form',),
     'secondary_attributes': (),
     'parent': None,
     'enveloping': None,
     'ambiguous': True,
     'serialisation_module': None,
     'meta': {},
     'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
      {'base_span': (4, 8), 'annotations': [{'normalized_form': None}]},
      {'base_span': (9, 15), 'annotations': [{'normalized_form': 'sadas'}]},
      {'base_span': (16, 19), 'annotations': [{'normalized_form': None}]},
      {'base_span': (20, 25), 'annotations': [{'normalized_form': None}]},
      {'base_span': (26, 32), 'annotations': [{'normalized_form': 'saia'}]},
      {'base_span': (32, 33), 'annotations': [{'normalized_form': None}]},
      {'base_span': (34, 39), 'annotations': [{'normalized_form': None}]},
      {'base_span': (40, 45), 'annotations': [{'normalized_form': None}]},
      {'base_span': (45, 46), 'annotations': [{'normalized_form': None}]},
      {'base_span': (48, 53), 'annotations': [{'normalized_form': None}]},
      {'base_span': (54, 58), 'annotations': [{'normalized_form': None}]},
      {'base_span': (58, 59), 'annotations': [{'normalized_form': None}]}]})
    text.add_layer(words_layer)
    text.meta['year'] = 2017
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text, text.diff(text_import)
    assert text_to_dict(text) == text_to_dict(dict_to_text(text_to_dict(text)))

    text = new_text(5)
    assert text == dict_to_text(text_to_dict(text))


def test_dict_export_import_simple():
    # Simple import/export of an existing Text, no tagging involved
    simple_text_dict = \
        {'layers': [{'ambiguous': False,
                     'attributes': (),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {},
                     'name': 'tokens',
                     'parent': None,
                     'serialisation_module': None,
                     'spans': [{'annotations': [{}], 'base_span': (0, 4)},
                               {'annotations': [{}], 'base_span': (4, 5)}]}],
         'meta': {'creation_date': '2021-06-10'},
         'text': 'Tere!'}
    text_obj = dict_to_text( simple_text_dict )
    assert isinstance( text_obj, load_text_class() )
    assert text_obj.layers == {'tokens'}
    assert text_obj.meta == {'creation_date': '2021-06-10'}
    new_text_dict = text_to_dict( text_obj )
    assert new_text_dict == simple_text_dict


def test_layer_to_records():
    # Case 1
    simple_text_dict = \
        {'layers': [{'ambiguous': False,
                     'attributes': (),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {'my_meta': 0},
                     'name': 'tokens',
                     'parent': None,
                     'serialisation_module': None,
                     'spans': [{'annotations': [{}], 'base_span': (0, 4)},
                               {'annotations': [{}], 'base_span': (4, 5)}]}],
         'meta': {},
         'text': 'Tere!'}
    text_obj = dict_to_text( simple_text_dict )
    assert layer_to_records( text_obj['tokens'], with_text=True ) == \
           [{'end': 4, 'start': 0, 'text': 'Tere'}, {'end': 5, 'start': 4, 'text': '!'}]
    # Case 2
    text = new_text(5)
    assert layer_to_records( text['layer_1'] ) == \
         [[{'attr': 'L1-0', 'attr_1': 'SADA', 'end': 4, 'start': 0}],
         [{'attr': 'L1-1', 'attr_1': 'KAKS', 'end': 9, 'start': 5}],
         [{'attr': 'L1-2', 'attr_1': 'KAKS', 'end': 16, 'start': 5},
          {'attr': 'L1-2', 'attr_1': 'KÜMME', 'end': 16, 'start': 5},
          {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND', 'end': 16, 'start': 5}],
         [{'attr': 'L1-3', 'attr_1': 'KÜMME', 'end': 14, 'start': 9}],
         [{'attr': 'L1-4', 'attr_1': 'KOLM', 'end': 21, 'start': 17}],
         [{'attr': 'L1-5', 'attr_1': 'NELI', 'end': 27, 'start': 23}],
         [{'attr': 'L1-6', 'attr_1': 'TUHAT', 'end': 33, 'start': 28}],
         [{'attr': 'L1-7', 'attr_1': 'VIIS', 'end': 38, 'start': 34}],
         [{'attr': 'L1-8', 'attr_1': 'SADA', 'end': 42, 'start': 34},
          {'attr': 'L1-8', 'attr_1': 'VIIS', 'end': 42, 'start': 34},
          {'attr': 'L1-8', 'attr_1': 'VIISSADA', 'end': 42, 'start': 34}],
         [{'attr': 'L1-9', 'attr_1': 'SADA', 'end': 42, 'start': 38}],
         [{'attr': 'L1-10', 'attr_1': 'KUUS', 'end': 47, 'start': 43}],
         [{'attr': 'L1-11', 'attr_1': 'KUUS', 'end': 54, 'start': 43},
          {'attr': 'L1-11', 'attr_1': 'KÜMME', 'end': 54, 'start': 43},
          {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND', 'end': 54, 'start': 43}],
         [{'attr': 'L1-12', 'attr_1': 'KÜMME', 'end': 52, 'start': 47}],
         [{'attr': 'L1-13', 'attr_1': 'SEITSE', 'end': 61, 'start': 55}],
         [{'attr': 'L1-14', 'attr_1': 'KOMA', 'end': 66, 'start': 62}],
         [{'attr': 'L1-15', 'attr_1': 'KAHEKSA', 'end': 74, 'start': 67}],
         [{'attr': 'L1-16', 'attr_1': 'ÜHEKSA', 'end': 82, 'start': 76}],
         [{'attr': 'L1-17', 'attr_1': 'ÜHEKSA', 'end': 89, 'start': 76},
          {'attr': 'L1-17', 'attr_1': 'KÜMME', 'end': 89, 'start': 76},
          {'attr': 'L1-17', 'attr_1': 'ÜHEKSAKÜMMEND', 'end': 89, 'start': 76}],
         [{'attr': 'L1-18', 'attr_1': 'KÜMME', 'end': 87, 'start': 82}]]


def test_records_to_layer():
    # Case 1
    simple_text_dict = \
        {'layers': [{'ambiguous': False,
                     'attributes': ('record_id', ),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {'my_meta': 0},
                     'name': 'tokens',
                     'parent': None,
                     'serialisation_module': None,
                     'spans': []}],
         'meta': {},
         'text': 'Tere!'}
    text_obj = dict_to_text( simple_text_dict )
    records = [{'end': 4, 'start': 0, 'text': 'Tere', 'record_id': 1}, 
               {'end': 5, 'start': 4, 'text': '!', 'record_id': 2}]
    records_to_layer( text_obj['tokens'], records )
    assert layer_to_dict( text_obj['tokens'] ) == \
        {'ambiguous': False,
         'attributes': ('record_id', ),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {'my_meta': 0},
         'name': 'tokens',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'record_id': 1}], 'base_span': (0, 4)},
                   {'annotations': [{'record_id': 2}], 'base_span': (4, 5)}]}
    # Case 2
    text = new_text(5)
    assert 'layer_6' not in text.layers
    text.add_layer( \
        dict_to_layer({'name': 'layer_6',
                       'attributes': ('attr', 'attr_1'),
                       'secondary_attributes': (),
                       'parent': None,
                       'enveloping': None,
                       'ambiguous': True,
                       'serialisation_module': None,
                       'meta': {},
                       'spans': []}) )
    records = \
         [[{'attr': 'L1-0', 'attr_1': 'SADA', 'end': 4, 'start': 0}],
         [{'attr': 'L1-1', 'attr_1': 'KAKS', 'end': 9, 'start': 5}],
         [{'attr': 'L1-2', 'attr_1': 'KAKS', 'end': 16, 'start': 5},
          {'attr': 'L1-2', 'attr_1': 'KÜMME', 'end': 16, 'start': 5},
          {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND', 'end': 16, 'start': 5}],
         [{'attr': 'L1-3', 'attr_1': 'KÜMME', 'end': 14, 'start': 9}],
         [{'attr': 'L1-4', 'attr_1': 'KOLM', 'end': 21, 'start': 17}],
         [{'attr': 'L1-5', 'attr_1': 'NELI', 'end': 27, 'start': 23}],
         [{'attr': 'L1-6', 'attr_1': 'TUHAT', 'end': 33, 'start': 28}],
         [{'attr': 'L1-7', 'attr_1': 'VIIS', 'end': 38, 'start': 34}],
         [{'attr': 'L1-8', 'attr_1': 'SADA', 'end': 42, 'start': 34},
          {'attr': 'L1-8', 'attr_1': 'VIIS', 'end': 42, 'start': 34},
          {'attr': 'L1-8', 'attr_1': 'VIISSADA', 'end': 42, 'start': 34}],
         [{'attr': 'L1-9', 'attr_1': 'SADA', 'end': 42, 'start': 38}],
         [{'attr': 'L1-10', 'attr_1': 'KUUS', 'end': 47, 'start': 43}],
         [{'attr': 'L1-11', 'attr_1': 'KUUS', 'end': 54, 'start': 43},
          {'attr': 'L1-11', 'attr_1': 'KÜMME', 'end': 54, 'start': 43},
          {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND', 'end': 54, 'start': 43}],
         [{'attr': 'L1-12', 'attr_1': 'KÜMME', 'end': 52, 'start': 47}],
         [{'attr': 'L1-13', 'attr_1': 'SEITSE', 'end': 61, 'start': 55}],
         [{'attr': 'L1-14', 'attr_1': 'KOMA', 'end': 66, 'start': 62}],
         [{'attr': 'L1-15', 'attr_1': 'KAHEKSA', 'end': 74, 'start': 67}],
         [{'attr': 'L1-16', 'attr_1': 'ÜHEKSA', 'end': 82, 'start': 76}],
         [{'attr': 'L1-17', 'attr_1': 'ÜHEKSA', 'end': 89, 'start': 76},
          {'attr': 'L1-17', 'attr_1': 'KÜMME', 'end': 89, 'start': 76},
          {'attr': 'L1-17', 'attr_1': 'ÜHEKSAKÜMMEND', 'end': 89, 'start': 76}],
         [{'attr': 'L1-18', 'attr_1': 'KÜMME', 'end': 87, 'start': 82}]]
    records_to_layer( text['layer_6'], records )
    for sid, layer_6_span in enumerate( text['layer_6'] ):
        assert layer_6_span == text['layer_1'][sid]
    
