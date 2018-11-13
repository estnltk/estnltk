from typing import Sequence
from estnltk.layer.span import Span
from estnltk.layer.layer import Layer


def flatten(input_layer: Layer, output_layer: str, output_attributes: Sequence[str]=None,
            attribute_mapping: Sequence=None, default_values: dict = None) -> Layer:
    """
    Reduces enveloping layer or layer with parent to a detached ambiguous layer of simple text spans.
    """
    layer_attributes = input_layer.attributes

    output_attributes = output_attributes or layer_attributes
    text_object = input_layer.text_object
    new_layer = Layer(name=output_layer,
                      attributes=output_attributes,
                      text_object=text_object,
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

    if input_layer.ambiguous:
        for span in input_layer:
            new_span = Span(span.start, span.end, text_object=text_object)
            for a in span:
                attrs = {new_attr: getattr(a, old_attr) for old_attr, new_attr, in attribute_mapping}
                new_layer.add_annotation(new_span, **attrs)
    else:
        for span in input_layer:
            new_span = Span(span.start, span.end, text_object=text_object)
            attrs = {new_attr: getattr(span, old_attr) for old_attr, new_attr in attribute_mapping}
            new_layer.add_annotation(new_span, **attrs)

    return new_layer
