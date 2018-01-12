from typing import List, Dict, Callable, Generator
from estnltk.spans import Span, SpanList
from estnltk.layer import Layer


def merge_layers(layers: List[Layer], layer_name: str, attributes: List[str]) -> Layer:
    """
    Creates a new layer spans of which is the union of spans of input layers.
    The input layers must be of the same type (parent, enveloping, ambiguous).
    Missing attribute values are None.
    """
    # TODO: merge ambiguous layers
    parent = layers[0].parent
    enveloping = layers[0].enveloping
    ambiguous = layers[0].ambiguous
    assert all(layer.parent == parent for layer in layers)
    assert all(layer.enveloping == enveloping for layer in layers)
    assert all(layer.ambiguous == ambiguous for layer in layers)

    new_layer = Layer(
        name=layer_name,
        attributes=attributes,
        parent=parent,
        enveloping=enveloping,
        ambiguous=ambiguous
    )

    if enveloping:
        for layer in layers:
            layer_attributes = layer.attributes
            none_attributes = [attr for attr in attributes if attr not in layer_attributes]
            for span in layer:
                new_span = SpanList()
                new_span.spans = span
                for attr in layer_attributes:
                    setattr(new_span, attr, getattr(span, attr))
                for attr in none_attributes:
                    setattr(new_span, attr, None)
                new_layer.add_span(new_span)
    elif parent:
        # TODO: merge layers with parent
        raise NotImplemented('merge of layers with parent is not yet implemented')
    else:
        for layer in layers:
            layer_attributes = layer.attributes
            none_attributes = [attr for attr in attributes if attr not in layer_attributes]
            for span in layer:
                new_span = Span(span.start, span.end, legal_attributes=attributes)
                for attr in layer_attributes:
                    setattr(new_span, attr, getattr(span, attr))
                for attr in none_attributes:
                    setattr(new_span, attr, None)
                new_layer.add_span(new_span)

    return new_layer


def combine_layers(a: List[Dict], b: List[Dict], fun: Callable[[Dict, Dict], Dict]) -> Generator:
    """
    Generator of merged layers.

    Parameters
    ----------
    a and b: iterable of dict
        Iterable of Estnltk layer elements. Must be ordered by *(start, end)*.

    fun: merge function
        Function that merges two layer elements. Must accept one None value.
        Example::

            def fun(x, y):
                if x is None:
                    return y
                return x

    Yields
    ------
    dict
        Merged layer elements.
    """
    a = iter(a)
    b = iter(b)
    a_end = False
    b_end = False
    try:
        x = next(a)
    except StopIteration:
        a_end = True
    try:
        y = next(b)
    except StopIteration:
        b_end = True

    while not a_end and not b_end:
        if x.start < y.start or x.start == y.start and x.end < y.end:
            yield fun(x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.start == y.start and x.end == y.end:
            yield fun(x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield fun(None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True

    if a_end and b_end:
        return

    if a_end:
        while True:
            yield fun(None, y)
            y = next(b)

    if b_end:
        while True:
            yield fun(x, None)
            x = next(a)
