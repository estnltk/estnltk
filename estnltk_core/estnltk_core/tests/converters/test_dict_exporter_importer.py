import pytest

from estnltk_core import Text
from estnltk_core.converters import text_to_dict, dict_to_text
from estnltk_core.converters import dict_to_layer

from estnltk_core.tests import new_text

from estnltk_core.common import load_text_class


T_1 = "Tere, maailm!"
T_2 = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''

@pytest.mark.xfail(reason='''Text to dict checks that the text matches the available Text version in the system.
 Thus it gives an assertion error if you try to pass it estnltk_core Text but have estnltk installed''')
def test_dict_export_import():
    text = Text('')
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text
    assert dict_text == text_to_dict(text_import)

    text = Text(T_2)
    words_layer = dict_to_layer({'name': 'words',
     'attributes': ('normalized_form',),
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

