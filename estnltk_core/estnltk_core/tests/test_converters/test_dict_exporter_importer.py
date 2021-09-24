import pytest

from estnltk_core import Text
from estnltk_core.converters import text_to_dict, dict_to_text

from estnltk_core.tests import new_text


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
