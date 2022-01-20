import pytest
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core import ElementaryBaseSpan, Span, Annotation
from estnltk_core.common import load_text_class

def test_annotation_without_span():
    annotation =   Annotation(None, attr_1='üks', attr_2=2, attr_3=3)
    annotation_1 = Annotation(None, attr_1='üks', attr_2=2, attr_3=3, attr_4='4')
    annotation_2 = Annotation(None, attr_1='üks', attr_2=2, attr_3=3)
    annotation_3 = Annotation(None, attr_1='üks', attr_2=2, attr_3=4)

    assert annotation.span is None
    assert annotation.start is None
    assert annotation.end is None
    assert annotation.layer is None
    assert annotation.legal_attribute_names is None
    assert annotation.text_object is None
    assert annotation.text is None
    assert len(annotation) == 3
    assert annotation.attr_1 == 'üks'
    assert annotation['attr_1'] == 'üks'
    assert annotation['attr_1', 'attr_3'] == ('üks', 3)

    assert 'attr_new' not in annotation
    annotation['attr_new'] = 'ÜKS'
    assert 'attr_new' in annotation
    assert annotation['attr_new'] == 'ÜKS'
    assert annotation.attr_new == 'ÜKS'
    annotation.attr_new = 'üks'
    assert annotation['attr_new'] == 'üks'
    del annotation['attr_new']
    assert 'attr_new' not in annotation

    with pytest.raises(KeyError):
        del annotation['attr_new']

    annotation.attr_new = 0
    del annotation.attr_new
    with pytest.raises(AttributeError):
        del annotation.attr_new

    with pytest.raises(KeyError):
        annotation['bla']

    with pytest.raises(TypeError):
        annotation[3]

    assert annotation == annotation
    assert annotation != annotation_1
    assert annotation == annotation_2
    assert annotation != annotation_3

    assert str(annotation) == "Annotation(None, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"
    assert repr(annotation) == "Annotation(None, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"

    span = Span(base_span=ElementaryBaseSpan(2, 6), layer=None)
    annotation.span = span
    assert annotation.span is span
    with pytest.raises(AttributeError):
        annotation.span = span

    assert Annotation(None, attr_1=1, attr_2=2) == Annotation(None, attr_1=1, attr_2=2)
    assert Annotation(None, attr_1=1, attr_2=2) != Annotation(None, attr_1=1, attr_2=22)
    assert Annotation(None, attr_1=1, attr_2=None) != Annotation(None, attr_1=1)

    with pytest.raises(AttributeError):
        annotation.__getstate__

    with pytest.raises(AttributeError):
        annotation.__setstate__

    #with pytest.raises(AttributeError):
    #    annotation.__deepcopy__


def test_annotation_with_text_object():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Tere!')
    layer = BaseLayer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, attr_1='üks', attr_2=2, attr_3=3)

    layer_1 = BaseLayer('test_layer_1', attributes=['attr_3', 'attr_1', 'attr_2'], text_object=text)
    span_1 = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer_1)
    annotation_1 = Annotation(span=span_1, attr_1='üks', attr_2=2, attr_3=3)

    layer_2 = BaseLayer('test_layer_1', attributes=['attr_1', 'attr_2'], text_object=text)
    span_2 = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer_2)
    annotation_2 = Annotation(span=span_2, attr_1='üks', attr_2=2)

    assert annotation.span is span

    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 2
    assert annotation.attr_3 == 3
    assert annotation['attr_1', 'attr_1'] == ('üks', 'üks')

    assert annotation.text_object is text

    annotation['span'] = 'span'
    annotation['start'] = 'start'
    annotation['end'] = 'emd'

    assert annotation.start == 0
    assert annotation.end == 4
    assert annotation.span is span

    assert annotation['span'] == 'span'
    assert annotation['start'] == 'start'
    assert annotation['end'] == 'emd'
    del annotation['span']
    del annotation['start']
    del annotation['end']

    with pytest.raises(AttributeError):
        annotation.bla

    with pytest.raises(AttributeError):
        del annotation.bla

    assert not annotation == 'Tere'
    assert annotation == annotation
    assert annotation == annotation_1
    assert annotation != annotation_2

    assert str(annotation) == "Annotation('Tere', {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"
    assert repr(annotation) == "Annotation('Tere', {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"

    assert str(annotation_1) == "Annotation('Tere', {'attr_3': 3, 'attr_1': 'üks', 'attr_2': 2})"
    assert repr(annotation_1) == "Annotation('Tere', {'attr_3': 3, 'attr_1': 'üks', 'attr_2': 2})"
