import pytest
from estnltk import Text, Layer, Span, Annotation


def test_annotation_without_span():
    annotation = Annotation(attr_1='üks', attr_2=2, attr_3='lambda a: 12 - 9')
    annotation_1 = Annotation(attr_1='üks', attr_2=2, attr_3='lambda a: 10 - 7', attr_4='4')
    annotation_2 = Annotation(attr_1='üks', attr_2=2, attr_3='lambda a: 10 - 7')
    annotation_3 = Annotation(attr_1='üks', attr_2=2, attr_3=4)

    assert annotation.span is None
    assert annotation.start is None
    assert annotation.end is None
    assert annotation.layer is None
    assert annotation.legal_attribute_names is None
    assert annotation.text_object is None
    assert annotation.text is None

    assert annotation == annotation
    assert annotation != annotation_1
    assert annotation == annotation_2
    assert annotation != annotation_3

    assert str(annotation) == "Annotation(None, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"
    assert repr(annotation) == "Annotation(None, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"

    span = Span(2, 6)
    annotation.span = span
    assert annotation.span is span
    with pytest.raises(AttributeError):
        annotation.span = span


def test_annotation_with_text_object():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(0, 4, layer=layer)
    annotation = Annotation(span=span, attr_1='üks', attr_2=2, attr_3='lambda a: 12 - 9')

    layer_1 = Layer('test_layer_1', attributes=['attr_3', 'attr_1', 'attr_2'], text_object=text)
    span_1 = Span(0, 4, layer=layer_1)
    annotation_1 = Annotation(span=span_1, attr_1='üks', attr_2=2, attr_3='lambda a: 12 - 9')

    layer_2 = Layer('test_layer_1', attributes=['attr_1', 'attr_2'], text_object=text)
    span_2 = Span(0, 4, layer=layer_2)
    annotation_2 = Annotation(span=span_2, attr_1='üks', attr_2=2)

    assert annotation.span is span

    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 2
    assert annotation.attr_3 == 3

    assert annotation.text_object is text

    with pytest.raises(AttributeError):
        annotation.bla

    with pytest.raises(AttributeError):
        del annotation.bla

    assert not annotation == 'Tere'
    assert annotation == annotation
    assert annotation == annotation_1
    assert annotation != annotation_2

    assert str(annotation) == "Annotation(Tere, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"
    assert repr(annotation) == "Annotation(Tere, {'attr_1': 'üks', 'attr_2': 2, 'attr_3': 3})"