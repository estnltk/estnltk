import pytest

import re
from copy import copy, deepcopy

from estnltk_core.layer.base_layer import BaseLayer
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

def test_attributes_and_default_values():
    layer = BaseLayer('test')
    assert () == layer.attributes
    assert {} == layer.default_values

    layer = BaseLayer('test', attributes=['attr_1', 'attr_2'], default_values={'attr_2': 2})
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
        layer.attributes = ['attr_1', 'attr_2', 'attr_1']

    assert ('attr_1', 'attr_2') == layer.attributes


def test_add_span():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('0123456789')
    layer = BaseLayer(name='ambiguous', attributes=['a', 'b', 'c'], ambiguous=True)

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

    layer = BaseLayer(name='ambiguous', attributes=['a', 'b', 'c'], ambiguous=False)

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
    # layer_0 : elementary layer, not ambiguous
    layer_0 = BaseLayer('layer_0', attributes=['attr_1', 'attr_2'], parent=None, enveloping=None, ambiguous=False)
    assert len(layer_0) == 0
    layer_0.add_annotation(ElementaryBaseSpan(10, 11), attr_1=11)
    assert len(layer_0) == 1
    assert layer_0[0].annotations == [Annotation(None, attr_1=11, attr_2=None)]
    with pytest.raises(ValueError):
        layer_0.add_annotation(ElementaryBaseSpan(10, 11), attr_1=111)

    layer_0.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_0) == 2
    assert layer_0[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # layer_1 : elementary layer, ambiguous
    layer_1 = BaseLayer('layer_1', attributes=['attr_1', 'attr_2'], parent=None, enveloping=None, ambiguous=True)
    assert len(layer_1) == 0
    layer_1.add_annotation(ElementaryBaseSpan(10, 11), attr_1=11)
    assert len(layer_1) == 1
    assert layer_1[0].annotations == [Annotation(None, attr_1=11, attr_2=None)]

    layer_1.add_annotation(ElementaryBaseSpan(10, 11), attr_1=111)
    assert layer_1[0].annotations == [Annotation(None, attr_1=11, attr_2=None), Annotation(None, attr_1=111, attr_2=None)]

    layer_1.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_1) == 2
    assert layer_1[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # layer_2 : elementary layer with parent
    layer_2 = BaseLayer('layer_2', attributes=['attr_1', 'attr_2'], parent='layer_0', enveloping=None, ambiguous=False)
    assert len(layer_2) == 0
    layer_2.add_annotation(layer_0[1], attr_1=2)
    assert len(layer_2) == 1
    assert layer_2[0].annotations == [Annotation(None, attr_1=2, attr_2=None)]
    with pytest.raises(ValueError):
        layer_2.add_annotation(layer_0[1], attr_1=111)

    layer_2.add_annotation(ElementaryBaseSpan(0, 1))
    assert len(layer_2) == 2
    assert layer_2[0].annotations == [Annotation(None, attr_1=None, attr_2=None)]

    # an enveloping layer
    # first, add base layer for the enveloping layer
    layer_0 = BaseLayer('layer_0', attributes=['span_id'], parent=None, enveloping=None, ambiguous=False)
    layer_0.add_annotation(ElementaryBaseSpan(0, 1), span_id=0)
    layer_0.add_annotation(ElementaryBaseSpan(1, 2), span_id=1)
    layer_0.add_annotation(ElementaryBaseSpan(2, 3), span_id=2)
    layer_0.add_annotation(ElementaryBaseSpan(3, 5), span_id=3)
    layer_0.add_annotation(ElementaryBaseSpan(5, 7), span_id=4)
    layer_0.add_annotation(ElementaryBaseSpan(7, 8), span_id=5)
    # layer_3 : the enveloping layer (level 1), not ambiguous
    layer_3 = BaseLayer('layer_3', attributes=['env_span_id'], parent=None, enveloping='layer_0', ambiguous=False)
    layer_3.add_annotation(EnvelopingBaseSpan( (ElementaryBaseSpan(0, 1), ElementaryBaseSpan(1, 2)) ), env_span_id=0)
    layer_3.add_annotation(EnvelopingBaseSpan( (ElementaryBaseSpan(2, 3), ElementaryBaseSpan(3, 5)) ), env_span_id=1)
    with pytest.raises(ValueError):
        # Adding a duplicate span raises a ValueError
        layer_3.add_annotation(EnvelopingBaseSpan( (ElementaryBaseSpan(2, 3), ElementaryBaseSpan(3, 5)) ), env_span_id=2)
    layer_3.add_annotation(EnvelopingBaseSpan( (ElementaryBaseSpan(5, 7), ElementaryBaseSpan(7, 8)) ), env_span_id=2)
    assert len(layer_3) == 3
    assert layer_3[0].base_span.level == 1
    assert layer_3[0].annotations == [Annotation(None, env_span_id=0)]
    assert layer_3[1].annotations == [Annotation(None, env_span_id=1)]
    assert layer_3[2].annotations == [Annotation(None, env_span_id=2)]
    with pytest.raises(ValueError, match='.*Mismatching base_span levels.*'):
        # Adding an enveloping span that has higher base_span level than the current one raises ValueError
        enveloping_span_level_2 = \
            EnvelopingBaseSpan((
                EnvelopingBaseSpan( (ElementaryBaseSpan(0, 1), ElementaryBaseSpan(1, 2)) ),
                EnvelopingBaseSpan( (ElementaryBaseSpan(2, 3), ElementaryBaseSpan(3, 5)) )
            ))
        layer_3.add_annotation(enveloping_span_level_2, env_span_id=22)

    # layer_4 : the enveloping layer (level 2), ambiguous
    layer_4 = BaseLayer('layer_4', attributes=['env_span_lvl2_count'], parent=None, enveloping='layer_3', ambiguous=True)
    enveloping_span_level_2 = \
        EnvelopingBaseSpan((
            EnvelopingBaseSpan( (ElementaryBaseSpan(0, 1), ElementaryBaseSpan(1, 2)) ),
            EnvelopingBaseSpan( (ElementaryBaseSpan(2, 3), ElementaryBaseSpan(3, 5)) )
        ))
    layer_4.add_annotation( enveloping_span_level_2, env_span_lvl2_count=0 )
    layer_4.add_annotation( enveloping_span_level_2, env_span_lvl2_count=1 )
    assert len(layer_4) == 1
    enveloping_span_level_2 = \
        EnvelopingBaseSpan((
            EnvelopingBaseSpan( (ElementaryBaseSpan(5, 7), ElementaryBaseSpan(7, 8)) ),
        ))
    layer_4.add_annotation( enveloping_span_level_2, env_span_lvl2_count=2 )
    layer_4.add_annotation( enveloping_span_level_2, env_span_lvl2_count=3 )
    assert len(layer_4) == 2
    assert layer_4[0].base_span.level == 2
    assert layer_4[0].annotations == [Annotation(None, env_span_lvl2_count=0), Annotation(None, env_span_lvl2_count=1)]
    assert layer_4[1].annotations == [Annotation(None, env_span_lvl2_count=2), Annotation(None, env_span_lvl2_count=3)]

    # test alternative ways of specifying attributes
    layer_x = BaseLayer('layer_x', attributes=['attr_1', 'attr_2'], parent=None, enveloping=None, ambiguous=False)
    assert len(layer_x) == 0
    # use only dictionary
    layer_x.add_annotation(ElementaryBaseSpan(0, 1), {'attr_1': 11})
    assert layer_x[0].annotations == [Annotation(None, attr_1=11, attr_2=None)]
    layer_x.add_annotation(ElementaryBaseSpan(1, 2), {'attr_1': 21, 'attr_2': 22})
    assert layer_x[1].annotations == [Annotation(None, attr_1=21, attr_2=22)]
    # use dictionary + keywords
    layer_x.add_annotation(ElementaryBaseSpan(2, 3), {'attr_1': 31}, attr_2=32)
    assert layer_x[2].annotations == [Annotation(None, attr_1=31, attr_2=32)]
    # use only keywords
    layer_x.add_annotation(ElementaryBaseSpan(3, 4), attr_1=41, attr_2=42)
    assert layer_x[3].annotations == [Annotation(None, attr_1=41, attr_2=42)]
    # use only keyword arguments from dict
    layer_x.add_annotation(ElementaryBaseSpan(4, 5), **{'attr_1':51, 'attr_2':52})
    assert layer_x[4].annotations == [Annotation(None, attr_1=51, attr_2=52)]
    # use a mix of regular dict and keyword arguments from dict
    layer_x.add_annotation(ElementaryBaseSpan(5, 6), {'attr_1': 61}, **{'attr_2':62})
    assert layer_x[5].annotations == [Annotation(None, attr_1=61, attr_2=62)]
    # Problematic case: cannot use attribute_dict as a simple keyword, it should be a dictionary
    with pytest.raises(ValueError, match=".+attribute_dict should be an instance of dict, not <class 'int'>"):
        layer_x.add_annotation( ElementaryBaseSpan(6, 7), attribute_dict=55 )


def test_add_annotation_with_tricky_attributes():
    # Test adding an annotation to a BaseLayer that has attributes 'text', 'start', 'end', 'span'
    layer = BaseLayer('my_layer', attributes=('text', 'start', 'end', 'span'))
    layer.add_annotation( ElementaryBaseSpan(1, 2), {'text': 'got you', 'start': 'you do not expect it', 'span': 'this can really break the construction'} )
    assert len(layer) == 1
    assert layer[0].annotations == [Annotation(None, {'text': 'got you', 'start': 'you do not expect it', 'end': None, 'span': 'this can really break the construction'})]


def test_layer_span_levels():
    layer = BaseLayer(name='my_layer', attributes=['a'])
    # Span level of the new empty layer is Mone 
    assert layer.span_level is None
    
    layer.add_annotation( ElementaryBaseSpan(0, 1), {'a':1} )
    # Span level of ElementaryBaseSpan is 0
    assert layer.span_level == 0
    layer.add_annotation( ElementaryBaseSpan(1, 2), {'a':2} )
    assert layer.span_level == 0
    
    # Restart the layer: the span level does not change
    layer.clear_spans()
    assert len(layer) == 0
    assert layer.span_level == 0
    
    # We cannot add enveloping spans (because the layer is not enveloping)
    with pytest.raises(TypeError, match=".+Elementary span is required.+"):
        layer.add_annotation( EnvelopingBaseSpan((ElementaryBaseSpan(0, 1), ElementaryBaseSpan(1, 2))), {'a':3} )
    
    env_layer = BaseLayer(name='enveloping_layer', attributes=['b'], enveloping='my_layer')
    # Span level of the new empty layer is Mone 
    assert env_layer.span_level is None
    env_layer.add_annotation( EnvelopingBaseSpan((ElementaryBaseSpan(0, 1), ElementaryBaseSpan(1, 2))), {'b':3} )
    # Span level of ordinary EnvelopingBaseSpan is 1
    assert env_layer.span_level == 1
    
    # Restart the layer: span level does not change
    env_layer.clear_spans()
    assert len(env_layer) == 0
    assert env_layer.span_level == 1

    # Cannot add enveloping span with different level
    with pytest.raises(ValueError, match=".+Mismatching base_span levels.+"):
        enveloping_span_level_2 = \
            EnvelopingBaseSpan((
                EnvelopingBaseSpan( (ElementaryBaseSpan(2, 3), ElementaryBaseSpan(3, 5)) ),
            ))
        env_layer.add_annotation( enveloping_span_level_2, {'a':3} )


def test_layer_clear_spans():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('0123456789')
    layer = BaseLayer(name='ambiguous', attributes=['a', 'b', 'c'], ambiguous=True)

    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    layer.add_span(span)

    span = Span(base_span=ElementaryBaseSpan(1, 2), layer=layer)
    span.add_annotation(Annotation(span, a='s2', b=False, c=5))
    span.add_annotation(Annotation(span, a='s4', b=False, c=5))
    layer.add_span(span)

    text.add_layer(layer)
    
    assert len(layer) == 2
    
    # Restart the layer
    layer.clear_spans()
    
    assert len(layer) == 0
    assert list(layer) == []
    
    span = Span(base_span=ElementaryBaseSpan(3, 4), layer=layer)
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    span.add_annotation(Annotation(span, a='s1', b=True, c=None))
    layer.add_span(span)
    
    assert len(layer) == 1


def test_layer_start_end():
    # Test that layer's start/end indexes will be properly resolved.
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    t = Text("0123456789")
    # Test empty layer
    empty_layer = BaseLayer('empty_layer', attributes=['value'])
    with pytest.raises(IndexError):
        assert empty_layer.start == -1
    with pytest.raises(ValueError):
        assert empty_layer.end == -1
    # Test filled-in layer
    layer = BaseLayer('layer', attributes=['value'])
    layer.add_annotation( (0,1), **{'value':0} )
    layer.add_annotation( (1,2), **{'value':1} )
    layer.add_annotation( (2,3), **{'value':2} )
    layer.add_annotation( (2,7), **{'value':None} )
    layer.add_annotation( (3,5), **{'value':None} )
    layer.add_annotation( (4,6), **{'value':None} )
    t.add_layer(layer)
    assert layer.start == 0
    assert layer.enclosing_text == '0123456'
    del layer[0]
    del layer[0]
    assert layer.start == 2
    assert layer.end == 7
    assert layer.enclosing_text == '23456'


def test_layer_indexing():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text("0123456789")
    layer = BaseLayer(name='base',
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
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.a, AttributeList)
    assert isinstance(layer['b'], AttributeList)
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.b, AttributeList)
    assert isinstance(layer['c'], AttributeList)
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.c, AttributeList)

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
    
    # Test getting indexes of specific spans
    assert layer.index( layer[0] ) == 0
    assert layer.index( layer[2] ) == 2
    assert layer.index( layer[6] ) == 6
    assert layer.index( layer[-1] ) == 7

    # Test getting items by their basespans
    assert layer.get( layer[0].base_span ) == layer[0]
    assert layer.get( layer[2].base_span ) == layer[2]
    assert layer.get( ElementaryBaseSpan(3, 4) ) == layer[3]
    assert layer.get( ElementaryBaseSpan(7, 8) ) == layer[7]


def test_ambiguous_layer_indexing():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text("0123456789")
    layer = BaseLayer(name='base',
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
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.a, AmbiguousAttributeList)
    assert isinstance(layer['b'], AmbiguousAttributeList)
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.b, AmbiguousAttributeList)
    assert isinstance(layer['c'], AmbiguousAttributeList)
    with pytest.raises(AttributeError):
        # AttributeError: attributes cannot be accessed directly in BaseLayer
        assert isinstance(layer.c, AmbiguousAttributeList)

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
    morph_layer = BaseLayer(name='morph_analysis',
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


def test_check_layer_consistency():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # 0) Set up test data
    # Create example texts with 'morph_analysis' layers
    # Create text 1
    text1 = Text('Kas?')
    morph_layer1 = BaseLayer(name='morph_analysis',
                             attributes=('normalized_text',
                                        'lemma',
                                        'root',
                                        'root_tokens',
                                        'ending',
                                        'clitic',
                                        'form',
                                        'partofspeech'),
                             text_object=text1,
                             enveloping=None,
                             parent=None,
                             ambiguous=True)
    # Populate layer with annotations
    morph_layer1.add_annotation( (0, 3), **{'clitic': '',
                                           'ending': '0',
                                           'form': '',
                                           'lemma': 'kas',
                                           'normalized_text': 'Kas',
                                           'partofspeech': 'D',
                                           'root': 'kas',
                                           'root_tokens': ['kas']} )
    morph_layer1.add_annotation( (3, 4), **{'clitic': '',
                                           'ending': '',
                                           'form': '',
                                           'lemma': '?',
                                           'normalized_text': '?',
                                           'partofspeech': 'Z',
                                           'root': '?',
                                           'root_tokens': ['?']} )
    text1.add_layer( morph_layer1 )
    # Create text 2
    text2 = Text('Kes ja kus?')
    morph_layer2 = BaseLayer(name='morph_analysis',
                            attributes=('normalized_text',
                                        'lemma',
                                        'root',
                                        'root_tokens',
                                        'ending',
                                        'clitic',
                                        'form',
                                        'partofspeech'),
                            text_object=text2,
                            enveloping=None,
                            parent=None,
                            ambiguous=True)
    # Populate layer with annotations
    morph_layer2.add_annotation( (0, 3), **{'clitic': '',
                                            'ending': '0',
                                            'form': 'sg n',
                                            'lemma': 'kes',
                                            'normalized_text': 'Kes',
                                            'partofspeech': 'P',
                                            'root': 'kes',
                                            'root_tokens': ['kes']} )
    morph_layer2.add_annotation( (0, 3), **{'clitic': '',
                                            'ending': '0',
                                            'form': 'pl n',
                                            'lemma': 'kes',
                                            'normalized_text': 'Kes',
                                            'partofspeech': 'P',
                                            'root': 'kes',
                                            'root_tokens': ['kes']} )
    morph_layer2.add_annotation( (4, 6), **{'clitic': '',
                                            'ending': '0',
                                            'form': '',
                                            'lemma': 'ja',
                                            'normalized_text': 'ja',
                                            'partofspeech': 'J',
                                            'root': 'ja',
                                            'root_tokens': ['ja']} )
    morph_layer2.add_annotation( (7, 10), **{'clitic': '',
                                             'ending': '0',
                                             'form': '',
                                             'lemma': 'kus',
                                             'normalized_text': 'kus',
                                             'partofspeech': 'D',
                                             'root': 'kus',
                                             'root_tokens': ['kus']} )
    morph_layer2.add_annotation( (10, 11), **{'clitic': '',
                                              'ending': '',
                                              'form': '',
                                              'lemma': '?',
                                              'normalized_text': '?',
                                              'partofspeech': 'Z',
                                              'root': '?',
                                              'root_tokens': ['?']} )
    text2.add_layer( morph_layer2 )
    
    # Fetch layers for consistency testing 
    other_morph_layer = text1['morph_analysis']
    morph_layer = text2['morph_analysis']

    # 1) Change first span, assign it to different layer
    old_first_span = morph_layer.spans[0]
    morph_layer.spans[0] = Span(base_span=old_first_span.base_span, layer=other_morph_layer)
    
    # Error msg because the Span is attached to a different layer
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is not None
    assert re.match('.+ is not attached to this layer', error_msg)
    
    morph_layer.spans[0] = old_first_span
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is None

    # 2) Add element with duplicate location to the list
    # (duplicate first span)
    morph_layer.spans.insert( 0, old_first_span )
    # Error msg because of span with duplicate location
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is not None
    assert re.match('duplicate spans:.+', error_msg)
   
    morph_layer.spans.pop(0)
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is None

    # 3) Add element with wrong location to the list
    # (add first span to the end of the spanlist)
    morph_layer.spans.append( old_first_span )
    # Error msg because of span with wrong location
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is not None
    assert re.match('ordering problem:.+', error_msg)

    morph_layer.spans.pop()
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is None

    # 4) Set span without annotations
    morph_layer.spans[0] = Span(old_first_span.base_span, old_first_span.layer)
    # Error msg because the first span has no annotations
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is not None
    assert re.match('.+ has no annotations', error_msg)
    
    morph_layer.spans[0] = old_first_span
    error_msg = morph_layer.check_span_consistency()
    assert error_msg is None

    # 5) Layer with missing attributes
    layer1 = BaseLayer(name='test_layer1',
                       attributes=['a', 'b', 'c'],
                       ambiguous=True)
    layer1.add_annotation((0, 1))
    assert layer1[0].annotations[0].a is None
    assert layer1[0].annotations[0].b is None
    assert layer1[0].annotations[0].c is None
    error_msg = layer1.check_span_consistency()
    assert error_msg is None
    del layer1[0].annotations[0].b
    # Error because layer's Annotation had missing attributes
    error_msg = layer1.check_span_consistency()
    #print(error_msg)
    assert error_msg is not None
    assert re.match(".+ has redundant annotation attributes: .+, missing annotation attributes: {'b'}", error_msg)

    # 6) Layer with redundant attributes
    layer1 = BaseLayer(name='test_layer1',
                       attributes=['a'],
                       ambiguous=True)
    layer2 = BaseLayer(name='test_layer2',
                       attributes=['a', 'b'],
                       ambiguous=True)
    amb_span1 = Span(ElementaryBaseSpan(0, 1), layer=layer1)
    amb_span2 = Span(ElementaryBaseSpan(0, 1), layer=layer2)
    broken_annotation = Annotation(amb_span2)
    for attr in ['a', 'b', 'c']:
        setattr(broken_annotation, attr, '')
    amb_span1.annotations.append(broken_annotation)
    layer1.spans.append(amb_span1)
    # Error because layer's Annotation had redundant attr
    error_msg = layer1.check_span_consistency()
    #print(error_msg)
    assert error_msg is not None
    assert re.match(".+ has redundant annotation attributes: {('b', 'c'|'c', 'b')}, missing annotation attributes:.+", error_msg)

    # B1) Check for missing Span attributes
    layer = BaseLayer(name='test_layer',
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
    # Error because Span misses some legal attributes
    error_msg = layer.check_span_consistency()
    #print(error_msg)
    assert error_msg is not None
    assert re.match(".+ has redundant annotation attributes: .+, missing annotation attributes: {'c'}", error_msg)
    del layer.spans[-1]
    del layer.spans[-1]

    # B2) Check for redundant Span attributes
    span3 = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    span3.add_annotation(Annotation(span3, a=1, b=11, c=0))
    span3.annotations[0].d = 12

    layer.spans.append(span3)
    # Error because annotation of the span3 has a redundant attribute
    error_msg = layer.check_span_consistency()
    #print(error_msg)
    assert error_msg is not None
    assert re.match(".+ has redundant annotation attributes: {'d'}, missing annotation attributes:.+", error_msg)


def test_shallow_copy():
    # Copying of detached layers
    # =======
    # Tests based on:
    # https://github.com/estnltk/estnltk/blob/5bacff50072f9415814aee4f369c28db0e8d7789/estnltk/tests/test_layer/test_layer_standard_operators.py#L33-L52
    layer = BaseLayer(
        name='empty_layer',
        attributes=['a', 'b'],
        text_object=None,
        parent=None,
        enveloping=None,
        ambiguous=True,
        default_values=dict(a=5, b='str'),
        serialisation_module="syntax_v0"
    )
    layer.meta = {'count': 5}

    s_copy = copy(layer)
    assert s_copy is not layer
    assert s_copy.name is layer.name
    assert s_copy.parent is layer.parent
    assert s_copy.enveloping is layer.enveloping
    assert s_copy.ambiguous is layer.ambiguous
    assert s_copy.serialisation_module is layer.serialisation_module
    assert s_copy.meta == layer.meta
    assert s_copy.meta is not layer.meta
    # =======
    
    layer = BaseLayer('test')
    layer_copy = copy( layer )
    assert layer == layer_copy
    assert layer is not layer_copy

    # Copying of attached layers
    text = new_text(5)

    layer = text['layer_1']
    layer_copy = copy( layer )

    assert layer_copy == layer
    assert layer_copy.attributes == layer.attributes
    # the tuple of attribute names is deep copied
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

    # list of spans is shallow copied 
    # internal
    assert layer_copy == layer
    assert layer_copy._span_list == layer._span_list
    assert layer_copy._span_list is not layer._span_list
    # public
    assert layer_copy == layer
    span = layer_copy[0]
    del layer_copy[0]
    assert layer_copy == layer
    assert len(layer_copy) == len(layer)

    # list of annotations is shallow copied
    assert layer == layer_copy
    layer_copy.add_annotation(layer_copy[0].base_span, attr='L1-2',  attr_1='kümme')
    assert layer_copy == layer
    del layer_copy[0].annotations[-1]

    # annotations are shallow copied
    assert layer == layer_copy
    layer_copy[0].annotations[0].attr_0 = '101'
    assert layer_copy == layer
    layer_copy[0].annotations[0].attr_0 = '100'


def test_deep_copy():
    # Simple empty layer
    layer = BaseLayer('test')
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Ambiguous layer
    text = new_text(5)

    layer = text['layer_1']
    layer_deepcopy = deepcopy( layer )
    assert layer_deepcopy == layer
    # Modify attributes
    # Initially, both layers' attributes point to the same tuple
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy.attributes is layer.attributes
    layer_deepcopy.attributes = [*layer_deepcopy.attributes, 'new_attribute']
    assert layer_deepcopy.attributes != layer.attributes
    layer_deepcopy.attributes = layer_deepcopy.attributes[:-1]
    # After modification of one layer, tuples won't be same anymore ...
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy.attributes is not layer.attributes

    # Modify spans
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] == layer[0]
    # Span references are different
    assert layer_deepcopy[0] is not layer[0]
    # Deleting span from one layer does not affect the other layer
    del layer_deepcopy[0]
    assert layer_deepcopy != layer
    layer_deepcopy.add_annotation(layer[0].base_span, attr='L1-0',  attr_1='SADA')
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] is not layer[0]
    
    # Modify annotations
    assert layer_deepcopy[0].annotations == layer[0].annotations
    # We can modify annotations without affecting the other layer
    layer_deepcopy.add_annotation(layer_deepcopy[1].base_span, attr='L1-2',  attr_1='KAKS!')
    assert layer_deepcopy[1].annotations != layer[1].annotations
    del layer_deepcopy[1].annotations[-1]
    assert layer_deepcopy[1].annotations == layer[1].annotations
    assert layer_deepcopy[1].annotations is not layer[1].annotations
    layer[2].annotations[-1].attr = '???'
    assert layer_deepcopy[2].annotations[-1].attr == 'L1-2'
    assert layer_deepcopy[2].annotations != layer[2].annotations
    layer_deepcopy[2].annotations[-1].attr = '???'
    assert layer_deepcopy[2].annotations == layer[2].annotations
    assert layer_deepcopy[2] == layer[2]

    # Enveloping layer
    Text = load_text_class()
    text = Text("Lihtsate kihtidega teksti kopeerimine")
    layer_a = BaseLayer('my_layer', attributes=['a', 'b'])
    layer_a.add_annotation( ElementaryBaseSpan(0, 4), a=1, b=2 )
    layer_a.add_annotation( ElementaryBaseSpan(5, 8), a=3, b=4 )
    text.add_layer( layer_a )
    env_layer = BaseLayer( 'enveloping_layer', attributes=['c'], 
                            enveloping='my_layer', ambiguous=True )
    text.add_layer( env_layer )
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [s.base_span for s in text['my_layer']] ), \
                               layer=env_layer )
    text['enveloping_layer'].add_annotation( env_span, c=9 )
    env_layer_deepcopy = deepcopy( text['enveloping_layer'] )
    assert env_layer == env_layer_deepcopy
    assert env_layer is not env_layer_deepcopy
    assert env_layer.meta is not env_layer_deepcopy.meta
    assert env_layer[0] == env_layer_deepcopy[0]
    
    # Modify spans
    del env_layer_deepcopy[0]
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [text['my_layer'][0].base_span] ), \
                               layer=env_layer_deepcopy )
    env_layer_deepcopy.add_annotation( env_span, c=7 )
    assert env_layer[0] != env_layer_deepcopy[0]
    assert env_layer != env_layer_deepcopy
    del env_layer_deepcopy[0]
    assert env_layer != env_layer_deepcopy
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [ text['my_layer'][0].base_span, \
                                                     text['my_layer'][1].base_span ] ), \
                               layer=env_layer_deepcopy )
    env_layer_deepcopy.add_annotation( env_span, c=9 )
    assert env_layer[0] == env_layer_deepcopy[0]
    assert env_layer == env_layer_deepcopy
    
    # Modify annotations
    env_layer_deepcopy.add_annotation(env_layer_deepcopy[0].base_span, c=10)
    env_layer_deepcopy.add_annotation(env_layer_deepcopy[0].base_span, c=11)
    assert env_layer[0].annotations != env_layer_deepcopy[0].annotations
    del env_layer_deepcopy[0].annotations[-1]
    env_layer.add_annotation(env_layer[0].base_span, c=10)
    assert env_layer[0].annotations == env_layer_deepcopy[0].annotations
    assert env_layer[0].annotations is not env_layer_deepcopy[0].annotations
    env_layer_deepcopy[0].annotations[-1].c = 9000
    assert env_layer[0].annotations != env_layer_deepcopy[0].annotations
    env_layer[0].annotations[-1].c = 9000
    assert env_layer[0].annotations == env_layer_deepcopy[0].annotations
    
    # =======
    # Tests based on:
    # https://github.com/estnltk/estnltk/blob/5bacff50072f9415814aee4f369c28db0e8d7789/estnltk/tests/test_layer/test_layer_standard_operators.py#L55-L166
    layer = BaseLayer(
        name='empty_layer',
        attributes=['a', 'b'],
        text_object=None,
        parent=None,
        enveloping=None,
        ambiguous=True,
        default_values=dict(a=5, b='str'),
        serialisation_module='syntax_v0'
    )
    layer.meta = {'count': 5}

    d_copy = deepcopy(layer)
    assert d_copy is not layer
    assert d_copy.name is layer.name
    assert d_copy.parent is layer.parent
    assert d_copy.enveloping is layer.enveloping
    assert d_copy.ambiguous is layer.ambiguous
    assert d_copy.serialisation_module is layer.serialisation_module
    assert d_copy.default_values is not layer.default_values
    assert d_copy.default_values == layer.default_values
    assert d_copy.meta is not layer.meta
    assert d_copy.meta == layer.meta
    assert d_copy.text_object is None
    assert d_copy.text_object == layer.text_object
    assert d_copy._span_list is not layer._span_list
    assert len(d_copy._span_list) == 0

    # Copying of attached empty layers
    text = Text("Test that layer attributes are correctly copied")
    text.add_layer(layer)
    assert layer.text_object is text
    assert d_copy.text_object is None

    # Copying of empty layer
    d_copy = deepcopy(layer)
    assert d_copy.text_object is not layer.text_object
    assert d_copy.text_object == layer.text_object

    # Copying of a simple nonempty layer
    layer = BaseLayer('nonempty_layer', attributes=['a', 'b'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    layer.add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)
    text.add_layer(layer)

    d_copy = deepcopy(layer)
    assert d_copy is not layer
    assert d_copy.name is layer.name
    assert d_copy.parent is layer.parent
    assert d_copy.enveloping is layer.enveloping
    assert d_copy.ambiguous is layer.ambiguous
    assert d_copy.serialisation_module is layer.serialisation_module
    assert d_copy.default_values is not layer.default_values
    assert d_copy.default_values == layer.default_values
    assert d_copy.meta is not layer.meta
    assert d_copy.meta == layer.meta
    assert d_copy._span_list is not layer._span_list
    assert len(d_copy._span_list) == len(layer._span_list)
    for i in range(len(d_copy._span_list)):
        assert d_copy[i] is not layer[i]
        assert d_copy[i].base_span is layer[i].base_span
        assert d_copy[i] == layer[i]

    # Copying of a simple nonempty layer with recursive meta
    layer = BaseLayer('recursive_meta', attributes=['a', 'b'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    layer.add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)
    layer.meta = {'text': text, 'layer': layer, 'span': layer[0]}
    text.add_layer(layer)

    d_copy = deepcopy(layer)
    assert d_copy is not layer
    assert d_copy.name is layer.name
    assert d_copy.parent is layer.parent
    assert d_copy.enveloping is layer.enveloping
    assert d_copy.ambiguous is layer.ambiguous
    assert d_copy.serialisation_module is layer.serialisation_module
    assert d_copy.default_values is not layer.default_values
    assert d_copy.default_values == layer.default_values
    assert d_copy.meta is not layer.meta
    assert d_copy.meta == layer.meta
    assert d_copy.text_object is not layer.text_object
    assert d_copy.text_object == layer.text_object
    assert d_copy._span_list is not layer._span_list
    assert len(d_copy._span_list) == len(layer._span_list)
    for i in range(len(d_copy._span_list)):
        assert d_copy[i] is not layer[i]
        assert d_copy[i].base_span is layer[i].base_span
        assert d_copy[i] == layer[i]

    # Copying of a recursive layer
    layer = BaseLayer('recursive_layer', attributes=['text', 'alayer', 'espan'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), text=text, alayer=layer)
    layer[0].espan = layer[0]
    layer.add_annotation(ElementaryBaseSpan(5, 8), text=text, alayer=text['nonempty_layer'], espan=text['nonempty_layer'][0])
    text.add_layer(layer)

    d_copy = deepcopy(layer)
    assert d_copy is not layer
    assert d_copy.name is layer.name
    assert d_copy.parent is layer.parent
    assert d_copy.enveloping is layer.enveloping
    assert d_copy.ambiguous is layer.ambiguous
    assert d_copy.serialisation_module is layer.serialisation_module
    assert d_copy.default_values is not layer.default_values
    assert d_copy.default_values == layer.default_values
    assert d_copy.meta is not layer.meta
    assert d_copy.meta == layer.meta
    #assert d_copy.text_object == layer.text_object  # infinite recursion, lets skip deep levels
    assert d_copy.text_object.text == layer.text_object.text
    assert d_copy.text_object.layers == layer.text_object.layers
    # ----------------------------------------------------------
    assert d_copy._span_list is not layer._span_list
    assert len(d_copy._span_list) == len(layer._span_list)
    for i in range(len(d_copy._span_list)):
        assert d_copy[i] is not layer[i]
        assert d_copy[i].base_span is layer[i].base_span
    assert d_copy[0]['text'] is d_copy.text_object
    assert d_copy[0].layer is d_copy
    assert d_copy[0]['alayer'] is d_copy
    assert d_copy[0]['espan'] is d_copy[0], "fails as Span's deep copy is incorrect"
    assert d_copy[1]['text'] is d_copy.text_object
    assert d_copy[1]['alayer'] is d_copy.text_object['nonempty_layer'], "Fails as Layer's deep copy is incorrect"
    # =======


def test_deep_copy_syntax_layer():
    # Special case of deepcopy: it should also work with syntax layer,
    # which attributes can contain references to other spans (complex 
    # references)
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Create txt with syntax layer
    text = Text('Tere, Kerttu!')
    syntax_layer = BaseLayer( name='my_syntax', attributes=('id',
                                                            'lemma',
                                                            'upostag',
                                                            'xpostag',
                                                            'feats',
                                                            'head',
                                                            'deprel',
                                                            'deps',
                                                            'misc',
                                                            'parent_span',
                                                            'children'),
                                                secondary_attributes=('parent_span',
                                                                      'children') )
    syntax_layer.add_annotation( (0, 4), **{'deprel': 'discourse',
                                            'deps': '_',
                                            'feats': {},
                                            'head': 3,
                                            'id': 1,
                                            'lemma': 'tere',
                                            'misc': '_',
                                            'upostag': 'I',
                                            'xpostag': 'I',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (4, 5), **{'deprel': 'punct',
                                            'deps': '_',
                                            'feats': {},
                                            'head': 3,
                                            'id': 2,
                                            'lemma': ',',
                                            'misc': '_',
                                            'upostag': 'Z',
                                            'xpostag': 'Z',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (6, 12), **{'deprel': 'root',
                                             'deps': '_',
                                             'feats': {'nom': 'nom',
                                                       'prop': 'prop',
                                                       'sg': 'sg'},
                                             'head': 0,
                                             'id': 3,
                                             'lemma': 'Kerttu',
                                             'misc': '_',
                                             'upostag': 'S',
                                             'xpostag': 'S',
                                             'parent_span': None,
                                             'children': None} )
    syntax_layer.add_annotation( (12, 13), **{'deprel': 'punct',
                                              'deps': '_',
                                              'feats': {},
                                              'head': 3,
                                              'id': 4,
                                              'lemma': '!',
                                              'misc': '_',
                                              'upostag': 'Z',
                                              'xpostag': 'Z',
                                              'parent_span': None,
                                              'children': None} )
    # Add parent/child references
    syntax_layer[0].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[0].annotations[0].children = ()
    syntax_layer[1].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[1].annotations[0].children = ()
    syntax_layer[2].annotations[0].parent_span = None
    syntax_layer[2].annotations[0].children = (syntax_layer[0], syntax_layer[1], syntax_layer[3])
    syntax_layer[3].annotations[0].parent_span = syntax_layer[2]
    syntax_layer[3].annotations[0].children = ()
    text.add_layer(syntax_layer)
    # Deepcopy syntax layer
    layer_deepcopy = deepcopy( syntax_layer )
    # Validate
    assert layer_deepcopy is not syntax_layer
    assert layer_deepcopy == syntax_layer
    assert layer_deepcopy.name == syntax_layer.name
    assert layer_deepcopy.attributes == syntax_layer.attributes
    assert layer_deepcopy.ambiguous == syntax_layer.ambiguous
    assert layer_deepcopy.parent == syntax_layer.parent
    assert layer_deepcopy.enveloping == syntax_layer.enveloping
    assert layer_deepcopy.serialisation_module == syntax_layer.serialisation_module
    assert len(layer_deepcopy) == len(syntax_layer)
    # 1) Validate copying references to spans: values should be equal
    assert syntax_layer[0].annotations[0].parent_span == layer_deepcopy[0].annotations[0].parent_span
    assert syntax_layer[1].annotations[0].parent_span == layer_deepcopy[1].annotations[0].parent_span
    assert syntax_layer[2].annotations[0].children == layer_deepcopy[2].annotations[0].children
    assert syntax_layer[3].annotations[0].parent_span == layer_deepcopy[3].annotations[0].parent_span
    
    # Checks that all attributes (except recursive 'parent_span' & 'children') are equal
    # ( reasoning: we cannot compare 'parent_span' & 'children' attribute values, as 
    #   they are recursive and this would lead to infinite recursion errors )
    def _annotations_equal_ex( annotation1, annotation2 ):
        assert annotation1.legal_attribute_names == annotation2.legal_attribute_names
        for attr in annotation1.legal_attribute_names:
            if attr not in ['parent_span', 'children']:
                assert annotation1[attr] == annotation2[attr]
    
    for i in range( len(layer_deepcopy) ):
        original_annotation = syntax_layer[i].annotations[0]
        deepcopy_annotation = layer_deepcopy[i].annotations[0]
        # Check that all attributes (except recursive 'parent_span' & 'children') are equal
        _annotations_equal_ex( original_annotation, deepcopy_annotation )
        # Check parent
        original_parent = original_annotation['parent_span']
        deepcopy_parent = deepcopy_annotation['parent_span']
        if isinstance( original_parent, Span ):
            assert original_parent.base_span == deepcopy_parent.base_span
            assert len(original_parent.annotations) == len(deepcopy_parent.annotations)
            for a in range(len(original_parent.annotations)):
                original_parent_ann = original_parent.annotations[0]
                deepcopy_parent_ann = deepcopy_parent.annotations[0]
                _annotations_equal_ex( original_parent_ann, deepcopy_parent_ann )
        else:
            assert original_parent == deepcopy_parent
        # Check children
        original_children = original_annotation['children']
        deepcopy_children = deepcopy_annotation['children']
        if len(original_children) > 0:
            for s in range(len(original_children)):
                orig_child = original_children[s]
                deep_child = deepcopy_children[s]
                assert orig_child.base_span == deep_child.base_span
                assert len(orig_child.annotations) == len(deep_child.annotations)
                for a in range(len(orig_child.annotations)):
                    orig_child_ann = orig_child.annotations[0]
                    deep_child_ann = deep_child.annotations[0]
                    _annotations_equal_ex( orig_child_ann, deep_child_ann )
        else:
            assert original_children == deepcopy_children

    # 2) Validate copying references to spans: references should point to different objects
    assert syntax_layer[0].annotations[0].parent_span is not layer_deepcopy[0].annotations[0].parent_span
    assert syntax_layer[1].annotations[0].parent_span is not layer_deepcopy[1].annotations[0].parent_span
    assert syntax_layer[2].annotations[0].children is not layer_deepcopy[2].annotations[0].children
    assert syntax_layer[3].annotations[0].parent_span is not layer_deepcopy[3].annotations[0].parent_span

