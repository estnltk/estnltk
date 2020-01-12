import pytest

from estnltk import ElementaryBaseSpan, Span, Layer, Annotation


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
