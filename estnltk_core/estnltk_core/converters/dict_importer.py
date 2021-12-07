from typing import Container, Union

from estnltk_core.common import create_text_object
from estnltk_core.layer.annotation import Annotation
from estnltk_core.converters import layer_dict_converter


def dict_to_annotation(span, annotation_dict: dict):
    return Annotation(span, **annotation_dict)


def dict_to_text(text_dict: dict, layers: Container = None) -> Union['BaseText', 'Text']:
    text = create_text_object( text_dict['text'] )
    text.meta = text_dict['meta']
    for layer_dict in text_dict['layers']:
        if layers is None or layer_dict['name'] in layers:
            layer = layer_dict_converter.dict_to_layer(layer_dict, text)
            text.add_layer(layer)
    return text

