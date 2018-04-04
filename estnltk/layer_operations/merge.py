from typing import Sequence
from estnltk import Span, SpanList
from estnltk.layer.layer import Layer


def merge_layers(layers: Sequence[Layer],
                 output_layer: str,
                 output_attributes: Sequence[str]) -> Layer:
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
        name=output_layer,
        attributes=tuple(output_attributes),
        parent=parent,
        enveloping=enveloping,
        ambiguous=ambiguous
    )

    if enveloping:
        for layer in layers:
            layer_attributes = layer.attributes
            none_attributes = [attr for attr in output_attributes if attr not in layer_attributes]
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
            none_attributes = [attr for attr in output_attributes if attr not in layer_attributes]
            for span in layer:
                new_span = Span(span.start, span.end, legal_attributes=output_attributes)
                for attr in layer_attributes:
                    setattr(new_span, attr, getattr(span, attr))
                for attr in none_attributes:
                    setattr(new_span, attr, None)
                new_layer.add_span(new_span)

    return new_layer
