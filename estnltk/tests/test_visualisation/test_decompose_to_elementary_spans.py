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
    #overlap at indexes 76-89 and 82-87
    expected = "[['Sada', [AS[Annotation(Sada, {'attr': 'L1-0', 'attr_1': 'SADA'})]]], [' ', []], ['kaks', [AS[Annotation(kaks, {'attr': 'L1-1', 'attr_1': 'KAKS'})], AS[Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKS'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KÜMME'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND'})]]], ['kümme', [AS[Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKS'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KÜMME'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND'})], AS[Annotation(kümme, {'attr': 'L1-3', 'attr_1': 'KÜMME'})]]], ['nd', [AS[Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKS'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KÜMME'}), Annotation(kakskümmend, {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND'})]]], [' ', []], ['kolm', [AS[Annotation(kolm, {'attr': 'L1-4', 'attr_1': 'KOLM'})]]], ['. ', []], ['Neli', [AS[Annotation(Neli, {'attr': 'L1-5', 'attr_1': 'NELI'})]]], [' ', []], ['tuhat', [AS[Annotation(tuhat, {'attr': 'L1-6', 'attr_1': 'TUHAT'})]]], [' ', []], ['viis', [AS[Annotation(viis, {'attr': 'L1-7', 'attr_1': 'VIIS'})], AS[Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'SADA'}), Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'VIIS'}), Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'VIISSADA'})]]], ['sada', [AS[Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'SADA'}), Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'VIIS'}), Annotation(viissada, {'attr': 'L1-8', 'attr_1': 'VIISSADA'})], AS[Annotation(sada, {'attr': 'L1-9', 'attr_1': 'SADA'})]]], [' ', []], ['kuus', [AS[Annotation(kuus, {'attr': 'L1-10', 'attr_1': 'KUUS'})], AS[Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUS'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KÜMME'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND'})]]], ['kümme', [AS[Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUS'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KÜMME'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND'})], AS[Annotation(kümme, {'attr': 'L1-12', 'attr_1': 'KÜMME'})]]], ['nd', [AS[Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUS'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KÜMME'}), Annotation(kuuskümmend, {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND'})]]], [' ', []], ['seitse', [AS[Annotation(seitse, {'attr': 'L1-13', 'attr_1': 'SEITSE'})]]], [' ', []], ['koma', [AS[Annotation(koma, {'attr': 'L1-14', 'attr_1': 'KOMA'})]]], [' ', []], ['kaheksa', [AS[Annotation(kaheksa, {'attr': 'L1-15', 'attr_1': 'KAHEKSA'})]]], ['. ', []], ['Üheksa', [AS[Annotation(Üheksa, {'attr': 'L1-16', 'attr_1': 'ÜHEKSA'})], AS[Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSA'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'KÜMME'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSAKÜMMEND'})]]], ['kümme', [AS[Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSA'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'KÜMME'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSAKÜMMEND'})], AS[Annotation(kümme, {'attr': 'L1-18', 'attr_1': 'KÜMME'})]]], ['nd', [AS[Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSA'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'KÜMME'}), Annotation(Üheksakümmend, {'attr': 'L1-17', 'attr_1': 'ÜHEKSAKÜMMEND'})]]], [' tuhat.', []]]"
    result = str(decompose_to_elementary_spans(new_text(5).layer_1,new_text(5).text))
    assert expected == result


def test_decompose_spans_partially_overlap():
    text_3 = Text('Tere, maailm!')
    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'], text_object=text_3)
    layer_0.add_span(Span(start=0, end=4, legal_attributes=['attr', 'attr_0'], attr='L0-0', attr_0='A'))
    layer_0.add_span(Span(start=4, end=8, legal_attributes=['attr', 'attr_0'], attr='L0-1', attr_0='B'))
    layer_0.add_span(Span(start=6, end=12, legal_attributes=['attr', 'attr_0'], attr='L0-2', attr_0='C'))
    layer_0.add_span(Span(start=10, end=13, legal_attributes=['attr', 'attr_0'], attr='L0-3', attr_0='D'))
    text_3['layer_0'] = layer_0

    result = str(decompose_to_elementary_spans(text_3.layer_0,text_3.text))
    expected = "[['Tere', [Span(start=0, end=4, text='Tere')]], [', ', [Span(start=4, end=8, text=', ma')]], ['ma', [Span(start=4, end=8, text=', ma'), Span(start=6, end=12, text='maailm')]], ['ai', [Span(start=6, end=12, text='maailm')]], ['lm', [Span(start=6, end=12, text='maailm'), Span(start=10, end=13, text='lm!')]], ['!', [Span(start=10, end=13, text='lm!')]]]"
    assert result == expected
