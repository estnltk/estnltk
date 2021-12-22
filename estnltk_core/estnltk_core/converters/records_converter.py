import warnings
from typing import Union, List, Dict, Any

from estnltk_core.layer.layer import Layer
from estnltk_core import Annotation
from estnltk_core import ElementaryBaseSpan
from estnltk_core import SpanList
from estnltk_core import EnvelopingSpan
from estnltk_core import Span

def layer_to_records(layer: Layer, with_text: bool=False) -> \
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


def records_to_layer(layer: Layer, records: Union[ List[Dict[str, Any]], List[List[Dict[str, Any]]] ], 
                                     rewriting: bool=False) -> Layer:
    '''Imports given layer's annotations from records. Technically, records are 
       annotation dicts with extra attributes 'start' and 'end' marking the 
       location of the span. Depending on the structure of layer (ambiguous or not), 
       records can be nested inside 1 or 2 lists. 
       If rewriting==True, existing annotations of the layer will be overwritten,
       otherwise new annotations will be appended to the layer.
       Note: this conversion does not work on enveloping layers.
    '''
    if layer.enveloping is not None:
        raise NotImplementedError('(!) records_to_layer has not been implemented for enveloping layers!'+\
                                  'Please use dict_to_layer/dict_to_text functions for complete dictionary import.')
    if rewriting:
        layer.clear_spans()

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

