from estnltk.tests import new_text
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk import Layer
from estnltk import Text


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
    layer_0.add_annotation(( 0,  4), attr='L0-0', attr_0='A')
    layer_0.add_annotation(( 4,  5), attr='L0-1', attr_0='B')
    layer_0.add_annotation(( 6, 12), attr='L0-2', attr_0='C')
    layer_0.add_annotation((12, 13), attr='L0-3', attr_0='D')
    text_3.add_layer(layer_0)

    expected = [['Tere', [0]],
                [',', [1]],
                [' ', []],
                ['maailm', [2]],
                ['!', [3]]]
    result = decompose_to_elementary_spans(layer_0, text_3.text)[0]
    assert expected == result


def test_decompose_with_span_inside_another_span():
    t = 'Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.'
    text_5 = Text(t)

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text_5, ambiguous=True)
    layer_1.add_annotation(( 0,  4), attr='L1-0', attr_1='SADA')
    layer_1.add_annotation(( 5,  9), attr='L1-1', attr_1='KAKS')
    layer_1.add_annotation(( 5, 16), attr='L1-2', attr_1='KAKS')
    layer_1.add_annotation(( 5, 16), attr='L1-2', attr_1='KÜMME')
    layer_1.add_annotation(( 5, 16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_1.add_annotation(( 9, 14), attr='L1-3', attr_1='KÜMME')
    layer_1.add_annotation((17, 21), attr='L1-4', attr_1='KOLM')
    layer_1.add_annotation((23, 27), attr='L1-5', attr_1='NELI')
    layer_1.add_annotation((28, 33), attr='L1-6', attr_1='TUHAT')
    layer_1.add_annotation((34, 38), attr='L1-7', attr_1='VIIS')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='SADA')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='VIIS')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='VIISSADA')
    layer_1.add_annotation((38, 42), attr='L1-9', attr_1='SADA')
    layer_1.add_annotation((43, 47), attr='L1-10', attr_1='KUUS')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KUUS')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KÜMME')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KUUSKÜMMEND')
    layer_1.add_annotation((47, 52), attr='L1-12', attr_1='KÜMME')
    layer_1.add_annotation((55, 61), attr='L1-13', attr_1='SEITSE')
    layer_1.add_annotation((62, 66), attr='L1-14', attr_1='KOMA')
    layer_1.add_annotation((67, 74), attr='L1-15', attr_1='KAHEKSA')
    layer_1.add_annotation((76, 82), attr='L1-16', attr_1='ÜHEKSA')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='ÜHEKSA')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='KÜMME')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='ÜHEKSAKÜMMEND')
    layer_1.add_annotation((82, 87), attr='L1-18', attr_1='KÜMME')
    text_5.add_layer(layer_1)

    layer = layer_1

    expected = [
        ['Sada', [0]],
        [' ', []],
        ['kaks', [1,2]],
        ['kümme', [2,3]],
        ['nd', [2]],
        [' ', []],
        ['kolm', [4]],
        ['. ', []],
        ['Neli', [5]],
        [' ', []],
        ['tuhat', [6]],
        [' ', []],
        ['viis', [7,8]],
        ['sada', [8,9]],
        [' ', []],
        ['kuus', [10,11]],
        ['kümme', [11,12]],
        ['nd', [11]],
        [' ', []],
        ['seitse', [13]],
        [' ', []],
        ['koma', [14]],
        [' ', []],
        ['kaheksa', [15]],
        ['. ', []],
        ['Üheksa', [16,17]],
        ['kümme', [17,18]],
        ['nd', [17]],
        [' tuhat.', []]]
    assert decompose_to_elementary_spans(layer, t)[0] == expected


def test_decompose_spans_partially_overlap():
    text_3 = Text('Tere, maailm!')
    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'], text_object=text_3)
    layer_0.add_annotation(( 0,  4), attr='L0-0', attr_0='A')
    layer_0.add_annotation(( 4,  8), attr='L0-1', attr_0='B')
    layer_0.add_annotation(( 6, 12), attr='L0-2', attr_0='C')
    layer_0.add_annotation((10, 13), attr='L0-3', attr_0='D')
    text_3.add_layer(layer_0)

    result = decompose_to_elementary_spans(text_3.layer_0,text_3.text)[0]
    expected = [['Tere', [0]],
                [', ', [1]],
                ['ma', [1,2]],
                ['ai', [2]],
                ['lm', [2,3]],
                ['!', [3]]]

    assert result == expected
