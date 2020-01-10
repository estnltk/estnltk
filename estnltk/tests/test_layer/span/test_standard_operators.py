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
        assert span_1.layer is span_2.layer
        assert span_1.base_span is span_2.base_span
        assert span_1.parent is span_2.parent
        assert span_1.annotations is span_2.annotations

    def check_deep_copy(span_1, span_2):
        assert span_1 is not span_2
        assert span_1.layer is not span_2.layer
        assert span_1.layer == span_2.layer
        assert span_1.base_span is span_2.base_span
        assert span_1.parent is not span_2.parent or span_1.parent is None
        assert span_1.parent == span_2.parent
        assert span_1.annotations is not span_2.annotations
        assert span_1.annotations == span_2.annotations

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
    span.parent = parent
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with a single annotation but with a parent
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=parent_layer)
    span.parent = parent
    annotation = Annotation(span=span, a=1, b=2, c=3)
    span.add_annotation(annotation)
    check_shallow_copy(copy(span), span)
    check_deep_copy(deepcopy(span), span)

    # Copying of span with several annotations but with a parent
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=parent_layer)
    span.parent = parent
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
    span.parent = span
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
    assert d_copy.layer is not span.layer
    assert d_copy.layer == span.layer
    assert d_copy.base_span is span.base_span
    assert d_copy.parent is None
    assert d_copy.parent == span.parent
    assert d_copy.annotations is not span.annotations
    assert len(d_copy.annotations) == 1
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy

    # Copying of recursive span with span annotations as an attribute
    layer = Layer('test_layer', attributes=['a', 'b', 'c', 'rec'], ambiguous=True, text_object=text)
    span = Span(base_span=base_span, layer=layer)
    annotation_1 = Annotation(span=span, a=1, b=2, c=3, rec=span)
    span.add_annotation(annotation_1)
    annotation_2 = Annotation(span=span, a=4, b=5, c=6, rec=None)
    span.add_annotation(annotation_2)
    annotation_2['rec'] = span.annotations
    assert span.annotations[0]['rec'] is span
    assert span.annotations[1]['rec'] is span.annotations
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    assert d_copy is not span
    assert d_copy.layer is not span.layer
    assert d_copy.layer == span.layer
    assert d_copy.base_span is span.base_span
    assert d_copy.parent is None
    assert d_copy.parent == span.parent
    assert d_copy.annotations is not span.annotations
    assert len(d_copy.annotations) == 2
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[1][('a', 'b', 'c')] == span.annotations[1][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy
    assert d_copy.annotations[1]['rec'] is d_copy.annotations

    # Copying of recursive span with parent as an attribute
    layer = Layer('test_layer', attributes=['a', 'b', 'c', 'rec'], ambiguous=True, text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    span.parent = parent
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
    assert d_copy.layer is not span.layer
    assert d_copy.layer == span.layer
    assert d_copy.base_span is span.base_span
    assert d_copy.parent is not span.parent
    assert d_copy.parent.base_span == span.parent.base_span
    assert len(d_copy.parent.annotations) == 1
    assert d_copy.parent.annotations[0][('a', 'b', 'c')] == span.parent.annotations[0][('a', 'b', 'c')]
    assert d_copy.parent.annotations[0]['rec'] is d_copy
    assert d_copy.annotations is not span.annotations
    assert len(d_copy.annotations) == 1
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy.parent


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
    error_template = 'an attempt to redefine a constant slot {!r} of Span. Define a new instance.'
    with pytest.raises(AttributeError, match=error_template.format('layer')):
        span.layer = None
    with pytest.raises(AttributeError, match=error_template.format('base_span')):
        span.base_span = None
    with pytest.raises(AttributeError, match=error_template.format('annotations')):
        span.annotations = None

    # Check that private slots cannot be assigned
    error_template = 'an attempt to assign a private slot {!r} of Span'
    with pytest.raises(AttributeError, match=error_template.format('_parent')):
        span._parent = None

    # Check that parent property cannot be assigned with incorrect values
    with pytest.raises(TypeError, match="'parent' must be an instance of Span."):
        span.parent = 5
    with pytest.raises(ValueError, match="an invalid 'parent' value: 'base_span' attributes must coincide."):
        span.parent = Span(base_span=ElementaryBaseSpan(2, 4), layer=layer)
    with pytest.raises(ValueError, match="an invalid 'parent' value: self-loops are not allowed."):
        span.parent = span

    # Check that parent property can be assigned only once
    span.parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    with pytest.raises(AttributeError, match="value of 'parent' property is already fixed. Define a new instance."):
        span.parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)

    # The same check but the parent property is computed silently
    text = Text('Tere!')
    parent_layer = Layer('parent_layer', attributes=['attr'], text_object=text)
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    text.add_layer(parent_layer)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    _ = span.parent
    with pytest.raises(AttributeError, match="value of 'parent' property is already fixed. Define a new instance."):
        span.parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)

    # The same check but the parent property is computed silently but it fails
    text = Text('Tere!')
    parent_layer = Layer('parent_layer', attributes=['attr'], text_object=text)
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    text.add_layer(parent_layer)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    _ = span.parent
    span.parent = parent
    assert span.parent is parent






def test_equality():
    pass

def test_repr_and_str():
    pass




