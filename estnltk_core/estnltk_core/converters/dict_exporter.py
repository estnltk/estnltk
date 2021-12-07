import warnings
from typing import Union, List, Dict, Any

from estnltk_core.layer.annotation import Annotation
from estnltk_core.common import load_text_class
from estnltk_core.converters import layer_dict_converter

from estnltk_core import Span, EnvelopingSpan

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


def layer_to_records(layer: 'Layer', with_text: bool=False) -> \
                          Union[ List[Dict[str, Any]], List[List[Dict[str, Any]]], List[List[List[Dict[str, Any]]]] ]:
    '''Exports annotations of given layer as records. Technically, 
       records are annotation dicts with extra attributes 'start' 
       and 'end' marking the location of the span. Depending on the
       structure of layer (ambiguous or enveloping layer), records 
       are nested inside 1 to 3 lists.
       If with_text==True, then records also contain an extra attribute
       'text' carrying textual content of each span.
    '''
    return [span_to_records(span, with_text) for span in layer._span_list]


def span_to_records(span: Union[Span, EnvelopingSpan], with_text: bool=False) -> \
                          Union[ Dict[str, Any], List[Dict[str, Any]], List[List[Dict[str, Any]]] ]:
    '''Exports annotations of given span or enveloping span as records. 
       Technically, records are annotation dicts with extra attributes 
       'start' and 'end' marking the location of the span. Depending 
       on the structure of layer (ambiguous or enveloping layer), records 
       can be nested inside 1 to 2 lists. 
       If with_text==True, then records also contain an extra attribute
       'text' carrying textual content of each span.
    '''
    if isinstance(span, EnvelopingSpan):
        if len(span._layer.attributes) > 0:
            warnings.warn( ("(!) Annotations of the enveloping span won't be added to the record. ")+\
                            "Please use layer_to_dict/text_to_dict functions for complete dictionary export.")
        return [span_to_records(s, with_text) for s in span.spans]
    elif isinstance(span, Span):
        records = []
        for annotation in span.annotations:
            record = {k: annotation[k] for k in span._layer.attributes}
            if with_text:
                record['text'] = span.text
            record['start'] = span.start
            record['end'] = span.end
            records.append( record )
        if span._layer.ambiguous:
            return records
        else:
            return records[0]
    return TypeError('Expected Span or EnvelopingSpan, but got {}'.format(type(span)))

