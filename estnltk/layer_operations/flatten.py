from typing import Sequence
from estnltk.layer.span import Span
from estnltk.layer.layer import Layer


def flatten(layer: Layer, layer_name: str, attributes: Sequence[str]=None) -> Layer:
    """
    Reduces enveloping layer or layer with parent to layer of simple text spans.
    """
    if attributes is None:
        attributes = layer.attributes
    new_layer = Layer(
        name=layer_name,
        attributes=attributes,
        parent=None,
        enveloping=None,
        ambiguous=False
    )

    layer_attributes = layer.attributes
    for span in layer:
        new_span = Span(span.start, span.end, legal_attributes=attributes)
        for attr in layer_attributes:
            setattr(new_span, attr, getattr(span, attr))
        new_layer.add_span(new_span)

    return new_layer
