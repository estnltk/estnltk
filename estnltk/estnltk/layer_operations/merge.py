from typing import Sequence
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.layer import Layer


def merge_layers(layers: Sequence[Layer],
                 output_layer: str,
                 output_attributes: Sequence[str],
                 text=None) -> Layer:
    """Creates a new layer spans of which is the union of spans of input layers.
    The input layers must be of the same type (parent, enveloping, ambiguous).
    Missing attribute values are None.

    """
    parent = layers[0].parent
    enveloping = layers[0].enveloping
    ambiguous = any(layer.ambiguous for layer in layers)

    assert all(layer.parent == parent for layer in layers), \
        "some layers have parent, some don't: " + str({layer.name: layer.parent for layer in layers})
    assert all(layer.enveloping == enveloping for layer in layers), \
        'some layers are enveloping, some are not: ' + str({layer.name: layer.enveloping for layer in layers})

    text_object = None
    for layer in layers:
        if layer.text_object is not None:
            text_object = layer.text_object
            break
    assert text is None or text is text_object
    text_object = text_object or text

    new_layer = Layer(
        name=output_layer,
        attributes=tuple(output_attributes),
        text_object=text_object,
        parent=parent,
        enveloping=enveloping,
        ambiguous=ambiguous
    )

    if enveloping:
        if ambiguous:
            for layer in layers:
                for span in layer:
                    for annotation in span.annotations:
                        new_layer.add_annotation(span, **annotation)
        # TODO: remove else part, delete if ambiguous
        else:
            for layer in layers:
                layer_attributes = layer.attributes
                none_attributes = [attr for attr in output_attributes if attr not in layer_attributes]
                for span in layer:
                    new_span = EnvelopingSpan(spans=span, layer=new_layer)
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
            for span in layer:
                for annotation in span.annotations:
                    new_layer.add_annotation(span.base_span, **annotation)

    return new_layer


def iterate_spans(layer):
    if layer.ambiguous:
        for ambiguous_span in layer:
            yield from ambiguous_span
    else:
        yield from layer
