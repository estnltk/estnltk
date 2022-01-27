#
#  merge -- vertical merging of layers
#
from typing import Sequence, Union
from estnltk_core.layer.enveloping_span import EnvelopingSpan
from estnltk_core.layer.base_layer import BaseLayer


def merge_layers(layers: Sequence[Union[BaseLayer, 'Layer']],
                 output_layer: str,
                 output_attributes: Sequence[str],
                 text=None) -> Union[BaseLayer, 'Layer']:
    """Creates a new layer spans of which is the union of spans of input layers.
    The input layers must be of the same type (parent, enveloping, ambiguous), 
    and they must cover the same Text object.
    Missing attribute values are None.

    """
    parent = layers[0].parent
    enveloping = layers[0].enveloping
    ambiguous = any(layer.ambiguous for layer in layers)
    secondary_attributes = layers[0].secondary_attributes

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
    
    if text_object is not None:
        assert all(layer.text_object == text_object for layer in layers), \
            "some layers belong to different text objects: " + \
                str( [layer.name for layer in layers if layer.text_object != text_object] )

    new_layer = layers[0].__class__(
        name=output_layer,
        attributes=tuple(output_attributes),
        secondary_attributes=secondary_attributes,
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


