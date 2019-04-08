from estnltk.tests import new_text
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk import Layer
from estnltk import Text
from estnltk import Span


def test_decompose_empty_text_empty_span():
    result = decompose_to_elementary_spans(new_text(1).layer_0, new_text(1).text)
    expected = [['', []]]
    assert result == expected


def test_decompose_text_with_empty_span():
    result = decompose_to_elementary_spans(new_text(1).layer_0, new_text(5).text)
    expected = [['Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.', []]]
    assert result == expected


def test_decompose_text_and_span():
    text_3 = Text('Tere, maailm!')
    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'], text_object=text_3)
    layer_0.add_annotation(Span(start=0, end=4), attr='L0-0', attr_0='A')
    layer_0.add_annotation(Span(start=4, end=5), attr='L0-1', attr_0='B')
    layer_0.add_annotation(Span(start=6, end=12), attr='L0-2', attr_0='C')
    layer_0.add_annotation(Span(start=12, end=13), attr='L0-3', attr_0='D')
    text_3['layer_0'] = layer_0

    expected = [['Tere', [layer_0[0]]],
                [',', [layer_0[1]]],
                [' ', []],
                ['maailm', [layer_0[2]]],
                ['!', [layer_0[3]]]]
    result = decompose_to_elementary_spans(layer_0, text_3.text)
    assert expected == result


def test_decompose_with_span_inside_another_span():
    t = 'Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.'
    text_5 = Text(t)

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text_5, ambiguous=True)
    layer_1.add_annotation(Span(start=0, end=4), attr='L1-0', attr_1='SADA')
    layer_1.add_annotation(Span(start=5, end=9), attr='L1-1', attr_1='KAKS')
    layer_1.add_annotation(Span(start=5, end=16), attr='L1-2', attr_1='KAKS')
    layer_1.add_annotation(Span(start=5, end=16), attr='L1-2', attr_1='KÜMME')
    layer_1.add_annotation(Span(start=5, end=16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_1.add_annotation(Span(start=9, end=14), attr='L1-3', attr_1='KÜMME')
    layer_1.add_annotation(Span(start=17, end=21), attr='L1-4', attr_1='KOLM')
    layer_1.add_annotation(Span(start=23, end=27), attr='L1-5', attr_1='NELI')
    layer_1.add_annotation(Span(start=28, end=33), attr='L1-6', attr_1='TUHAT')
    layer_1.add_annotation(Span(start=34, end=38), attr='L1-7', attr_1='VIIS')
    layer_1.add_annotation(Span(start=34, end=42), attr='L1-8', attr_1='SADA')
    layer_1.add_annotation(Span(start=34, end=42), attr='L1-8', attr_1='VIIS')
    layer_1.add_annotation(Span(start=34, end=42), attr='L1-8', attr_1='VIISSADA')
    layer_1.add_annotation(Span(start=38, end=42), attr='L1-9', attr_1='SADA')
    layer_1.add_annotation(Span(start=43, end=47), attr='L1-10', attr_1='KUUS')
    layer_1.add_annotation(Span(start=43, end=54), attr='L1-11', attr_1='KUUS')
    layer_1.add_annotation(Span(start=43, end=54), attr='L1-11', attr_1='KÜMME')
    layer_1.add_annotation(Span(start=43, end=54), attr='L1-11', attr_1='KUUSKÜMMEND')
    layer_1.add_annotation(Span(start=47, end=52), attr='L1-12', attr_1='KÜMME')
    layer_1.add_annotation(Span(start=55, end=61), attr='L1-13', attr_1='SEITSE')
    layer_1.add_annotation(Span(start=62, end=66), attr='L1-14', attr_1='KOMA')
    layer_1.add_annotation(Span(start=67, end=74), attr='L1-15', attr_1='KAHEKSA')
    layer_1.add_annotation(Span(start=76, end=82), attr='L1-16', attr_1='ÜHEKSA')
    layer_1.add_annotation(Span(start=76, end=89), attr='L1-17', attr_1='ÜHEKSA')
    layer_1.add_annotation(Span(start=76, end=89), attr='L1-17', attr_1='KÜMME')
    layer_1.add_annotation(Span(start=76, end=89), attr='L1-17', attr_1='ÜHEKSAKÜMMEND')
    layer_1.add_annotation(Span(start=82, end=87), attr='L1-18', attr_1='KÜMME')
    text_5['layer_1'] = layer_1

    layer = layer_1

    expected = [
        ['Sada', [layer[0]]],
        [' ', []],
        ['kaks', [layer[1], layer[2]]],
        ['kümme', [layer[2], layer[3]]],
        ['nd', [layer[2]]],
        [' ', []],
        ['kolm', [layer[4]]],
        ['. ', []],
        ['Neli', [layer[5]]],
        [' ', []],
        ['tuhat', [layer[6]]],
        [' ', []],
        ['viis', [layer[7], layer[8]]],
        ['sada', [layer[8], layer[9]]],
        [' ', []],
        ['kuus', [layer[10], layer[11]]],
        ['kümme', [layer[11], layer[12]]],
        ['nd', [layer[11]]],
        [' ', []],
        ['seitse', [layer[13]]],
        [' ', []],
        ['koma', [layer[14]]],
        [' ', []],
        ['kaheksa', [layer[15]]],
        ['. ', []],
        ['Üheksa', [layer[16], layer[17]]],
        ['kümme', [layer[17], layer[18]]],
        ['nd', [layer[17]]],
        [' tuhat.', []]]
    assert decompose_to_elementary_spans(layer, t) == expected


def test_decompose_spans_partially_overlap():
    text_3 = Text('Tere, maailm!')
    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'], text_object=text_3)
    layer_0.add_annotation(Span(start=0,  end=4),  attr='L0-0', attr_0='A')
    layer_0.add_annotation(Span(start=4,  end=8),  attr='L0-1', attr_0='B')
    layer_0.add_annotation(Span(start=6,  end=12), attr='L0-2', attr_0='C')
    layer_0.add_annotation(Span(start=10, end=13), attr='L0-3', attr_0='D')
    text_3['layer_0'] = layer_0

    result = decompose_to_elementary_spans(text_3.layer_0,text_3.text)
    expected = [['Tere', [layer_0[0]]],
                [', ', [layer_0[1]]],
                ['ma', [layer_0[1], layer_0[2]]],
                ['ai', [layer_0[2]]],
                ['lm', [layer_0[2], layer_0[3]]],
                ['!', [layer_0[3]]]]

    assert result == expected
