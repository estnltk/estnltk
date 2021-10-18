import pytest

from estnltk_core import Span, Layer, ElementaryBaseSpan
from estnltk_core.converters import text_to_json, json_to_text
from estnltk_core.converters import annotation_to_json, json_to_annotation
from estnltk_core.tests import new_text

from estnltk_core.common import load_text_class

T_1 = "Tere, maailm!"
T_2 = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''

@pytest.mark.xfail(reason='''TODO: needs to be fixed''')
def test_json_export_import():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('')
    json_text = text_to_json(text)
    text_import = json_to_text(json_text)
    assert text_import == text
    assert json_text == text_to_json(text_import)
    
    text = Text(T_2).tag_layer(['morph_analysis', 'paragraphs'])
    text.meta['year'] = 2017
    json_text = text_to_json(text)
    text_import = json_to_text(json_text)
    assert text_import == text, text.diff(text_import)
    # the following line randomly breaks in Python 3.5
    # assert json_text == text_to_json(text_import)

    text = Text(T_2)

    text = json_to_text(text_to_json(text))
    text.tag_layer(['tokens'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['compound_tokens'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['words'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['morph_analysis'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['sentences'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['paragraphs'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['morph_extended'])

    text = json_to_text(text_to_json(text))
    assert text == Text(T_2).tag_layer(['morph_extended', 'paragraphs'])


def test_annotation_json_export_import():
    layer = Layer('my_layer', attributes=['attr', 'attr_0'])
    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)

    annotation = new_text(5).layer_0[0].annotations[0]

    a = json_to_annotation(span, annotation_to_json(annotation))
    assert a == annotation
