import pytest
from copy import copy, deepcopy

import estnltk
from estnltk import Text
from estnltk import Layer
from estnltk import ElementaryBaseSpan


def test_len():
    # Invalid layer object does not create infinite recursion
    layer = Layer.__new__(Layer)
    with pytest.raises(AttributeError):
        _ = len(layer)

    # Length of an empty layer
    layer = Layer(name='layer', attributes=['a', 'b'], default_values=dict(a=5, b='str'), ambiguous=True)
    assert len(layer) == 0

    # Length of a nonempty layer
    layer.add_annotation(ElementaryBaseSpan(0, 4), a=1, b='*')
    assert len(layer) == 1
    layer.add_annotation(ElementaryBaseSpan(5, 7), a=2, b='*')
    assert len(layer) == 2
    base_span = ElementaryBaseSpan(8, 10)
    layer.add_annotation(base_span, a=3, b='*')
    assert len(layer) == 3
    layer.add_annotation(base_span, a=4, b='*')
    assert len(layer) == 3


def test_copy_constructors():
    # Copying of detached layers
    layer = Layer(
        name='empty_layer',
        attributes=['a', 'b'],
        text_object=None,
        parent=None,
        enveloping=None,
        ambiguous=True,
        default_values=dict(a=5, b='str'),
        serialisation_module=estnltk.converters.serialisation_modules.syntax_v0
    )
    layer.meta = {'count': 5}

    s_copy = copy(layer)
    assert s_copy is not layer
    assert s_copy.name is layer.name
    assert s_copy.parent is layer.parent
    assert s_copy.enveloping is layer.enveloping
    assert s_copy.ambiguous is layer.ambiguous
    assert s_copy.serialisation_module is layer.serialisation_module
    # ???

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

    d_copy = deepcopy(layer)
    assert d_copy.text_object is not layer.text_object
    assert d_copy.text_object == layer.text_object

    # Copying of a simple nonempty layer
    layer = Layer('nonempty_layer', attributes=['a', 'b'])
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
    assert d_copy.text_object is not layer.text_object
    assert d_copy.text_object == layer.text_object
    assert d_copy._span_list is not layer._span_list
    assert len(d_copy._span_list) == len(layer._span_list)
    for i in range(len(d_copy._span_list)):
        assert d_copy[i] is not layer[i]
        assert d_copy[i].base_span is layer[i].base_span
        assert d_copy[i] == layer[i]

    # Copying of a simple nonempty layer with recursive meta
    layer = Layer('recursive_meta', attributes=['a', 'b'])
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
    layer = Layer('recursive_layer', attributes=['text', 'layer', 'espan'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=layer)
    layer[0].espan = layer[0]
    layer.add_annotation(ElementaryBaseSpan(5, 8), text=text, layer=text.nonempty_layer, espan=text.nonempty_layer[0])
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
    # assert d_copy.text_object == layer.text_object infinite recursion, lets skip deep levels
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
    # assert d_copy[0].espan is d_copy[0], "Fails as Span deep copy is incorrect"
    assert d_copy[1]['text'] is d_copy.text_object
    assert d_copy[1].layer is d_copy.text_object.nonempty_layer, "Fails as layers deep copy is incorrect"
    # assert text['text'][0].espan is d_copy.nonempty_layer[0], "Fails as layers deep copy is incorrect"

# test recursion ftroug Layer.attributes

    # WTF layer['layer_name'] ??

