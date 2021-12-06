from typing import Container, Union, List, Dict, Any

from estnltk_core.common import create_text_object
from estnltk_core.layer.annotation import Annotation
from estnltk_core.converters import layer_dict_converter

from estnltk_core import ElementaryBaseSpan
from estnltk_core import SpanList

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


def records_to_layer(layer: 'Layer', records: List[Dict[str, Any]], rewriting: bool=False) -> 'Layer':
    '''Populates given layer with annotations from given list of records (dicts).
       Technically, records are annotation dicts with extra attributes 'start' and 
       'end' marking the location of the span.
       If rewriting==True, existing annotations of the layer will be overwritten,
       otherwise new annotations will be appended to the layer.
    '''
    if rewriting:
        layer._span_list = SpanList()

    if layer.ambiguous:
        for record_line in records:
            for record in record_line:
                attributes = {attr: record.get(attr, layer.default_values[attr]) for attr in layer.attributes}
                layer.add_annotation(ElementaryBaseSpan(record['start'], record['end']), **attributes)
    else:
        for record in records:
            if record is None:
                continue
            attributes = {attr: record.get(attr, layer.default_values[attr]) for attr in layer.attributes}
            layer.add_annotation(ElementaryBaseSpan(record['start'], end=record['end']), **attributes)
    return layer
