import pytest
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core import EnvelopingSpan, Annotation, EnvelopingBaseSpan
from estnltk_core.common import create_text_object

text = create_text_object('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')

layer_0 = BaseLayer('layer_0', attributes=['attr', 'attr_0'])
layer_0.add_annotation(( 0,  4), attr='L0-0',  attr_0='100')
layer_0.add_annotation(( 5,  9), attr='L0-1',  attr_0='2')
layer_0.add_annotation(( 5, 16), attr='L0-2',  attr_0='20')
layer_0.add_annotation(( 9, 14), attr='L0-3',  attr_0='10')
layer_0.add_annotation((17, 21), attr='L0-4',  attr_0='3')
layer_0.add_annotation((23, 27), attr='L0-5',  attr_0='4')
layer_0.add_annotation((28, 33), attr='L0-6',  attr_0='1000')
layer_0.add_annotation((34, 38), attr='L0-7',  attr_0='5')
layer_0.add_annotation((34, 42), attr='L0-8',  attr_0='500')
layer_0.add_annotation((38, 42), attr='L0-9',  attr_0='100')
layer_0.add_annotation((43, 47), attr='L0-10', attr_0='6')
layer_0.add_annotation((43, 54), attr='L0-11', attr_0='60')
layer_0.add_annotation((47, 52), attr='L0-12', attr_0='10')
layer_0.add_annotation((55, 61), attr='L0-13', attr_0='7')
layer_0.add_annotation((62, 66), attr='L0-14', attr_0=',')
layer_0.add_annotation((67, 74), attr='L0-15', attr_0='8')
layer_0.add_annotation((76, 82), attr='L0-16', attr_0='9')
layer_0.add_annotation((76, 89), attr='L0-17', attr_0='90')
layer_0.add_annotation((82, 87), attr='L0-18', attr_0='10')
layer_0.add_annotation((90, 95), attr='L0-19', attr_0='1000')
text.add_layer(layer_0)

layer_4 = BaseLayer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_0')
layer_4.add_annotation([layer_0[0], layer_0[2], layer_0[4]], attr='L4-0', attr_4='123')
layer_4.add_annotation([layer_0[5], layer_0[6], layer_0[8], layer_0[11], layer_0[13]], attr='L4-1', attr_4='4567')
layer_4.add_annotation([layer_0[15]], attr='L4-2', attr_4='8')
layer_4.add_annotation([layer_0[14]], attr='L4-3', attr_4=',')
layer_4.add_annotation([layer_0[17], layer_0[19]], attr='L4-4', attr_4='90 000')
text.add_layer(layer_4)


def test_enveloping_span():
    span = EnvelopingSpan(base_span=EnvelopingBaseSpan([layer_0[0].base_span,
                                                        layer_0[2].base_span,
                                                        layer_0[4].base_span]),
                          layer=layer_4)
    assert span.layer is layer_4
    assert span.parent is None


def test_annotations():
    span = EnvelopingSpan(base_span=EnvelopingBaseSpan([layer_0[0].base_span,
                                                        layer_0[2].base_span,
                                                        layer_0[4].base_span]),
                          layer=layer_4)
    assert span.annotations == []

    annotation = Annotation(span, attr=0, attr_4=1)
    span.add_annotation(annotation)
    span.add_annotation(annotation)
    assert len(span.annotations) == 1

    with pytest.raises(ValueError):
        annotation = Annotation(span, attr=0, attr_4=2)
        span.add_annotation(annotation)

    assert len(span.annotations) == 1
    assert span.annotations[0] == Annotation(span, attr=0, attr_4=1)


def test_getitem():
    assert isinstance(layer_4[0], EnvelopingSpan)

    assert layer_4[0]['attr_4'] == '123'

    with pytest.raises(KeyError):
        layer_4[0]['bla']
