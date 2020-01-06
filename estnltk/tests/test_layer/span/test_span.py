import pytest

from estnltk import ElementaryBaseSpan, Span, Layer, Annotation
from estnltk.layer import AttributeList


def test_add_annotation():
    span_1 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert len(span_1.annotations) == 2

    span_2 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

    span_2.add_annotation(Annotation(span_2, attr_1=3))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))

    assert span_1 == span_2


def test_getattr():
    span_1 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert span_1.attr_1 == AttributeList([0, 3], 'attr_1')

    _ = span_1.__getstate__
    _ = span_1.__setstate__
    with pytest.raises(AttributeError):
        span_1._ipython_canary_method_should_not_exist_
    with pytest.raises(AttributeError):
        span_1.blabla

    assert hasattr(span_1, 'attr_1')
    assert not hasattr(span_1, 'blabla')


def test_getitem():
    span_1 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert isinstance(span_1.annotations[0], Annotation)
    assert span_1.annotations[0].attr_1 == 0
    assert span_1.annotations[1].attr_1 == 3

    assert span_1['attr_1'] == AttributeList([0, 3], 'attr_1')

    with pytest.raises(KeyError):
        span_1[:]

    with pytest.raises(KeyError):
        span_1['bla']

    with pytest.raises(KeyError):
        span_1[0]


def test_base_spans():
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=Layer('test', attributes=['attr_1'], ambiguous=True))

    assert ElementaryBaseSpan(0, 1) == span_1.base_span
