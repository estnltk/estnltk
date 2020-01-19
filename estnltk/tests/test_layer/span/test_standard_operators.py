import pytest
from copy import copy, deepcopy

from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import EnvelopingSpan
from estnltk import Annotation
from estnltk import ElementaryBaseSpan
from estnltk.layer import AttributeList

from estnltk import EnvelopingBaseSpan
from estnltk.tests import inspect_class_members


def test_len():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # For some reason simple span does not have len operator
    with pytest.raises(TypeError, match="object of type 'Span' has no len()"):
        _ = len(span)


def test_protected_attribute_list():
    # Check that list of methods is constant
    assert isinstance(Span.methods, frozenset)
    # Test that the list of prohibited attribute names is complete
    members = inspect_class_members(Span(ElementaryBaseSpan(0, 1), None))
    assert set(members['properties']) <= Span.methods | Span.constant_attributes | {'parent', 'spans'}
    assert set(members['private_methods']) <= Span.methods
    assert set(members['protected_methods']) <= Span.methods
    assert set(members['public_methods']) <= Span.methods
    assert set(members['private_variables']) <= Span.constant_attributes
    assert set(members['protected_variables']) <= Span.methods
    assert set(members['public_variables']) <= Span.constant_attributes
    # Additional slots are assignable
    print(set(Span.__slots__) & Span.methods)
    assert len(set(Span.__slots__) & Span.methods) == 0
    # Make sure that Span passes Jupyter sanity checks
    assert '_ipython_canary_method_should_not_exist_' in Span.constant_attributes


def test_constructor():
    # Check a minimal viable constructor with elementary base span
    layer = Layer('test')
    base_span = ElementaryBaseSpan(0, 1)
    span = Span(base_span=base_span, layer=layer)
    assert span.layer is layer
    assert span.base_span is base_span
    assert span.annotations == list()
    assert span._parent is None
    assert span._spans is None

    # Check a minimal viable constructor with enveloping base span
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 2), ElementaryBaseSpan(3, 4)])
    span = EnvelopingSpan(base_span=base_span, layer=layer)
    assert span.layer is layer
    assert span.base_span is base_span
    assert span.annotations == list()
    assert span._parent is None
    assert span._spans is None


def test_copy_constructors():
    # TODO: Add check for _spans field
    # TODO: Correct checks .parent. It is incorrect now

    def check_shallow_copy(span_1, span_2):
        assert span_1 is not span_2
        assert span_1.layer is span_2.layer
        assert span_1.base_span is span_2.base_span
        assert span_1._parent is span_2._parent
        assert span_1.annotations is span_2.annotations

    def check_deep_copy(span_1, span_2):
        assert span_1 is not span_2
        assert span_1.layer is not span_2.layer
        assert span_1.layer == span_2.layer
        assert span_1.base_span is span_2.base_span
        assert span_1._parent is None or span_1._parent is not span_2._parent
        assert span_1._parent == span_2._parent
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

    # Copying of recursive span with parent.parent as span
    text = Text('Tere!')
    base_span = ElementaryBaseSpan(0, 4)
    layer = Layer('test_layer', attributes=['a', 'b', 'c'], text_object=text)
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=layer)
    span.add_annotation(Annotation(span=span, a=1, b=2, c=3))
    parent.add_annotation(Annotation(span=parent, a=4, b=5, c=6))
    span.parent = parent
    parent.parent = span
    assert span.parent is parent
    assert parent.parent is span
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    check_deep_copy(d_copy, span)
    assert d_copy.parent.parent is d_copy
    assert d_copy['a'] == 1
    assert d_copy.parent['a'] == 4

    # Copying of recursive span with span as an attribute
    text = Text('Tere!')
    base_span = ElementaryBaseSpan(0, 4)
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
    assert d_copy._parent is None
    assert d_copy._parent == span._parent
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
    assert d_copy._parent is None
    assert d_copy._parent == span._parent
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
    assert span._parent is parent
    assert span.annotations[0]['rec'] is parent
    assert parent.annotations[0]['rec'] is span
    check_shallow_copy(copy(span), span)
    d_copy = deepcopy(span)
    assert d_copy is not span
    assert d_copy.layer is not span.layer
    assert d_copy.layer == span.layer
    assert d_copy.base_span is span.base_span
    assert d_copy._parent is not span._parent
    assert d_copy._parent.base_span == span._parent.base_span
    assert len(d_copy.parent.annotations) == 1
    assert d_copy._parent.annotations[0][('a', 'b', 'c')] == span._parent.annotations[0][('a', 'b', 'c')]
    assert d_copy._parent.annotations[0]['rec'] is d_copy
    assert d_copy.annotations is not span.annotations
    assert len(d_copy.annotations) == 1
    assert d_copy.annotations[0][('a', 'b', 'c')] == span.annotations[0][('a', 'b', 'c')]
    assert d_copy.annotations[0]['rec'] is d_copy._parent


def test_attribute_assignment_and_access():
    # TODO: Use the next function as a start
    pass

def test_getattr():
    span_1 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

    span_1.add_annotation(Annotation(span_1, attr_1=0))
    span_1.add_annotation(Annotation(span_1, attr_1=3))

    assert span_1.attr_1 == AttributeList([0, 3], 'attr_1')

    _ = span_1.__getstate__
    _ = span_1.__setstate__
    with pytest.raises(AttributeError):
        span_1._ipython_canary_method_should_not_exist_
    with pytest.raises(AttributeError):
        span_1.blabla

    assert hasattr(span_1, 'attr_1')
    assert not hasattr(span_1, 'blabla')



def test_attribute_deletion():
    pass

def test_item_assignment_and_access():
    # TODO: Use the next function as a start
    pass

def test_getitem():
    span_1 = Span(ElementaryBaseSpan(0, 1), Layer('test', attributes=['attr_1'], ambiguous=True))

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


def test_multi_indexing():
    pass

def test_span_slot_access_rules():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    base_span = ElementaryBaseSpan(0, 4)
    span = Span(base_span=base_span, layer=layer)

    # Check that all basic slots are accessible for reading
    assert span.base_span is base_span
    assert span.layer is layer
    assert span.annotations == list()
    assert span._parent is None
    assert span._spans is None

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
    with pytest.raises(AttributeError, match=error_template.format('_spans')):
        span._spans = None

    # Span.parent and Span.spans are properties and tested together with other properties











def test_equality():
    pass

def test_repr_and_str():
    pass




