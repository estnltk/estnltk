from typing import Sequence
from estnltk.layer.base_span import ElementaryBaseSpan
from estnltk.layer.layer import Layer


def flatten(input_layer: Layer, output_layer: str, output_attributes: Sequence[str] = None,
            attribute_mapping: Sequence = None, default_values: dict = None) -> Layer:
    """Reduces enveloping layer or layer with parent to a detached ambiguous layer of simple text spans.

    """
    layer_attributes = input_layer.attributes

    output_attributes = output_attributes or layer_attributes
    new_layer = Layer(name=output_layer,
                      attributes=output_attributes,
                      text_object=input_layer.text_object,
                      parent=None,
                      enveloping=None,
                      ambiguous=True,
                      default_values=default_values
                      )

    if attribute_mapping is None:
        attribute_mapping = tuple((attr, attr) for attr in output_attributes)
    else:
        assert {attr for attr, _ in attribute_mapping} <= set(layer_attributes)
        assert {attr for _, attr in attribute_mapping} <= set(output_attributes)

    for span in input_layer:
        for annotation in span.annotations:
            attrs = {new_attr: getattr(annotation, old_attr) for old_attr, new_attr, in attribute_mapping}
            new_layer.add_annotation(ElementaryBaseSpan(span.start, span.end), **attrs)

    return new_layer
