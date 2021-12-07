from typing import Union, List

from estnltk_core.layer.annotation import Annotation
from estnltk_core.common import load_text_class
from estnltk_core.converters import layer_dict_converter


def annotation_to_dict(annotation: Annotation) -> dict:
    if isinstance(annotation, Annotation):
        return dict(annotation)
    raise TypeError('expected Annotation, got {}'.format(type(annotation)))


def text_to_dict(text: Union['BaseText', 'Text']) -> dict:
    assert isinstance( text, load_text_class() ), type(text)
    text_dict = {'text': text.text,
                 'meta': text.meta,
                 'layers': []}
    for layer in text.sorted_layers():
        text_dict['layers'].append(layer_dict_converter.layer_to_dict(layer))
    return text_dict

