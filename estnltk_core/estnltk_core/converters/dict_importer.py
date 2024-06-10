from typing import Container, Union

from estnltk_core.common import create_text_object
from estnltk_core.layer.annotation import Annotation
from estnltk_core.converters import layer_dict_converter


def dict_to_annotation(span, annotation_dict: dict):
    return Annotation(span, **annotation_dict)


def dict_to_text(text_dict: dict, layers: Container = None) -> Union['BaseText', 'Text']:
    text = create_text_object( text_dict['text'] )
    text.meta = text_dict['meta']
    # Restore all layer objects
    layer_objects = {}
    # span layers
    for layer_dict in text_dict['layers']:
        if layers is None or layer_dict['name'] in layers:
            layer = layer_dict_converter.dict_to_layer(layer_dict, text)
            if layer_dict['serialisation_module'] == 'legacy_v0':
                # Hack for legacy serialization 
                # (in legacy, dict_to_layer relies on previously added layers)
                text.add_layer(layer)
            else:
                # Normal serialization
                layer_objects[layer.name] = layer
    if 'relation_layers' in text_dict:
        # Restore relation layers (available starting from version 1.7.2+)
        for layer_dict in text_dict['relation_layers']:
            if layers is None or layer_dict['name'] in layers:
                layer = layer_dict_converter.dict_to_layer(layer_dict, text)
                layer_objects[layer.name] = layer
    # Add layers in the topological order
    for layer in text.__class__.topological_sort(layer_objects):
        text.add_layer(layer)
    return text

