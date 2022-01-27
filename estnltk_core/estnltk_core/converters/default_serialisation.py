from typing import Union

from estnltk_core.layer.base_layer import to_base_span
from estnltk_core.layer.layer import Layer


def layer_to_dict(layer: Layer) -> dict:
    return {
        'name': layer.name,
        'attributes': layer.attributes,
        'secondary_attributes': layer.secondary_attributes,
        'parent': layer.parent,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'serialisation_module': None,
        'meta': layer.meta,
        'spans': [{'base_span': span.base_span.raw(),
                   'annotations': [dict(annotation) for annotation in span.annotations]}
                  for span in layer]
    }


def dict_to_layer(layer_dict: dict, text: Union['BaseText', 'Text']) -> Layer:
    layer = Layer(name=layer_dict['name'],
                  attributes=layer_dict['attributes'],
                  secondary_attributes=layer_dict.get('secondary_attributes', ()),
                  text_object=text,
                  parent=layer_dict['parent'],
                  enveloping=layer_dict['enveloping'],
                  ambiguous=layer_dict['ambiguous'],
                  )
    layer.meta.update(layer_dict['meta'])

    for span_dict in layer_dict['spans']:
        base_span = to_base_span(span_dict['base_span'])
        for annotation in span_dict['annotations']:
            layer.add_annotation(base_span, **annotation)

    return layer
