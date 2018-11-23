from typing import Sequence
from estnltk import Span, EnvelopingSpan, Layer


def merge_layers(layers: Sequence[Layer],
                 output_layer: str,
                 output_attributes: Sequence[str],
                 text) -> Layer:
    """
    Creates a new layer spans of which is the union of spans of input layers.
    The input layers must be of the same type (parent, enveloping, ambiguous).
    Missing attribute values are None.
    """
    parent = layers[0].parent
    enveloping = layers[0].enveloping
    #ambiguous = layers[0].ambiguous
    ambiguous = any(layer.ambiguous for layer in layers)

    assert all(layer.parent == parent for layer in layers), \
        "some layers have parent, some don't: " + str({layer.name: layer.parent for layer in layers})
    assert all(layer.enveloping == enveloping for layer in layers), \
        'some layers are enveloping, some are not: ' + str({layer.name: layer.enveloping for layer in layers})
    #assert all(layer.ambiguous == ambiguous for layer in layers),\
    #    'some layers are ambiguous, some are not: ' + str({layer.name: layer.ambiguous for layer in layers})

    new_layer = Layer(
        name=output_layer,
        attributes=tuple(output_attributes),
        text_object=text,
        parent=parent,
        enveloping=enveloping,
        ambiguous=ambiguous
    )

    if enveloping:
        if ambiguous:
            for layer in layers:
                layer_attributes = layer.attributes
                none_attributes = [attr for attr in output_attributes if attr not in layer_attributes]
                for span in iterate_spans(layer):
                    new_span = EnvelopingSpan(spans=span.spans, layer=new_layer)
                    for attr in layer_attributes:
                        setattr(new_span, attr, getattr(span, attr))
                    for attr in none_attributes:
                        setattr(new_span, attr, None)
                    new_layer.add_span(new_span)
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
        if ambiguous:
            for layer in layers:
                layer_attributes = layer.attributes
                none_attributes = [attr for attr in output_attributes if attr not in layer_attributes]
                for amb_span in layer:
                    # TODO: think about this quick fix
                    if isinstance(amb_span, Span):
                        amb_span = [amb_span]
                    for span in amb_span:
                        new_span = Span(span.start, span.end, legal_attributes=output_attributes)
                        for attr in layer_attributes:
                            setattr(new_span, attr, getattr(span, attr))
                        for attr in none_attributes:
                            setattr(new_span, attr, None)
                        new_layer.add_span(new_span)
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


def iterate_spans(layer):
    if layer.ambiguous:
        for ambiguous_span in layer:
            yield from ambiguous_span
    else:
        yield from layer
