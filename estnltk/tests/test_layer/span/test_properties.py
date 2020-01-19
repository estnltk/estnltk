import pytest

from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import Annotation
from estnltk import ElementaryBaseSpan
from estnltk import EnvelopingBaseSpan


def test_start_and_end():
    # Span with elementary base span
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'])
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.start == 0
    assert span.end == 4

    # Span with enveloping base span
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.start == 0
    assert span.end == 12


def test_legal_attribute_names():
    return
    """
    TODO: Remove this function with the corresponding property
    """
    # Normal annotation without an attached span
    annotation = Annotation(span=None)
    assert annotation.legal_attribute_names is None

    # Annotation with without an attached span but has same-named attributes
    annotation = Annotation(span=None, legal_attribute_names=42)
    assert annotation.legal_attribute_names is None

    # Truly minimal layer
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'])
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Normal annotation with span
    annotation = Annotation(span=span, attr_1=42, attr_2=43, attr_3=44)
    assert annotation.legal_attribute_names == ('attr_1', 'attr_2', 'attr_3')

    # Normal annotation with span and extra attributes
    annotation = Annotation(span=span, legal_attribute_names=42, text=43, number=44)
    assert annotation.legal_attribute_names == ('attr_1', 'attr_2', 'attr_3')
    layer = Layer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, attr_1=42, attr_2=43, legal_attribute_names=44)
    assert annotation.legal_attribute_names == ()
    layer = Layer('test_layer', attributes=[])
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, attr_1=42, attr_2=43, legal_attribute_names=44)
    assert annotation.legal_attribute_names == ()


def test_text_properties_and_text_object():
    # Span with elementary base span and no layer
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Span with enveloping base span and no layer
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=None)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None


    # Span with elementary base span and no text object
    layer = Layer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Span with enveloping base span and no text object
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text is None
    assert span.enclosing_text is None
    assert span.text_object is None

    # Valid span with elementary base span that is attached to text
    text = Text('0123456789abcdef')
    layer = Layer('test_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text == '0123'
    assert span.enclosing_text == '0123'
    assert span.text_object is text

    # Valid span with enveloping base span that is attached to text
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '89ab']
    assert span.enclosing_text == '0123456789ab'
    assert span.text_object is text

    # Valid span with enveloping base span that is attached to text and is continuous
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(4, 8), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '4567', '89ab']
    assert span.enclosing_text == '0123456789ab'
    assert span.text_object is text

    # Invalid span with elementary base span that is attached to text
    # We cannot check whether span is valid during its creation as text might be unreachable.
    # Thus natural truncation is the only sane solution to the problem.
    text = Text('01')
    layer = Layer('test_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    assert span.text == '01'
    assert span.enclosing_text == '01'
    assert span.text_object is text
    # Invalid span that is completely outside of text
    # The outcome is an empty string
    span = Span(base_span=ElementaryBaseSpan(3, 8), layer=layer)
    assert span.text == ''
    assert span.enclosing_text == ''
    assert span.text_object is text

    # Invalid span with enveloping base span that is attached to text
    # Natural truncation is the only sane solution to the problem.
    # We do not omit empty texts to preserve the number of leafs
    text = Text('0123456789a')
    layer = Layer('test_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['0123', '89a']
    assert span.enclosing_text == '0123456789a'
    assert span.text_object is text
    text = Text('')
    layer = Layer('test_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    span = Span(base_span=base_span, layer=layer)
    assert span.text == ['', '']
    assert span.enclosing_text == ''
    assert span.text_object is text


def test_parent_property_assignment_and_access():
    # Check that parent property cannot be assigned with incorrect values
    layer = Layer('test_layer')
    base_span = ElementaryBaseSpan(0, 4)
    span = Span(base_span=base_span, layer=layer)
    # Only spans can be assigned as parents
    with pytest.raises(TypeError, match="'parent' must be an instance of Span."):
        span.parent = 5
    # Parent must have the same base span as the span
    with pytest.raises(ValueError, match="an invalid 'parent' value: 'base_span' attributes must coincide."):
        span.parent = Span(base_span=ElementaryBaseSpan(2, 4), layer=layer)
    with pytest.raises(ValueError, match="an invalid 'parent' value: 'base_span' attributes must coincide."):
        span.parent = Span(base_span=EnvelopingBaseSpan(spans=[base_span]), layer=layer)
    # Self-looping through parent attribute is not allowed
    with pytest.raises(ValueError, match="an invalid 'parent' value: self-loops are not allowed."):
        span.parent = span

    # Check that parent property can be assigned only once
    span = Span(base_span=base_span, layer=layer)
    parent = Span(base_span=base_span, layer=layer)
    span.parent = parent
    assert span.parent is parent
    with pytest.raises(AttributeError, match="value of 'parent' property is already fixed. Define a new instance."):
        span.parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)

    # Computation of parent property succeeds if we do everything right
    text = Text('Tere!')
    parent_layer = Layer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    text.add_layer(parent_layer)
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    # Parent attribute is computed and cached
    assert span.parent is parent_layer[0]
    assert span._parent is parent_layer[0]
    # It is now impossible to redefine the parent property
    with pytest.raises(AttributeError, match="value of 'parent' property is already fixed. Define a new instance."):
        span.parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)

    # Computation of parent property fails if span does not have a layer
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.parent is None
    assert span._parent is None
    # It is possible to redefine the parent property
    span.parent = parent
    assert span.parent is parent

    # Computation of parent property fails if a layer does have a parent attribute
    layer = Layer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.parent is None
    assert span._parent is None
    # It is possible to redefine the parent property
    span.parent = parent
    assert span.parent is parent

    # Computation of parent property fails if a layer does not reference a text object
    layer = Layer('test_layer', parent="parent_layer")
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    assert span.parent is None
    assert span._parent is None
    # It is possible to redefine the parent property
    span.parent = parent
    assert span.parent is parent

    # Computation of parent property fails if the parent layer is not attached to the text
    text = Text('Tere!')
    parent_layer = Layer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    parent = Span(base_span=ElementaryBaseSpan(0, 4), layer=None)
    # Parent attribute is not computed and cached
    assert span.parent is None
    assert span._parent is None
    # It is possible to redefine the parent property
    span.parent = parent
    assert span.parent is parent

    # Computation of parent property fails if the base span is not in parent layer that is attached to the text
    text = Text('Tere!')
    parent_layer = Layer('parent_layer', attributes=['attr'], text_object=text)
    parent_layer.add_annotation(base_span=ElementaryBaseSpan(0, 2), attr=42)
    text.add_layer(parent_layer)
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], parent='parent_layer', text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    # Parent attribute is not computed and cached
    assert span.parent is None
    assert span._parent is None
    # It is possible to redefine the parent property
    span.parent = parent
    assert span.parent is parent


def test_spans_property_assignment_and_access():
    # Check that spans property cannot be assigned with incorrect values
    layer = Layer('test_layer')
    base_span = ElementaryBaseSpan(0, 4)
    span = Span(base_span=base_span, layer=layer)
    # Spans must be empty for spans without compound spans
    with pytest.raises(AttributeError, match="'spans' property cannot be set as the span contains no sub-spans."):
        span.spans = [Span(base_span=base_span, layer=None)]
    # Only a list of spans can be assigned as spans
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    with pytest.raises(TypeError, match="'spans' must be a list or tuple of Span objects."):
        span.spans = 5
    with pytest.raises(TypeError, match="'spans' must be a list or tuple of Span objects."):
        span.spans = [4, 6, 9]
    # The number of spans in the list must be correct
    error = "an invalid 'spans' value: the number of spans must match the sub-span count."
    with pytest.raises(ValueError, match=error):
        span.spans = [Span(base_span=base_span._spans[0], layer=None)]
    # The base span attribute must be correct
    error = "an invalid 'spans' value: 'base_span' attribute must match a sub-span location."
    with pytest.raises(ValueError, match=error):
        span.spans = [Span(base_span=base_span._spans[0], layer=None), Span(base_span=base_span._spans[0], layer=None)]
    with pytest.raises(ValueError, match=error):
        span.spans = [Span(base_span=base_span._spans[1], layer=None), Span(base_span=base_span._spans[1], layer=None)]

    # Check that spans property can be assigned only once for tuple of spans
    layer = Layer('test_layer')
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = (Span(base_span=base_span._spans[0], layer=None),)
    span.spans = sub_spans
    assert span.spans == sub_spans
    with pytest.raises(AttributeError, match="value of 'spans' property is already fixed. Define a new instance."):
        span.spans = sub_spans

    # Check that spans property can be assigned only once for list of spans
    layer = Layer('test_layer')
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=base_span._spans[0], layer=None)]
    span.spans = sub_spans
    assert span.spans == sub_spans
    with pytest.raises(AttributeError, match="value of 'spans' property is already fixed. Define a new instance."):
        span.spans = sub_spans


    # Computation of spans property succeeds if we do everything right
    text = Text('Tere see on piisavalt pikk tekst!')
    base_layer = Layer('base_layer', attributes=['attr'], text_object=text)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(6, 10), attr=24)
    text.add_layer(base_layer)
    layer = Layer('test_layer', enveloping='base_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    # Span attribute is computed and cached
    assert span.spans == (base_layer[0], base_layer[1])
    assert span._spans[0] is base_layer[0]
    assert span._spans[1] is base_layer[1]
    # It is now impossible to redefine the parent property
    with pytest.raises(AttributeError, match="value of 'spans' property is already fixed. Define a new instance."):
        span.spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]

    # Computation of span property fails if span does not have a layer
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=None)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if a layer does have a enveloping attribute
    layer = Layer('test_layer')
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if a layer does not reference a text object
    layer = Layer('test_layer', enveloping='base_layer')
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if the base layer is not attached to the text
    text = Text('Tere see on piisavalt pikk tekst!')
    base_layer = Layer('base_layer', attributes=['attr'], text_object=text)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(6, 10), attr=24)
    layer = Layer('test_layer', enveloping='base_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if sub-spans are not in base layer that is attached to the text (1)
    text = Text('Tere see on piisavalt pikk tekst!')
    base_layer = Layer('base_layer', attributes=['attr'], text_object=text)
    text.add_layer(base_layer)
    layer = Layer('test_layer', enveloping='base_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if sub-spans are not in base layer that is attached to the text (2)
    text = Text('Tere see on piisavalt pikk tekst!')
    base_layer = Layer('base_layer', attributes=['attr'], text_object=text)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(0, 4), attr=42)
    text.add_layer(base_layer)
    layer = Layer('test_layer', enveloping='base_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans

    # Computation of spans property fails if sub-spans are not in base layer that is attached to the text (3)
    text = Text('Tere see on piisavalt pikk tekst!')
    base_layer = Layer('base_layer', attributes=['attr'], text_object=text)
    base_layer.add_annotation(base_span=ElementaryBaseSpan(6, 10), attr=24)
    text.add_layer(base_layer)
    layer = Layer('test_layer', enveloping='base_layer', text_object=text)
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 10)])
    span = Span(base_span=base_span, layer=layer)
    sub_spans = [Span(base_span=sub_base_span, layer=None) for sub_base_span in base_span._spans]
    assert span.spans is None
    assert span._spans is None
    # It is possible to redefine the spans property
    span.spans = sub_spans
    assert span.spans == sub_spans


def test_complex_logic_for_parent_and_spans_attributes():
    # Default resolving mechanism is conservative
    text = Text('Tere see on piisavalt pikk tekst!')
    layer_1 = Layer('layer_1', attributes=['a'], text_object=text)
    layer_2 = Layer('layer_2', attributes=['b'], text_object=text, parent='layer_1')
    layer_3 = Layer('layer_3', attributes=['c'], text_object=text, enveloping='layer_2')
    layer_4 = Layer('layer_4', attributes=['d'], text_object=text, parent='layer_3')
    text.add_layer(layer_1)
    text.add_layer(layer_2)
    text.add_layer(layer_3)
    text.add_layer(layer_4)
    layer_1.add_annotation(base_span=ElementaryBaseSpan(0, 4), a=1)
    layer_1.add_annotation(base_span=ElementaryBaseSpan(6, 9), a=2)
    layer_2.add_annotation(base_span=ElementaryBaseSpan(0, 4), b=3)
    layer_2.add_annotation(base_span=ElementaryBaseSpan(6, 9), b=4)
    compound_base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 9)])
    layer_3.add_annotation(base_span=compound_base_span, c=5)
    layer_4.add_annotation(base_span=compound_base_span, d=6)
    assert layer_4[0].spans is None
    assert layer_4[0].parent is layer_3[0]
    assert layer_3[0].spans == (layer_2[0], layer_2[1])
    assert layer_3[0].parent is None
    assert layer_2[0].spans is None
    assert layer_2[0].parent is layer_1[0]
    assert layer_2[1].spans is None
    assert layer_2[1].parent is layer_1[1]
    assert layer_1[0].spans is None
    assert layer_1[0].parent is None
    assert layer_1[1].spans is None
    assert layer_1[1].parent is None

    # It is possible to define very aggressive scheme for parent and spans attributes
    text = Text('Tere see on piisavalt pikk tekst!')
    layer_1 = Layer('layer_1', attributes=['a'], text_object=text)
    layer_2 = Layer('layer_2', attributes=['b'], text_object=text, parent='layer_1')
    layer_3 = Layer('layer_3', attributes=['c'], text_object=text, enveloping='layer_2')
    layer_4 = Layer('layer_4', attributes=['d'], text_object=text, parent='layer_3')
    text.add_layer(layer_1)
    text.add_layer(layer_2)
    text.add_layer(layer_3)
    text.add_layer(layer_4)
    layer_1.add_annotation(base_span=ElementaryBaseSpan(0, 4), a=1)
    layer_1.add_annotation(base_span=ElementaryBaseSpan(6, 9), a=2)
    layer_2.add_annotation(base_span=ElementaryBaseSpan(0, 4), b=3)
    layer_2.add_annotation(base_span=ElementaryBaseSpan(6, 9), b=4)
    compound_base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(6, 9)])
    layer_3.add_annotation(base_span=compound_base_span, c=5)
    layer_4.add_annotation(base_span=compound_base_span, d=6)
    # A span can have both parent and spans attribute, spans attribute does not have to be closest
    layer_4[0].spans = (layer_1[0], layer_1[1])
    # Parent attribute does not have to respect the layer derivation
    layer_1[0].parent = layer_2[0]
    layer_1[1].parent = layer_2[1]
    layer_3[0].parent = layer_4[0]
    assert layer_4[0].spans == (layer_1[0], layer_1[1])
    assert layer_4[0].parent is layer_3[0]
    assert layer_3[0].spans == (layer_2[0], layer_2[1])
    assert layer_3[0].parent is layer_4[0]
    assert layer_2[0].spans is None
    assert layer_2[0].parent is layer_1[0]
    assert layer_2[1].spans is None
    assert layer_2[1].parent is layer_1[1]
    assert layer_1[0].spans is None
    assert layer_1[0].parent is layer_2[0]
    assert layer_1[1].spans is None
    assert layer_1[1].parent is layer_2[1]


def test_to_record():
    return
    # Normal annotation without an attached span
    annotation = Annotation(span=None)
    assert annotation.to_record(with_text=False) == {'end': None, 'start': None}
    assert annotation.to_record(with_text=True) == {'end': None, 'start': None, 'text': None}

    # Annotation with without an attached span but has same-named attributes
    annotation = Annotation(span=None, to_record=42)
    assert annotation.to_record(with_text=False) == {'end': None, 'start': None, 'to_record': 42}
    assert annotation.to_record(with_text=True) == {'end': None, 'start': None, 'text': None, 'to_record': 42}

    # Annotation with a span that is not mapped to a text object
    layer = Layer('test_layer')
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span)
    assert annotation.to_record(with_text=False) == {'end': 4, 'start': 0}
    assert annotation.to_record(with_text=True) == {'end': 4, 'start': 0, 'text': None}

    # Annotation with a span that is not mapped to a text object but has same-named attributes
    annotation = Annotation(span=span, to_record=42)
    assert annotation.to_record(with_text=False) == {'end': 4, 'start': 0, 'to_record': 42}
    assert annotation.to_record(with_text=True) == {'end': 4, 'start': 0, 'text': None, 'to_record': 42}

    # Annotation with a span that is mapped to a text object
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, attr_1=42, attr_2=43, attr_3=44)
    assert annotation.to_record(with_text=False) == {'end': 4, 'start': 0, 'attr_1': 42, 'attr_2': 43, 'attr_3': 44}
    assert annotation.to_record(with_text=True) == {'end': 4, 'start': 0, 'text': 'Tere',
                                                    'attr_1': 42, 'attr_2': 43, 'attr_3': 44}

    # Annotation with a span that is mapped to a text object but has same-named attributes
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, to_record=42)
    assert annotation.to_record(with_text=False) == {'end': 4, 'start': 0, 'to_record': 42}
    assert annotation.to_record(with_text=True) == {'end': 4, 'start': 0, 'text': 'Tere', 'to_record': 42}

    # Format collision with start, end and text keywords (WRONG RESULT)
    annotation = Annotation(span=None, start=42, end=43, text=44)
    assert annotation.to_record(with_text=False) == {'end': None, 'start': None, 'text': 44}
    assert annotation.to_record(with_text=True) == {'end': None, 'start': None, 'text': None}

    # Format collision with start, end and text keywords (WRONG RESULT)
    annotation = Annotation(span=span, start=42, end=43, text=44)
    assert annotation.to_record(with_text=False) == {'end': 4, 'start': 0, 'text': 44}
    assert annotation.to_record(with_text=True) == {'end': 4, 'start': 0, 'text': 'Tere'}



