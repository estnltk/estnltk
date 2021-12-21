import pytest
import re

from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core import ElementaryBaseSpan, Span, Annotation
from estnltk_core.layer import AttributeList

from estnltk_core.common import load_text_class

def test_add_annotation():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert len(span_1.annotations) == 2

    span_2 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_2.add_annotation(Annotation(span_2, attr_1=3))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))
    span_2.add_annotation(Annotation(span_2, attr_1=0))

    assert span_1 == span_2


def test_getattr():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

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


def test_getitem():
    span_1 = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert isinstance(span_1.annotations[0], Annotation)
    assert span_1.annotations[0].attr_1 == 0
    assert span_1.annotations[1].attr_1 == 3

    assert span_1['attr_1'] == AttributeList([0, 3], 'attr_1')

    with pytest.raises(KeyError):
        span_1[:]

    with pytest.raises(KeyError):
        span_1['bla']

    with pytest.raises(KeyError):
        span_1[0]


def test_base_spans():
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=BaseLayer('test', attributes=['attr_1'], ambiguous=True))

    assert ElementaryBaseSpan(0, 1) == span_1.base_span


def test_span_annotations_repr():
    # Test span annotations rendering (as string)
    # Case 1: spans with annotation values consisting of basic types: None, str, int, float, bool
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=None) )
    assert str(span) == "Span(None, [{'attr_1': None}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1='my_value') )
    assert str(span) == "Span(None, [{'attr_1': 'my_value'}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=42) )
    assert str(span) == "Span(None, [{'attr_1': 42}])"

    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=3.1415926535897) )
    assert str(span) == "Span(None, [{'attr_1': 3.1415926535897}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_1'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_1=False) )
    assert str(span) == "Span(None, [{'attr_1': False}])"
    
    # Case 2: spans with annotation values consisting of sequences of basic types
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_seq'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_seq=(None, None, None, False)) )
    assert str(span) == "Span(None, [{'attr_seq': (None, None, None, False)}])"
    
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_seq'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_seq=[1, 2, 3.14, 'N/A']) )
    assert str(span) == "Span(None, [{'attr_seq': [1, 2, 3.14, 'N/A']}])"

    # Case 3: spans with annotation values consisting of dicts of basic types
    span = Span(ElementaryBaseSpan(0, 1), BaseLayer('test', attributes=['attr_dict'], ambiguous=True))
    span.add_annotation( Annotation(span, attr_dict={"a": 1, "b": 2, "c": None}) )
    assert str(span) == "Span(None, [{'attr_dict': {'a': 1, 'b': 2, 'c': None}}])"

    # Case 4: repr of syntax layer (which has recursive span references)
    syntax_layer = BaseLayer( name='my_syntax', attributes=('id',
                                                            'lemma',
                                                            'head',
                                                            'parent_span',
                                                            'children') )
    syntax_layer.add_annotation( (0, 4), **{'head': 3,
                                            'id': 1,
                                            'lemma': 'tere',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (4, 5), **{'head': 3,
                                            'id': 2,
                                            'lemma': ',',
                                            'parent_span': None,
                                            'children': None} )
    syntax_layer.add_annotation( (6, 12), **{'head': 0,
                                             'id': 3,
                                             'lemma': 'Kerttu',
                                             'parent_span': None,
                                             'children': None} )
    syntax_layer.add_annotation( (12, 13), **{'head': 3,
                                              'id': 4,
                                              'lemma': '!',
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
    # Check span repr
    expected_span_0_repr = \
       "Span(None, [{'id': 1, 'lemma': 'tere', 'head': 3, 'parent_span': <class 'estnltk_core.layer.span.Span'>, 'children': ()}])"
    assert repr(syntax_layer[0]) == expected_span_0_repr
    assert str(syntax_layer[0]) == expected_span_0_repr
    expected_span_1_repr = \
       "Span(None, [{'id': 2, 'lemma': ',', 'head': 3, 'parent_span': <class 'estnltk_core.layer.span.Span'>, 'children': ()}])"
    assert repr(syntax_layer[1]) == expected_span_1_repr
    assert str(syntax_layer[1]) == expected_span_1_repr
    expected_span_2_repr = \
       "Span(None, [{'id': 3, 'lemma': 'Kerttu', 'head': 0, 'parent_span': None, 'children': <class 'tuple'>}])"
    assert repr(syntax_layer[2]) == expected_span_2_repr
    assert str(syntax_layer[2]) == expected_span_2_repr


def test_repr_html():
    # Test span rendering as HTML
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Case 1: no text object -- return same output as str
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=BaseLayer('test', attributes=['attr_1']))
    span_1.add_annotation(Annotation(span_1, attr_1=0))
    assert span_1._repr_html_() == str(span_1)

    # Case 2: with text object, return HTML
    text = Text('ABC')
    layer = BaseLayer('test', attributes=['attr_1'], text_object=text, ambiguous=True)
    span_1 = Span(ElementaryBaseSpan(0, 1), layer=layer)
    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))
    output_html_1 = span_1._repr_html_()
    output_html_2 = span_1._to_html()
    # This renders a HTML table. However, its formatting depends on pandas, so we don't
    # want to hardcode formatting into test. 
    # Instead, test loosely general properties
    assert output_html_1 == output_html_2
    assert output_html_1.startswith('<b>{}</b>'.format(span_1.__class__.__name__))
    assert '<table' in output_html_1
    assert '<th>text</th>' in output_html_1
    assert '<th>attr_1</th>' in output_html_1
    assert re.search( '<td>.*?A.*?</td>', output_html_1 ) is not None
    assert re.search( '<td>.*?0.*?</td>', output_html_1 ) is not None
    assert re.search( '<td></td>', output_html_1 ) is not None
    assert re.search( '<td>.*?3.*?</td>', output_html_1 ) is not None
    assert '</table>' in output_html_1

