from typing import Union, Sequence, List, Container

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.layer.annotation import Annotation
from estnltk.converters.serialisation_modules import layer_dict_converter


def list_to_tuple(value):
    if isinstance(value, list):
        return tuple(value)
    return value


def _dict_to_annotation(span, annotation_dict: dict):
    return Annotation(span, **annotation_dict)


def dict_to_annotation(d: Union[dict, Sequence[dict]], span) -> Union[Annotation, List[Annotation]]:
    if isinstance(d, Sequence):
        return [_dict_to_annotation(span, ad) for ad in d]
    return _dict_to_annotation(span, d)


def _dict_to_layer(layer_dict: dict, text: Text, detached_layers) -> Layer:
    return layer_dict_converter.dict_to_layer(layer_dict, text)


def dict_to_layer(layer_dict: dict, text: Text = None, detached_layers=None) -> Union[Layer, List[Layer]]:
    if isinstance(layer_dict, (list, tuple)) and isinstance(text, (list, tuple)):
        if detached_layers is None:
            detached_layers = [None] * len(layer_dict)
        assert len(layer_dict) == len(text) == len(detached_layers)
        return [_dict_to_layer(ld, t, dl) for ld, t, dl in zip(layer_dict, text, detached_layers)]
    return _dict_to_layer(layer_dict, text, detached_layers)


def _dict_to_text(text_dict: dict, layers: Container = None) -> Text:
    text = Text(text_dict['text'])
    text.meta = text_dict['meta']
    for layer_dict in text_dict['layers']:
        if layers is None or layer_dict['name'] in layers:
            layer = dict_to_layer(layer_dict, text)
            text.add_layer(layer)
    return text


def dict_to_text(text_dict: Union[dict, Sequence[dict]], layers: Container = None) -> Union[Text, List[Text]]:
    if isinstance(text_dict, Sequence):
        return [_dict_to_text(td, layers) for td in text_dict]
    return _dict_to_text(text_dict, layers)
