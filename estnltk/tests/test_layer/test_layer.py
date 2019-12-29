import pytest

from estnltk import Text
from estnltk import Layer
from estnltk import ElementaryBaseSpan
from estnltk import Span
from estnltk import Annotation
from estnltk.layer import AmbiguousAttributeTupleList
from estnltk.layer import AmbiguousAttributeList
from estnltk.layer import AttributeTupleList
from estnltk.layer import AttributeList
from estnltk.tests import new_text
from estnltk.tests import example_text


def test_attributes_and_default_values():
    layer = Layer('test')
    assert () == layer.attributes
    assert {} == layer.default_values

    layer = Layer('test', attributes=['attr_1', 'attr_2'], default_values={'attr_2': 2})
    assert ('attr_1', 'attr_2') == layer.attributes
    assert {'attr_1': None, 'attr_2': 2} == layer.default_values
    layer.attributes = ['attr_1']
    assert {'attr_1': None} == layer.default_values
    layer.attributes = ['attr_1', 'attr_2']
    assert {'attr_1': None, 'attr_2': None} == layer.default_values
    assert ('attr_1', 'attr_2') == layer.attributes

    with pytest.raises(TypeError):
        layer.attributes = 3

    with pytest.raises(AssertionError):
        layer.attributes = ['1attr', '2attr']

    with pytest.raises(AssertionError):
        layer.attributes = ['attr_1', 'attr_2', 'attr_1']

    with pytest.raises(AssertionError):
        layer.attributes = ['3attr']

    assert ('attr_1', 'attr_2') == layer.attributes


def test_add_span():
    text = Text('0123456789')
    layer = Layer(name='ambiguous', attributes=['a', 'b', 'c'], ambiguous=True)

    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    layer.add_span(span)

    span = Span(base_span=ElementaryBaseSpan(1, 2), layer=layer)
    span.add_annotation(Annotation(span, a='s2', b=False, c=5))
    span.add_annotation(Annotation(span, a='s4', b=False, c=5))
    layer.add_span(span)

    span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    span.add_annotation(Annotation(span, a='s3', b=True, c=None))
    layer.add_span(span)

    text.add_layer(layer)

    assert len(layer) == 3
    assert isinstance(layer[0], Span)
    assert isinstance(layer[1], Span)
    assert isinstance(layer[2], Span)
    assert len(layer[0].annotations) == 1
    assert len(layer[1].annotations) == 1
    assert len(layer[2].annotations) == 2

    layer = Layer(name='ambiguous', attributes=['a', 'b', 'c'], ambiguous=False)

    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    layer.add_span(span)

    span = Span(base_span=ElementaryBaseSpan(1, 2), layer=layer)
    span.add_annotation(Annotation(span, a='s2', b=False, c=5))
    layer.add_span(span)

    span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    span.add_annotation(Annotation(span, a='s3', b=True, c=None))
    layer.add_span(span)

    with pytest.raises(ValueError):
        span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
        span.add_annotation(Annotation(span, a='s1', b=True, c=None))
        layer.add_span(span)

    with pytest.raises(ValueError):
        span = Span(base_span=ElementaryBaseSpan(1, 2), layer=layer)
        span.add_annotation(Annotation(span, a='s4', b=False, c=5))
        layer.add_span(span)

    assert len(layer) == 3
    assert isinstance(layer[0], Span)
    assert isinstance(layer[1], Span)
    assert isinstance(layer[2], Span)


def test_add_annotation():
    # layer_0
    layer_0 = Layer('layer_0', attributes=['attr_1', 'attr_2'], parent=None, enveloping=None, ambiguous=False)
    assert len(layer_0) == 0
    layer_0.add_annotation(ElementaryBaseSpan(10, 11), attr_1=11)
    assert len(layer_0) == 1
    assert layer_0[0].annotations == [Annotation(None, attr_1=11, attr_2=None)]
    with pytest.raises(ValueError):
        layer_0.add_annotation(ElementaryBaseSpan(10, 11), attr_1=111)

    layer_0.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_0) == 2
    assert layer_0[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # layer_1
    layer_1 = Layer('layer_1', attributes=['attr_1', 'attr_2'], parent=None, enveloping=None, ambiguous=True)
    assert len(layer_1) == 0
    layer_1.add_annotation(ElementaryBaseSpan(10, 11), attr_1=11)
    assert len(layer_1) == 1
    assert layer_1[0].annotations == [Annotation(None, attr_1=11, attr_2=None)]

    layer_1.add_annotation(ElementaryBaseSpan(10, 11), attr_1=111)
    assert layer_1[0].annotations == [Annotation(None, attr_1=11, attr_2=None), Annotation(None, attr_1=111, attr_2=None)]

    layer_1.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_1) == 2
    assert layer_1[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # layer_2
    layer_2 = Layer('layer_2', attributes=['attr_1', 'attr_2'], parent='layer_0', enveloping=None, ambiguous=False)
    assert len(layer_2) == 0
    layer_2.add_annotation(layer_0[1], attr_1=2)
    assert len(layer_2) == 1
    assert layer_2[0].annotations == [Annotation(None, attr_1=2, attr_2=None)]
    with pytest.raises(ValueError):
        layer_2.add_annotation(layer_0[1], attr_1=111)

    layer_2.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_2) == 2
    assert layer_2[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # TODO: continue with all layer types


def test_layer_indexing():
    t = Text("0123456789")
    layer = Layer(name='base',
                  attributes=['a', 'b', 'c'],
                  default_values={'a': 'default a', 'b': 'default b', 'c': 'default c'},
                  ambiguous=False)

    layer.add_annotation((0, 1), a=1, b=11, c=21)
    layer.add_annotation((1, 2), a=2, b=12)
    layer.add_annotation((2, 3), a=3)
    layer.add_annotation((3, 4))
    layer.add_annotation((4, 5), a=5, b=15, c=25)
    layer.add_annotation((5, 6), a=6, b=16, c=None)
    layer.add_annotation((6, 7), a=7, b=None, c=None)
    layer.add_annotation((7, 8), a=None, b=None, c=None)
    t.add_layer(layer)

    span_2 = layer[2]
    assert isinstance(span_2, Span)
    assert span_2.text == '2'
    assert span_2.a == 3
    assert span_2.b == 'default b'
    assert span_2.c == 'default c'

    assert isinstance(layer['a'], AttributeList)
    assert isinstance(layer.a, AttributeList)
    assert layer['a'] == layer.a
    assert isinstance(layer['b'], AttributeList)
    assert isinstance(layer.b, AttributeList)
    assert layer['b'] == layer.b
    assert isinstance(layer['c'], AttributeList)
    assert isinstance(layer.c, AttributeList)
    assert layer['c'] == layer.c

    assert len(layer['a']) == 8
    assert len(layer['b']) == 8
    assert len(layer['c']) == 8

    assert isinstance(layer['a', 'b'], AttributeTupleList)
    assert isinstance(layer[['a', 'b']], AttributeTupleList)
    assert layer['a', 'b'] == layer[['a', 'b']]
    assert layer['a', 'b'] == layer[('a', 'b')]
    assert len(layer[['a', 'b']]) == 8
    assert isinstance(layer[['a']], AttributeTupleList)
    assert layer['a'] != layer[['a']]
    assert len(layer[['a']]) == 8

    atl = t.base['a', 'b']
    t.pop_layer('base')
    assert atl == AttributeTupleList([[1, 11],
                                      [2, 12],
                                      [3, 'default b'],
                                      ['default a', 'default b'],
                                      [5, 15],
                                      [6, 16],
                                      [7, None],
                                      [None, None]],
                                     ('a', 'b'))


def test_ambiguous_layer_indexing():
    t = Text("0123456789")
    layer = Layer(name='base',
                  attributes=['a', 'b', 'c'],
                  text_object=t,
                  default_values={'a': 'default a', 'b': 'default b'},
                  ambiguous=True)
    layer.add_annotation((0, 1), a=1, b=11, c=21)
    layer.add_annotation((0, 1), a=1, b=11, c=21)
    layer.add_annotation((1, 2), a=2, b=12)
    layer.add_annotation((1, 2), a=2, b=123)
    layer.add_annotation((2, 3), a=3)
    layer.add_annotation((3, 4))
    layer.add_annotation((3, 4), a=4, b=None)
    layer.add_annotation((4, 5), a=5, b=15, c=25)
    layer.add_annotation((5, 6), a=6, b=16, c=None)
    layer.add_annotation((6, 7), a=7, b=None, c=None)
    layer.add_annotation((7, 8), a=None, b=None, c=None)
    layer.add_annotation((7, 8), a=None, b=None, c=None)
    t.add_layer(layer)

    span_3 = layer[3]
    assert isinstance(span_3, Span)
    assert len(span_3.annotations) == 2
    assert isinstance(span_3.annotations[0], Annotation)
    assert span_3.annotations[0].text == '3'
    assert span_3.annotations[0].a == 'default a'
    assert span_3.annotations[0].b == 'default b'
    assert span_3.annotations[0].c is None
    assert span_3.annotations[1].text == '3'
    assert span_3.annotations[1].a == 4
    assert span_3.annotations[1].b is None
    assert span_3.annotations[1].c is None

    assert isinstance(layer['a'], AmbiguousAttributeList)
    assert isinstance(layer.a, AmbiguousAttributeList)
    assert layer['a'] == layer.a
    assert isinstance(layer['b'], AmbiguousAttributeList)
    assert isinstance(layer.b, AmbiguousAttributeList)
    assert layer['b'] == layer.b
    assert isinstance(layer['c'], AmbiguousAttributeList)
    assert isinstance(layer.c, AmbiguousAttributeList)
    assert layer['c'] == layer.c

    assert len(layer['a']) == 8
    assert len(layer['b']) == 8
    assert len(layer['c']) == 8

    assert isinstance(layer['a', 'b'], AmbiguousAttributeTupleList)
    assert isinstance(layer[['a', 'b']], AmbiguousAttributeTupleList)
    assert layer['a', 'b'] == layer[['a', 'b']]
    assert len(layer[['a', 'b']]) == 8
    assert isinstance(layer[['a']], AmbiguousAttributeTupleList)
    assert layer['a'] != layer[['a']]
    assert len(layer[['a']]) == 8


def test_advanced_indexing():
    text = Text('Mis on Sinu nimi?').analyse('morphology')
    layer = text.morph_analysis

    assert layer[:] == layer
    assert layer[2:10:2].text == ['Sinu', '?']
    assert layer[[True, False, True, False, True]].text == ['Mis', 'Sinu', '?']
    assert layer[lambda span: len(span.annotations) > 1].text == ['Mis', 'on']
    assert layer[[1, 3, 4]].text == ['on', 'nimi', '?']

    assert layer[:]['text', 'lemma'] == layer[['text', 'lemma']]
    assert layer[2:10:2, ['text', 'lemma']] == layer[2:10:2]['text', 'lemma']
    assert layer[[True, False, True, False, True], ['text', 'lemma']] == layer[True, False, True, False, True][
        'text', 'lemma']
    assert layer[lambda span: len(span.annotations) > 1,
                 ['text', 'lemma']] == layer[lambda span: len(span.annotations) > 1]['text', 'lemma']
    assert layer[[1, 3, 4], ['text', 'lemma']] == layer[[1, 3, 4]]['text', 'lemma']
    assert list(layer[0, 'lemma']) == ['mis', 'mis']
    assert list(layer[0, ['lemma', 'form']][0]) == ['mis', 'pl n']
    assert list(layer[0, ['lemma', 'form']][1]) == ['mis', 'sg n']
    with pytest.raises(IndexError):
        layer[[]]


def test_check_layer_consistency():
    other_morph_layer = \
        Text('Kas?').analyse('morphology')['morph_analysis']
    text = Text('Kes ja kus?').analyse('morphology')
    morph_layer = text['morph_analysis']

    # 1) Change first span, assign it to different layer
    old_first_span = morph_layer.spans[0]
    morph_layer.spans[0] = Span(base_span=old_first_span.base_span, layer=other_morph_layer)
    with pytest.raises(AssertionError) as e1:
        # Assertion error because the Span is connected
        # to different layer
        morph_layer.check_span_consistency()
    morph_layer.spans[0] = old_first_span
    morph_layer.check_span_consistency()

    # 2) Add element with duplicate location to the list
    morph_layer.spans.append(old_first_span)
    with pytest.raises(AssertionError) as e2:
        # Assertion error because span with duplicate location
        # exists
        morph_layer.check_span_consistency()
    morph_layer.spans.pop()
    morph_layer.check_span_consistency()

    # 3) Set span without annotations
    morph_layer.spans[0] = Span(old_first_span.base_span, old_first_span.layer)
    with pytest.raises(AssertionError) as e3:
        # Assertion error because the first span has no annotations
        morph_layer.check_span_consistency()
    morph_layer.spans[0] = old_first_span
    morph_layer.check_span_consistency()

    # 4) Layer with missing attributes
    layer1 = Layer(name='test_layer1',
                   attributes=['a', 'b', 'c'],
                   ambiguous=True)
    layer1.add_annotation((0, 1))
    assert layer1[0].annotations[0].a is None
    assert layer1[0].annotations[0].b is None
    assert layer1[0].annotations[0].c is None
    layer1.check_span_consistency()
    del layer1[0].annotations[0].b
    with pytest.raises(AssertionError) as e4:
        # Assertion error because layer's Annotation had missing attributes
        layer1.check_span_consistency()
    # print(e4)

    # 5) Layer with redundant attributes
    layer1 = Layer(name='test_layer1',
                   attributes=['a'],
                   ambiguous=True)
    layer2 = Layer(name='test_layer2',
                   attributes=['a', 'b'],
                   ambiguous=True)
    amb_span1 = Span(ElementaryBaseSpan(0, 1), layer=layer1)
    amb_span2 = Span(ElementaryBaseSpan(0, 1), layer=layer2)
    broken_annotation = Annotation(amb_span2)
    for attr in ['a', 'b', 'c']:
        setattr(broken_annotation, attr, '')
    amb_span1.annotations.append(broken_annotation)
    layer1.spans.append(amb_span1)
    with pytest.raises(AssertionError) as e5:
        # Assertion error because layer's Annotation had redundant attr
        layer1.check_span_consistency()

    # B1) Check for missing Span attributes
    layer = Layer(name='test_layer',
                  attributes=['a', 'b', 'c'],
                  ambiguous=False)
    span1 = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span1.add_annotation(Annotation(span1, a=1, b=11, c=None))
    del span1.annotations[0].c

    span2 = Span(base_span=ElementaryBaseSpan(1, 2), layer=layer)
    span2.add_annotation(Annotation(span2, a=None, b=11, c=21))
    del span2.annotations[0].a

    layer.spans.append(span1)
    layer.spans.append(span2)
    with pytest.raises(AssertionError) as ex1:
        # Assertion error because Span misses some legal attributes
        layer.check_span_consistency()
    del layer.spans[-1]
    del layer.spans[-1]
    # print(ex1)

    # B2) Check for redundant Span attributes
    span3 = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span3.add_annotation(Annotation(span3, a=1, b=11, c=0))
    span3.annotations[0].d = 12

    layer.spans.append(span3)
    with pytest.raises(AssertionError) as ex2:
        # assertion error because annotation of the span3 has a redundant attribute
        layer.check_span_consistency()


def test_count_values():
    assert new_text(1).layer_5.count_values('attr') == {}

    assert new_text(5).layer_0.count_values('attr_0') == {',': 1,
                                                          '10': 3,
                                                          '100': 2,
                                                          '1000': 2,
                                                          '2': 1,
                                                          '20': 1,
                                                          '3': 1,
                                                          '4': 1,
                                                          '5': 1,
                                                          '500': 1,
                                                          '6': 1,
                                                          '60': 1,
                                                          '7': 1,
                                                          '8': 1,
                                                          '9': 1,
                                                          '90': 1}

    assert new_text(5).layer_1.count_values('attr_1') == {'KAHEKSA': 1,
                                                          'KAKS': 2,
                                                          'KAKSKÜMMEND': 1,
                                                          'KOLM': 1,
                                                          'KOMA': 1,
                                                          'KUUS': 2,
                                                          'KUUSKÜMMEND': 1,
                                                          'KÜMME': 6,
                                                          'NELI': 1,
                                                          'SADA': 3,
                                                          'SEITSE': 1,
                                                          'TUHAT': 1,
                                                          'VIIS': 2,
                                                          'VIISSADA': 1,
                                                          'ÜHEKSA': 2,
                                                          'ÜHEKSAKÜMMEND': 1}


def test_groupby():
    result = example_text(5).layer_1.groupby(['attr_1']).groups
    for key in result:
        result[key] = [sp.text for sp in result[key]]
    assert result == {('KAHEKSA',): ['kaheksa'],
                      ('KAKS',): ['kaks', 'kakskümmend'],
                      ('KAKSKÜMMEND',): ['kakskümmend'],
                      ('KOLM',): ['kolm'],
                      ('KOMA',): ['koma'],
                      ('KUUS',): ['kuus', 'kuuskümmend'],
                      ('KUUSKÜMMEND',): ['kuuskümmend'],
                      ('KÜMME',): ['kakskümmend',
                                   'kümme',
                                   'kuuskümmend',
                                   'kümme',
                                   'Üheksakümmend',
                                   'kümme'],
                      ('NELI',): ['Neli'],
                      ('SADA',): ['Sada', 'viissada', 'sada'],
                      ('SEITSE',): ['seitse'],
                      ('TUHAT',): ['tuhat'],
                      ('VIIS',): ['viis', 'viissada'],
                      ('VIISSADA',): ['viissada'],
                      ('ÜHEKSA',): ['Üheksa', 'Üheksakümmend'],
                      ('ÜHEKSAKÜMMEND',): ['Üheksakümmend']}

    result = example_text(5).layer_0.groupby(['attr', 'attr_0']).groups
    for key in result:
        result[key] = [sp.text for sp in result[key]]
    assert result == {('L0-0', '100'): ['Sada'],
                      ('L0-1', '2'): ['kaks'],
                      ('L0-10', '6'): ['kuus'],
                      ('L0-11', '60'): ['kuuskümmend'],
                      ('L0-12', '10'): ['kümme'],
                      ('L0-13', '7'): ['seitse'],
                      ('L0-14', ','): ['koma'],
                      ('L0-15', '8'): ['kaheksa'],
                      ('L0-16', '9'): ['Üheksa'],
                      ('L0-17', '90'): ['Üheksakümmend'],
                      ('L0-18', '10'): ['kümme'],
                      ('L0-19', '1000'): ['tuhat'],
                      ('L0-2', '20'): ['kakskümmend'],
                      ('L0-3', '10'): ['kümme'],
                      ('L0-4', '3'): ['kolm'],
                      ('L0-5', '4'): [' Neli'],
                      ('L0-6', '1000'): ['tuhat'],
                      ('L0-7', '5'): ['viis'],
                      ('L0-8', '500'): ['viissada'],
                      ('L0-9', '100'): ['sada']}

    groups = example_text(5).layer_1.groupby(['attr'], return_type='annotations').groups
    result = {}
    for key in groups:
        result[key] = [sp.text for sp in groups[key]]
    assert result == {('L1-0',): ['Sada'],
                      ('L1-1',): ['kaks'],
                      ('L1-10',): ['kuus'],
                      ('L1-11',): ['kuuskümmend', 'kuuskümmend', 'kuuskümmend'],
                      ('L1-12',): ['kümme'],
                      ('L1-13',): ['seitse'],
                      ('L1-14',): ['koma'],
                      ('L1-15',): ['kaheksa'],
                      ('L1-16',): ['Üheksa'],
                      ('L1-17',): ['Üheksakümmend', 'Üheksakümmend', 'Üheksakümmend'],
                      ('L1-18',): ['kümme'],
                      ('L1-2',): ['kakskümmend', 'kakskümmend', 'kakskümmend'],
                      ('L1-3',): ['kümme'],
                      ('L1-4',): ['kolm'],
                      ('L1-5',): ['Neli'],
                      ('L1-6',): ['tuhat'],
                      ('L1-7',): ['viis'],
                      ('L1-8',): ['viissada', 'viissada', 'viissada'],
                      ('L1-9',): ['sada']}

    result = example_text(5).layer_0.groupby(['attr', 'attr_0'], return_type='annotations').groups
    for key in result:
        result[key] = [sp.text for sp in result[key]]
    assert result == {('L0-0', '100'): ['Sada'],
                      ('L0-1', '2'): ['kaks'],
                      ('L0-10', '6'): ['kuus'],
                      ('L0-11', '60'): ['kuuskümmend'],
                      ('L0-12', '10'): ['kümme'],
                      ('L0-13', '7'): ['seitse'],
                      ('L0-14', ','): ['koma'],
                      ('L0-15', '8'): ['kaheksa'],
                      ('L0-16', '9'): ['Üheksa'],
                      ('L0-17', '90'): ['Üheksakümmend'],
                      ('L0-18', '10'): ['kümme'],
                      ('L0-19', '1000'): ['tuhat'],
                      ('L0-2', '20'): ['kakskümmend'],
                      ('L0-3', '10'): ['kümme'],
                      ('L0-4', '3'): ['kolm'],
                      ('L0-5', '4'): [' Neli'],
                      ('L0-6', '1000'): ['tuhat'],
                      ('L0-7', '5'): ['viis'],
                      ('L0-8', '500'): ['viissada'],
                      ('L0-9', '100'): ['sada']}


def test_copy():
    layer = Layer('test')
    layer_copy = layer.copy()
    assert layer == layer_copy
    assert layer is not layer_copy

    text = new_text(5)

    layer = text['layer_1']
    layer_copy = layer.copy()

    assert layer_copy == layer
    assert layer_copy.attributes == layer.attributes
    # the tuple of attribute names is not copied
    assert layer_copy.attributes is layer.attributes
    layer_copy.attributes = [*layer_copy.attributes, 'new_attribute']
    assert layer_copy.attributes != layer.attributes
    layer_copy.attributes = layer_copy.attributes[:-1]
    assert layer_copy.attributes == layer.attributes
    assert layer_copy.attributes is not layer.attributes

    assert layer_copy == layer
    assert layer_copy.default_values == layer.default_values
    assert layer_copy.default_values is not layer.default_values
    layer_copy.default_values['new_attribute'] = 13
    assert layer_copy.default_values != layer.default_values
    del layer_copy.default_values['new_attribute']
    assert layer_copy.default_values == layer.default_values

    # list of spans is copied
    assert layer_copy == layer
    span = layer_copy[0]
    del layer_copy[0]
    assert layer_copy != layer
    layer_copy.add_span(span)

    # list of annotations is copied
    assert layer == layer_copy
    layer_copy.add_annotation(layer_copy[0].base_span, attr='L1-2',  attr_1='kümme')
    assert layer_copy != layer
    del layer_copy[0].annotations[-1]

    # annotations are copied
    assert layer == layer_copy
    layer_copy[0].annotations[0].attr_0 = '101'
    assert layer_copy != layer
    layer_copy[0].annotations[0].attr_0 = '100'


def test_ancestor_layers():
    text = Text('')

    layer_1 = Layer('layer_1', text_object=text)
    layer_2 = Layer('layer_2', text_object=text, parent='layer_1')
    layer_3 = Layer('layer_3', text_object=text, parent='layer_2')
    layer_4 = Layer('layer_4', text_object=text, enveloping='layer_2')
    layer_5 = Layer('layer_5', text_object=text, enveloping='layer_2')
    layer_6 = Layer('layer_6', text_object=text, parent='layer_5')

    layer_7 = Layer('layer_7', text_object=text)

    layer_8 = Layer('layer_8', text_object=text)
    layer_9 = Layer('layer_9', text_object=text, enveloping='layer_8')

    text.add_layer(layer_1)
    text.add_layer(layer_2)
    text.add_layer(layer_3)
    text.add_layer(layer_4)
    text.add_layer(layer_5)
    text.add_layer(layer_6)
    text.add_layer(layer_7)
    text.add_layer(layer_8)
    text.add_layer(layer_9)

    assert layer_1.ancestor_layers() == ['layer_2', 'layer_3', 'layer_4', 'layer_5', 'layer_6']
    assert layer_2.ancestor_layers() == ['layer_3', 'layer_4', 'layer_5', 'layer_6']
    assert layer_3.ancestor_layers() == []
    assert layer_4.ancestor_layers() == []
    assert layer_5.ancestor_layers() == ['layer_6']
    assert layer_6.ancestor_layers() == []

    assert layer_7.ancestor_layers() == []

    assert layer_8.ancestor_layers() == ['layer_9']
    assert layer_9.ancestor_layers() == []


def test_descendant_layers():
    text = Text('')

    layer_1 = Layer('layer_1', text_object=text)
    layer_2 = Layer('layer_2', text_object=text, parent='layer_1')
    layer_3 = Layer('layer_3', text_object=text, parent='layer_2')
    layer_4 = Layer('layer_4', text_object=text, enveloping='layer_2')
    layer_5 = Layer('layer_5', text_object=text, enveloping='layer_2')
    layer_6 = Layer('layer_6', text_object=text, parent='layer_5')

    layer_7 = Layer('layer_7', text_object=text)

    layer_8 = Layer('layer_8', text_object=text)
    layer_9 = Layer('layer_9', text_object=text, enveloping='layer_8')

    text.add_layer(layer_1)
    text.add_layer(layer_2)
    text.add_layer(layer_3)
    text.add_layer(layer_4)
    text.add_layer(layer_5)
    text.add_layer(layer_6)
    text.add_layer(layer_7)
    text.add_layer(layer_8)
    text.add_layer(layer_9)

    assert layer_1.descendant_layers() == []
    assert layer_2.descendant_layers() == ['layer_1']
    assert layer_3.descendant_layers() == ['layer_1', 'layer_2']
    assert layer_4.descendant_layers() == ['layer_1', 'layer_2']
    assert layer_5.descendant_layers() == ['layer_1', 'layer_2']
    assert layer_6.descendant_layers() == ['layer_1', 'layer_2', 'layer_5']

    assert layer_7.descendant_layers() == []

    assert layer_8.descendant_layers() == []
    assert layer_9.descendant_layers() == ['layer_8']
