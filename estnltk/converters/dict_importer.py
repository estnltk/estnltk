from typing import Union, Sequence, List, Container

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.layer.base_span import ElementaryBaseSpan
from estnltk.layer.span import Span
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.annotation import Annotation


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
    layer = Layer(name=layer_dict['name'],
                  attributes=layer_dict['attributes'],
                  text_object=text,
                  parent=layer_dict['parent'],
                  enveloping=layer_dict['enveloping'],
                  ambiguous=layer_dict['ambiguous']
                  )
    layer._base = layer_dict['_base']

    if text is None:
        layers = {}
    else:
        layers = text.layers.copy()
    if detached_layers:
        layers.update(detached_layers)

    if layer.parent:
        parent_layer = layers[layer._base]
        if layer.ambiguous:
            for rec in layer_dict['spans']:
                for r in rec:
                    parent = parent_layer[r['_index_']]
                    span = Span(base_span=parent.base_span, parent=parent, layer=layer)
                    span.add_annotation(**{k: list_to_tuple(v) for k, v in r.items()})
                    layer.add_span(span)
        else:
            for rec in layer_dict['spans']:
                layer.add_annotation(Span(base_span=parent_layer[rec['_index_']].base_span, parent=parent_layer[rec['_index_']], layer=layer), **rec)
    elif layer.enveloping:
        enveloped_layer = layers[layer.enveloping]
        if layer.ambiguous:
            for records in layer_dict['spans']:
                for rec in records:
                    spans = [enveloped_layer[i] for i in rec['_index_']]
                    attributes = {attr: list_to_tuple(rec[attr]) for attr in layer.attributes}
                    span = EnvelopingSpan(spans=spans, layer=layer)
                    layer.add_annotation(span, **attributes)
        else:
            for rec in layer_dict['spans']:
                spans = [enveloped_layer[i] for i in rec['_index_']]
                span = EnvelopingSpan(spans=spans, layer=layer)

                attributes = {attr: list_to_tuple(rec[attr]) for attr in layer.attributes}
                span.add_annotation(**attributes)

                layer.add_span(span)
    else:
        layer = layer.from_records(layer_dict['spans'], rewriting=True)
    return layer


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
            text[layer.name] = layer
    return text


def dict_to_text(text_dict: Union[dict, Sequence[dict]], layers: Container = None) -> Union[Text, List[Text]]:
    if isinstance(text_dict, Sequence):
        return [_dict_to_text(td, layers) for td in text_dict]
    return _dict_to_text(text_dict, layers)
