import pytest

from estnltk_core import Text
from estnltk_core.converters import text_to_dict, dict_to_text

from estnltk_core.tests import new_text

from estnltk_core.common import load_text_class


T_1 = "Tere, maailm!"
T_2 = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''

@pytest.mark.xfail(reason="TODO fix this")
def test_dict_export_import():
    text = Text('')
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text
    assert dict_text == text_to_dict(text_import)

    text = Text(T_2).tag_layer(['morph_analysis', 'paragraphs'])
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

