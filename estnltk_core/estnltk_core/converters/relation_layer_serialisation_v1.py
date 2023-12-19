from typing import Union

__version__ = 'relations_v1'

from estnltk_core.layer.relation_layer import to_relation_base_span
from estnltk_core.layer.relation_layer import RelationLayer


def layer_to_dict(layer: RelationLayer) -> dict:
    return {
        'name': layer.name,
        'span_names': layer.span_names,
        'attributes': layer.attributes,
        'secondary_attributes': layer.secondary_attributes,
        'display_order': layer.display_order,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'serialisation_module': __version__,
        'meta': layer.meta,
        'relations': [{'named_spans': {named_span.name: named_span.base_span.raw() \
                                                        for named_span in relation.spans},
                       'annotations': [dict(annotation) for annotation in relation.annotations]}
                       for relation in layer]
    }


def dict_to_layer(layer_dict: dict, text: Union['BaseText', 'Text']) -> RelationLayer:
    layer = RelationLayer(name=layer_dict['name'],
                          span_names=layer_dict['span_names'],
                          attributes=layer_dict['attributes'],
                          secondary_attributes=layer_dict['secondary_attributes'],
                          display_order=layer_dict.get('display_order', ()),
                          enveloping=layer_dict.get('enveloping', None),
                          ambiguous=layer_dict['ambiguous'],
                          text_object=text)
    layer.meta.update(layer_dict['meta'])

    for relation_dict in layer_dict['relations']:
        named_spans = [ (k, to_relation_base_span(v)) \
                         for k, v in relation_dict['named_spans'].items() ]
        for annotation in relation_dict['annotations']:
            relation_annotation_dict = annotation.copy()
            for span_name, base_span in named_spans:
                assert span_name not in relation_annotation_dict.keys()
                relation_annotation_dict[span_name] = base_span
            layer.add_annotation( relation_annotation_dict )
    return layer
