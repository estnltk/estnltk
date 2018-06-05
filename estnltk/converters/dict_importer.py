from typing import Union, Sequence, List

from estnltk.text import Text, Layer, Span, EnvelopingSpan


def _dict_to_layer(layer_dict: dict, text: Text) -> Layer:
    layer = Layer(name=layer_dict['name'],
                  attributes=layer_dict['attributes'],
                  parent=layer_dict['parent'],
                  enveloping=layer_dict['enveloping'],
                  ambiguous=layer_dict['ambiguous']
                  )
    layer._base = layer_dict['_base']
    if layer.parent:
        parent_layer = text[layer._base]
        if layer.ambiguous:
            for rec in layer_dict['spans']:
                for r in rec:
                    span = Span(parent=parent_layer[r['_index_']])
                    for attr in layer.attributes:
                        setattr(span, attr, r[attr])
                    layer.add_span(span)
        else:
            for rec in layer_dict['spans']:
                span = parent_layer[rec['_index_']].mark(layer.name)
                for attr in layer.attributes:
                    setattr(span, attr, rec[attr])
    elif layer.enveloping:
        enveloped_layer = text[layer.enveloping]
        if layer.ambiguous:
            for records in layer_dict['spans']:
                for rec in records:
                    spans = [enveloped_layer[i] for i in rec['_index_']]
                    attributes = {attr: rec[attr] for attr in layer.attributes}
                    span = EnvelopingSpan(spans=spans, layer=layer, attributes=attributes)
                    layer.add_span(span)
        else:
            for rec in layer_dict['spans']:
                spans = [enveloped_layer[i] for i in rec['_index_']]
                #attributes = {attr: rec['attr'] for attr in layer.attributes}
                span = EnvelopingSpan(spans=spans, layer=layer)
                for attr in layer.attributes:
                    setattr(span, attr, rec[attr])
                layer.add_span(span)
    else:
        layer = layer.from_records(layer_dict['spans'], rewriting=True)
    return layer


def dict_to_layer(layer_dict: dict, text: Text) -> Union[Layer, List[Layer]]:
    if isinstance(layer_dict, (list, tuple)) and isinstance(text, (list, tuple)):
        assert len(layer_dict) == len(text)
        return [_dict_to_layer(ld, t) for ld, t in zip(layer_dict, text)]
    return _dict_to_layer(layer_dict, text)


def _dict_to_text(text_dict: dict) -> Text:
    text = Text(text_dict['text'])
    text.meta = text_dict['meta']
    for layer_dict in text_dict['layers']:
        layer = dict_to_layer(layer_dict, text)
        text[layer.name] = layer

    return text


def dict_to_text(text_dict: Union[dict, Sequence[dict]]) -> Union[Text, List[Text]]:
    if isinstance(text_dict, Sequence):
        return [_dict_to_text(td) for td in text_dict]
    return _dict_to_text(text_dict)