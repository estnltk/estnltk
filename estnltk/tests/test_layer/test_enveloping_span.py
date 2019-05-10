import pytest
from estnltk import EnvelopingSpan, Span, Layer, Text, Annotation


text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')

layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
layer_0.add_annotation(Span(start= 0, end= 4), attr='L0-0',  attr_0='100')
layer_0.add_annotation(Span(start= 5, end= 9), attr='L0-1',  attr_0='2')
layer_0.add_annotation(Span(start= 5, end=16), attr='L0-2',  attr_0='20')
layer_0.add_annotation(Span(start= 9, end=14), attr='L0-3',  attr_0='10')
layer_0.add_annotation(Span(start=17, end=21), attr='L0-4',  attr_0='3')
layer_0.add_annotation(Span(start=23, end=27), attr='L0-5',  attr_0='4')
layer_0.add_annotation(Span(start=28, end=33), attr='L0-6',  attr_0='1000')
layer_0.add_annotation(Span(start=34, end=38), attr='L0-7',  attr_0='5')
layer_0.add_annotation(Span(start=34, end=42), attr='L0-8',  attr_0='500')
layer_0.add_annotation(Span(start=38, end=42), attr='L0-9',  attr_0='100')
layer_0.add_annotation(Span(start=43, end=47), attr='L0-10', attr_0='6')
layer_0.add_annotation(Span(start=43, end=54), attr='L0-11', attr_0='60')
layer_0.add_annotation(Span(start=47, end=52), attr='L0-12', attr_0='10')
layer_0.add_annotation(Span(start=55, end=61), attr='L0-13', attr_0='7')
layer_0.add_annotation(Span(start=62, end=66), attr='L0-14', attr_0=',')
layer_0.add_annotation(Span(start=67, end=74), attr='L0-15', attr_0='8')
layer_0.add_annotation(Span(start=76, end=82), attr='L0-16', attr_0='9')
layer_0.add_annotation(Span(start=76, end=89), attr='L0-17', attr_0='90')
layer_0.add_annotation(Span(start=82, end=87), attr='L0-18', attr_0='10')
layer_0.add_annotation(Span(start=90, end=95), attr='L0-19', attr_0='1000')
text['layer_0'] = layer_0

layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_0')
layer_4.add_annotation([layer_0[0], layer_0[2], layer_0[4]], attr='L4-0', attr_4='123')
layer_4.add_annotation([layer_0[5], layer_0[6], layer_0[8], layer_0[11], layer_0[13]], attr='L4-1', attr_4='4567')
layer_4.add_annotation([layer_0[15]], attr='L4-2', attr_4='8')
layer_4.add_annotation([layer_0[14]], attr='L4-3', attr_4=',')
layer_4.add_annotation([layer_0[17], layer_0[19]], attr='L4-4', attr_4='90 000')
text['layer_4'] = layer_4


def new_enveloping_span():
    return EnvelopingSpan([layer_0[0], layer_0[2], layer_0[4]], layer=layer_4)


def test_enveloping_span():
    span = EnvelopingSpan([layer_0[0], layer_0[2], layer_0[4]], layer=layer_4)
    assert span.layer is layer_4
    assert span.parent is None


def test_annotations():
    span = EnvelopingSpan([layer_0[0], layer_0[2], layer_0[4]], layer=layer_4)
    assert span.annotations == []

    span.add_annotation(attr=0, attr_4=1)
    span.add_annotation(attr=0, attr_4=1)
    assert len(span.annotations) == 1

    span.add_annotation(attr=0, attr_4=2)
    assert len(span.annotations) == 2

    assert span.annotations[0] == Annotation(span, attr=0, attr_4=1)
    assert span.annotations[1] == Annotation(span, attr=0, attr_4=2)


def test_getitem():
    assert isinstance(layer_4[0], EnvelopingSpan)

    assert layer_4[0]['attr_4'] == '123'

    with pytest.raises(AttributeError):
        layer_4[0]['bla']
