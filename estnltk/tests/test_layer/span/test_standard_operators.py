import pytest
from copy import copy, deepcopy

from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import EnvelopingSpan
from estnltk import Annotation
from estnltk import ElementaryBaseSpan
from estnltk import EnvelopingBaseSpan
from estnltk.tests import inspect_class_members


def test_len():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # For some reason simple span does not have len operator
    with pytest.raises(TypeError, match="object of type 'Span' has no len()"):
        _ = len(span)


def test_methods_list():
    pass


def test_copy_constructors():

    def check_shallow_copy(span_1, span_2):
        assert span_1 is not span_2
        assert span_1._layer is span_2._layer
        assert span_1._base_span is span_2._base_span
        assert span_1._parent is span_2._parent
        assert span_1._annotations is span_2._annotations

    def check_deep_copy(span_1, span_2):
        assert span_1 is not span_2
        assert span_1._layer is not span_2._layer
        assert span_1._layer == span_2._layer
        assert span_1._base_span is span_2._base_span
        assert span_1._parent is not span_2._parent or span_1.parent is None
        assert span_1._parent == span_2._parent
        assert span_1._annotations is not span_2._annotations
        assert span_1._annotations == span_2._annotations

    text = Text('Tere!')
    base_span = ElementaryBaseSpan(0, 4)
    layer = Layer('test_layer', attributes=['a', 'b', 'c'], ambiguous=True, text_object=text)

    # Copying of span with no annotations no parent
    span = Span(base_span=base_span, layer=layer)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with a single annotation but no parent
    span = Span(base_span=base_span, layer=layer)
    annotation = Annotation(span=span, a=1, b=2, c=3)
    span.add_annotation(annotation)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with several annotations but no parent
    span = Span(base_span=base_span, layer=layer)
    annotation_1 = Annotation(span=span, a=1, b=2, c=3)
    annotation_2 = Annotation(span=span, a=4, b=5, c=6)
    annotation_3 = Annotation(span=span, a=7, b=8, c=9)
    span.add_annotation(annotation_1)
    span.add_annotation(annotation_2)
    span.add_annotation(annotation_3)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    text = Text('Tere!')
    base_span = ElementaryBaseSpan(0, 4)
    parent_layer = Layer('parent_layer', attributes=['x', 'y', 'z'], ambiguous=True, text_object=text)
    layer = Layer('test_layer', attributes=['a', 'b', 'c'], ambiguous=True, parent=parent_layer, text_object=text)

    # Copying of span with no annotations but with a parent
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=parent_layer)
    # span._parent = parent
    super(Span, span).__setattr__('_parent', parent)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with a single annotation but with a parent
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=parent_layer)
    # span._parent = parent
    super(Span, span).__setattr__('_parent', parent)
    annotation = Annotation(span=span, a=1, b=2, c=3)
    span.add_annotation(annotation)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with several annotations but with a parent
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=parent_layer)
    # span._parent = parent
    super(Span, span).__setattr__('_parent', parent)
    annotation_1 = Annotation(span=span, a=1, b=2, c=3)
    annotation_2 = Annotation(span=span, a=4, b=5, c=6)
    annotation_3 = Annotation(span=span, a=7, b=8, c=9)
    span.add_annotation(annotation_1)
    span.add_annotation(annotation_2)
    span.add_annotation(annotation_3)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of recursive span with parent = span
    span = Span(base_span=base_span, layer=layer)
    # span._parent = span
    super(Span, span).__setattr__('_parent', span)
    assert span.parent is span
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    check_deep_copy(d_copy, span)
    assert d_copy.parent is d_copy

    # Copying of recursive span with span as an attribute
    layer = Layer('test_layer', attributes=['a', 'b', 'c', 'rec'], ambiguous=True, text_object=text)
    span = Span(base_span=base_span, layer=layer)
    annotation = Annotation(span=span, a=1, b=2, c=3, rec=span)
    span.add_annotation(annotation)
    assert span.annotations[0]['rec'] is span
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    assert d_copy is not span
    assert d_copy._layer is not span._layer
    assert d_copy._layer == span._layer
    assert d_copy._base_span is span._base_span
    assert d_copy.parent is None
    assert d_copy._parent == span._parent
    assert d_copy._annotations is not span._annotations
    assert len(d_copy._annotations) == 1
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy

    # Copying of recursive span with span annotations as an attribute
    layer = Layer('test_layer', attributes=['a', 'b', 'c', 'rec'], ambiguous=True, text_object=text)
    span = Span(base_span=base_span, layer=layer)
    annotation_1 = Annotation(span=span, a=1, b=2, c=3, rec=span)
    span.add_annotation(annotation_1)
    annotation_2 = Annotation(span=span, a=4, b=5, c=6, rec=None)
    span.add_annotation(annotation_2)
    annotation_2['rec'] = span._annotations
    assert span.annotations[0]['rec'] is span
    assert span.annotations[1]['rec'] is span._annotations
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    assert d_copy is not span
    assert d_copy._layer is not span._layer
    assert d_copy._layer == span._layer
    assert d_copy._base_span is span._base_span
    assert d_copy.parent is None
    assert d_copy._parent == span._parent
    assert d_copy._annotations is not span._annotations
    assert len(d_copy._annotations) == 2
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[1][('a', 'b', 'c')] == span.annotations[1][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy
    assert d_copy.annotations[1]['rec'] is d_copy._annotations

    # Copying of recursive span with parent as an attribute
    layer = Layer('test_layer', attributes=['a', 'b', 'c', 'rec'], ambiguous=True, text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(3, 4), layer=layer)
    # span._parent = parent
    super(Span, span).__setattr__('_parent', parent)
    annotation = Annotation(span=span, a=1, b=2, c=3, rec=span.parent)
    span.add_annotation(annotation)
    annotation = Annotation(span=parent, a=4, b=5, c=6, rec=span)
    parent.add_annotation(annotation)
    assert span.parent is parent
    assert span.annotations[0]['rec'] is parent
    assert parent.annotations[0]['rec'] is span
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    assert d_copy is not span
    assert d_copy._layer is not span._layer
    assert d_copy._layer == span._layer
    assert d_copy._base_span is span._base_span
    assert d_copy._parent is not span.parent
    assert d_copy._parent._base_span == span.parent._base_span
    assert len(d_copy._parent.annotations) == 1
    assert d_copy._parent.annotations[0][('a', 'b', 'c')] == span._parent.annotations[0][('a', 'b', 'c')]
    assert d_copy._parent.annotations[0]['rec'] is d_copy
    assert d_copy._annotations is not span._annotations
    assert len(d_copy._annotations) == 1
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy._parent


def test_attribute_assignment_and_access():
    pass

def test_attribute_deletion():
    pass

def test_item_assignment_and_access():
    pass

def test_multi_indexing():
    pass

def test_span_slot_access_rules():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Check that basic slots are fixed during initialisation and cannot be changed
    error_template = 'an attempt to change an immutable slot {!r} whose value is fixed by the constructor'
    with pytest.raises(AttributeError, match=error_template.format('_layer')):
        span._layer = None
    with pytest.raises(AttributeError, match=error_template.format('_base_span')):
        span._base_span = None


def test_equality():
    pass

def test_repr_and_str():
    pass




