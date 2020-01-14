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
    # Only spans can be assigned as parents
    layer = Layer('test_layer')
    span = Span(base_span=base_span, layer=layer)
    span.parent = 5




    # Self-looping through parent attribute is not allowed
    text = Text('Tere!')
    base_span = ElementaryBaseSpan(0, 4)
    layer = Layer('test_layer', attributes=['a', 'b', 'c'], ambiguous=True, text_object=text)
    span = Span(base_span=base_span, layer=layer)
    with pytest.raises(ValueError, match="an invalid 'parent' value: self-loops are not allowed."):
        span.parent = span


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




