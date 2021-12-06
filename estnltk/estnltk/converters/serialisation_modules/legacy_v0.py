from typing import Union

from estnltk_core.layer.layer import Layer
from estnltk_core.layer.span import Span
from estnltk_core.layer.annotation import Annotation
from estnltk_core.converters import records_to_layer
from estnltk_core.converters import layer_to_records

__version__ = 'legacy_v0'


def layer_to_dict(layer: Layer) -> dict:
    assert '_index_' not in layer.attributes
    layer_dict = {'name': layer.name,
                  'attributes': layer.attributes,
                  'parent': layer.parent,
                  '_base': None,
                  'enveloping': layer.enveloping,
                  'ambiguous': layer.ambiguous,
                  'spans': []}
    if layer.parent:
        parent_layer = layer.text_object[layer.parent]
        records = layer_to_records( layer )
        last_index = 0
        for span, record in zip(layer, records):
            if layer.ambiguous:
                index = parent_layer.index(span.parent, last_index)
                for rec in record:
                    rec['_index_'] = index
            else:
                index = parent_layer.index(span.parent, last_index)
                record['_index_'] = index
            last_index = index
            layer_dict['spans'].append(record)
    elif layer.enveloping:
        enveloped_layer = layer.text_object[layer.enveloping]

        records = []
        last_index = 0
        for enveloping_span in layer:
            if layer.ambiguous:
                ambiguous_record = []
                index = [enveloped_layer.index(span, last_index) for span in enveloping_span.spans]
                for annotation in enveloping_span.annotations:
                    last_index = index[0]
                    record = {attr: getattr(annotation, attr) for attr in layer.attributes}
                    record['_index_'] = index
                    ambiguous_record.append(record)
                records.append(ambiguous_record)
            else:
                index = [enveloped_layer.index(span, last_index) for span in enveloping_span]
                last_index = index[0]
                record = {attr: getattr(enveloping_span, attr) for attr in layer.attributes}
                record['_index_'] = index
                records.append(record)
        layer_dict['spans'] = records
    else:
        layer_dict['spans'] = layer_to_records( layer )

    return layer_dict


def dict_to_layer(layer_dict: dict, text: Union['BaseText', 'Text']) -> Layer:
    layer = Layer(name=layer_dict['name'],
                  attributes=layer_dict['attributes'],
                  text_object=text,
                  parent=layer_dict['parent'],
                  enveloping=layer_dict['enveloping'],
                  ambiguous=layer_dict['ambiguous']
                  )

    if layer.parent:
        parent_layer = text[layer.parent]
        if layer.ambiguous:
            for rec in layer_dict['spans']:
                parent = parent_layer[rec[0]['_index_']]
                span = Span(parent.base_span, layer)
                for r in rec:
                    attributes = {attr: r[attr] for attr in layer.attributes}
                    span.add_annotation(Annotation(span, **attributes))
                layer.add_span(span)
        else:
            for rec in layer_dict['spans']:
                # layer.add_annotation(parent_layer[rec['_index_']].base_span, **rec)
                layer.add_annotation(Span(base_span=parent_layer[rec['_index_']].base_span, layer=layer), **rec)
    elif layer.enveloping:
        enveloped_layer = text[layer.enveloping]
        if layer.ambiguous:
            for records in layer_dict['spans']:
                for rec in records:
                    spans = [enveloped_layer[i] for i in rec['_index_']]
                    attributes = {attr: rec[attr] for attr in layer.attributes}
                    layer.add_annotation(spans, **attributes)
        else:
            for rec in layer_dict['spans']:
                spans = [enveloped_layer[i] for i in rec['_index_']]
                attributes = {attr: rec[attr] for attr in layer.attributes}

                layer.add_annotation(spans, **attributes)
    else:
        layer = records_to_layer( layer, layer_dict['spans'], rewriting=True )
    return layer