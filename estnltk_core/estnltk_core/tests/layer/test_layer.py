import pytest

from copy import copy, deepcopy

from estnltk_core import Layer
from estnltk_core import ElementaryBaseSpan
from estnltk_core import EnvelopingBaseSpan, EnvelopingSpan
from estnltk_core import Span
from estnltk_core import Annotation
from estnltk_core.layer import AmbiguousAttributeTupleList
from estnltk_core.layer import AmbiguousAttributeList
from estnltk_core.layer import AttributeTupleList
from estnltk_core.layer import AttributeList
from estnltk_core.tests import new_text

from estnltk_core.common import load_text_class

from estnltk_core.tests import create_amb_attribute_list


@pytest.mark.filterwarnings("ignore:Attribute names")
def test_problematic_attribute_names():
    # Test that warnings/errors will be risen in case of problematic attribute names
    layer = Layer('test', attributes=['attr_1', 'attr_2'])
    with pytest.warns(UserWarning, match='Attribute names.+are not valid Python identifiers.+'):
        layer.attributes = ['1attr', '2attr']
    assert ('1attr', '2attr') == layer.attributes

    with pytest.warns(UserWarning, match='Attribute names.+are not valid Python identifiers.+'):
        layer.attributes = ['3attr', 'attr 4']
    assert ('3attr', 'attr 4') == layer.attributes

    with pytest.warns(UserWarning, match='Attribute names.+overlap with Span/Annotation property.+'):
        layer.attributes = ['start', 'text']
    assert ('start', 'text') == layer.attributes

    # Test that BaseLayer's check about duplicate attribute names also works
    with pytest.raises(AssertionError):
        layer.attributes = ['attr_1', 'attr_2', 'attr_1']


def test_layer_indexing():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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

    atl = t['base']['a', 'b']
    t.pop_layer('base')
    assert isinstance(atl, AttributeTupleList)
    assert atl == create_amb_attribute_list([[1, 11],
                                             [2, 12],
                                             [3, 'default b'],
                                             ['default a', 'default b'],
                                             [5, 15],
                                             [6, 16],
                                             [7, None],
                                             [None, None]],
                                             ('a', 'b'))


def test_ambiguous_layer_indexing():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # 1) Set up test data
    # Create example text with 'morph_analysis' layer
    text = Text('Mis on Sinu nimi?')
    morph_layer = Layer(name='morph_analysis',
                        attributes=('normalized_text',
                                    'lemma',
                                    'root',
                                    'root_tokens',
                                    'ending',
                                    'clitic',
                                    'form',
                                    'partofspeech'),
                        text_object=text,
                        enveloping=None,
                        parent=None,
                        ambiguous=True)
    # Populate layer with annotations
    morph_layer.add_annotation( (0, 3), **{'clitic': '',
                                           'ending': '0',
                                           'form': 'sg n',
                                           'lemma': 'mis',
                                           'normalized_text': 'Mis',
                                           'partofspeech': 'P',
                                           'root': 'mis',
                                           'root_tokens': ['mis']} )
    morph_layer.add_annotation( (0, 3), **{'clitic': '',
                                           'ending': '0',
                                           'form': 'pl n',
                                           'lemma': 'mis',
                                           'normalized_text': 'Mis',
                                           'partofspeech': 'P',
                                           'root': 'mis',
                                           'root_tokens': ['mis']} )
    morph_layer.add_annotation( (4, 6), **{'clitic': '',
                                           'ending': '0',
                                           'form': 'b',
                                           'lemma': 'olema',
                                           'normalized_text': 'on',
                                           'partofspeech': 'V',
                                           'root': 'ole',
                                           'root_tokens': ['ole']} )
    morph_layer.add_annotation( (4, 6), **{'clitic': '',
                                           'ending': '0',
                                           'form': 'vad',
                                           'lemma': 'olema',
                                           'normalized_text': 'on',
                                           'partofspeech': 'V',
                                           'root': 'ole',
                                           'root_tokens': ['ole']} )
    morph_layer.add_annotation( (7, 11), **{'clitic': '',
                                            'ending': '0',
                                            'form': 'sg g',
                                            'lemma': 'sina',
                                            'normalized_text': 'Sinu',
                                            'partofspeech': 'P',
                                            'root': 'sina',
                                            'root_tokens': ['sina']} )
    morph_layer.add_annotation( (12, 16), **{'clitic': '',
                                            'ending': '0',
                                            'form': 'sg n',
                                            'lemma': 'nimi',
                                            'normalized_text': 'nimi',
                                            'partofspeech': 'S',
                                            'root': 'nimi',
                                            'root_tokens': ['nimi']} )
    morph_layer.add_annotation( (16, 17), **{'clitic': '',
                                             'ending': '',
                                             'form': '',
                                             'lemma': '?',
                                             'normalized_text': '?',
                                             'partofspeech': 'Z',
                                             'root': '?',
                                             'root_tokens': ['?']} )
    text.add_layer( morph_layer )
    
    # 2) Test layer access via indexing
    layer = text['morph_analysis']

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
    assert list(layer[0, ['lemma', 'form']][0]) == ['mis', 'sg n']
    assert list(layer[0, ['lemma', 'form']][1]) == ['mis', 'pl n']
    with pytest.raises(IndexError):
        layer[[]]


def test_count_values():
    assert new_text(1)['layer_5'].count_values('attr') == {}

    assert new_text(5)['layer_0'].count_values('attr_0') == {',': 1,
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

    assert new_text(5)['layer_1'].count_values('attr_1') == {'KAHEKSA': 1,
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
    result = new_text(5)['layer_1'].groupby(['attr_1']).groups
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

    result = new_text(5)['layer_0'].groupby(['attr', 'attr_0']).groups
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

    groups = new_text(5)['layer_1'].groupby(['attr'], return_type='annotations').groups
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

    result = new_text(5)['layer_0'].groupby(['attr', 'attr_0'], return_type='annotations').groups
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


def test_descendant_layers():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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

    assert layer_1.descendant_layers() == ['layer_2', 'layer_3', 'layer_4', 'layer_5', 'layer_6']
    assert layer_2.descendant_layers() == ['layer_3', 'layer_4', 'layer_5', 'layer_6']
    assert layer_3.descendant_layers() == []
    assert layer_4.descendant_layers() == []
    assert layer_5.descendant_layers() == ['layer_6']
    assert layer_6.descendant_layers() == []

    assert layer_7.descendant_layers() == []

    assert layer_8.descendant_layers() == ['layer_9']
    assert layer_9.descendant_layers() == []


def test_ancestor_layers():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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

    assert layer_1.ancestor_layers() == []
    assert layer_2.ancestor_layers() == ['layer_1']
    assert layer_3.ancestor_layers() == ['layer_1', 'layer_2']
    assert layer_4.ancestor_layers() == ['layer_1', 'layer_2']
    assert layer_5.ancestor_layers() == ['layer_1', 'layer_2']
    assert layer_6.ancestor_layers() == ['layer_1', 'layer_2', 'layer_5']

    assert layer_7.ancestor_layers() == []

    assert layer_8.ancestor_layers() == []
    assert layer_9.ancestor_layers() == ['layer_8']

