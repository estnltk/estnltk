from typing import List, Mapping, Union, Sequence
from estnltk.text import Text
from estnltk.converters.layer_dict_converters import layer_dict_converter


def annotation_to_dict(annotation: Union['Annotation', Sequence['Annotation']]) -> Union[dict, List[dict]]:
    if isinstance(annotation, Mapping):
        return dict(annotation)
    if isinstance(annotation, Sequence):
        return [dict(a) for a in annotation]
    raise TypeError('expected Annotation or Sequence of Annotations, got {}'.format(type(annotation)))


def _layer_to_dict(layer: 'Layer') -> dict:
    return layer_dict_converter.layer_to_dict(layer)


def _text_to_dict(text: Text) -> dict:
    assert isinstance(text, Text), type(text)
    text_dict = {'text': text.text,
                 'meta': text.meta,
                 'layers': []}
    for layer in text.list_layers():
        text_dict['layers'].append(_layer_to_dict(layer))
    return text_dict


def layer_to_dict(layer: Union[Sequence['Layer'], 'Layer']):
    if isinstance(layer, Sequence):
        return [_layer_to_dict(l) for l in layer]
    return _layer_to_dict(layer)


def text_to_dict(text: Union['Text', Sequence['Text']]) -> Union[dict, List[dict]]:
    if isinstance(text, Sequence):
        return [_text_to_dict(t) for t in text]
    return _text_to_dict(text)
