import pytest

from estnltk import AmbiguousSpan, Span, Layer
from estnltk.layer import AttributeList


def test_add_annotation():
    span_1 = AmbiguousSpan(Layer('test', attributes=['attr_1']), Span(0, 1))

    span_1.add_annotation(attr_1=0)
    span_1.add_annotation(attr_1=3)
    span_1.add_annotation(attr_1=3)

    assert len(span_1) == 2

    span_2 = AmbiguousSpan(Layer('test', attributes=['attr_1']), Span(0, 1))

    span_2.add_annotation(attr_1=3)
    span_2.add_annotation(attr_1=0)
    span_2.add_annotation(attr_1=0)
    span_2.add_annotation(attr_1=0)

    assert span_1 == span_2


def test_getattr():
    span_1 = AmbiguousSpan(Layer('test', attributes=['attr_1'], ambiguous=True), Span(0, 1))

    span_1.add_annotation(attr_1=0)
    span_1.add_annotation(attr_1=3)

    assert span_1.attr_1 == AttributeList([0, 3], 'attr_1')

    with pytest.raises(AttributeError):
        span_1.__getstate__
    with pytest.raises(AttributeError):
        span_1.__setstate__
    with pytest.raises(AttributeError):
        span_1._ipython_canary_method_should_not_exist_
    with pytest.raises(AttributeError):
        span_1.blabla

    assert hasattr(span_1, 'attr_1')
    assert not hasattr(span_1, 'blabla')
