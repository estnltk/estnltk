from typing import List, Mapping, Union, Sequence
from estnltk.text import Text


def annotation_to_dict(annotation: Union['Annotation', Sequence['Annotation']]) -> Union[dict, List[dict]]:
    if isinstance(annotation, Mapping):
        return dict(annotation)
    if isinstance(annotation, Sequence):
        return [dict(a) for a in annotation]
    raise TypeError('expected Annotation or Sequence of Annotations, got {}'.format(type(annotation)))


def _layer_to_dict(layer: 'Layer', text: 'Text') -> dict:
    assert '_index_' not in layer.attributes
    layer_dict = {'name': layer.name,
                  'attributes': layer.attributes,
                  'parent': layer.parent,
                  '_base': layer._base,
                  'enveloping': layer.enveloping,
                  'ambiguous': layer.ambiguous,
                  'spans': []}
    if layer.parent:
        parent_spanlist = text[layer._base].span_list
        records = layer.to_records()
        last_index = 0
        for span, record in zip(layer, records):
            if layer.ambiguous:
                index = parent_spanlist.index(span.parent, last_index)
                for rec in record:
                    rec['_index_'] = index
            else:
                index = parent_spanlist.index(span.parent, last_index)
                record['_index_'] = index
            last_index = index
            layer_dict['spans'].append(record)
    elif layer.enveloping:
        enveloped_spanlist = text[layer.enveloping].span_list

        records = []
        last_index = 0
        for enveloping_span in layer:
            if layer.ambiguous:
                ambiguous_record = []
                index = [enveloped_spanlist.index(span, last_index) for span in enveloping_span.spans]
                for annotation in enveloping_span.annotations:
                    last_index = index[0]
                    record = {attr: getattr(annotation, attr) for attr in layer.attributes}
                    record['_index_'] = index
                    ambiguous_record.append(record)
                records.append(ambiguous_record)
            else:
                index = [enveloped_spanlist.index(span, last_index) for span in enveloping_span]
                last_index = index[0]
                record = {attr: getattr(enveloping_span, attr) for attr in layer.attributes}
                record['_index_'] = index
                records.append(record)
        layer_dict['spans'] = records
    else:
        layer_dict['spans'] = layer.to_records()

    return layer_dict


def _text_to_dict(text: Text) -> dict:
    assert isinstance(text, Text), type(text)
    text_dict = {'text': text.text,
                 'meta': text.meta,
                 'layers': []}
    for layer in text.list_layers():
        text_dict['layers'].append(_layer_to_dict(layer, text))
    return text_dict


def layer_to_dict(layer: Union[Sequence['Layer'], 'Layer'], text: Union[Sequence['Text'], 'Text']):
    if isinstance(layer, Sequence) and isinstance(text, Sequence):
        assert len(layer) == len(text)
        return [_layer_to_dict(l, t) for l, t in zip(layer, text)]
    return _layer_to_dict(layer, text)


def text_to_dict(text: Union['Text', Sequence['Text']]) -> Union[dict, List[dict]]:
    if isinstance(text, Sequence):
        return [_text_to_dict(t) for t in text]
    return _text_to_dict(text)
