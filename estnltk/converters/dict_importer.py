from estnltk.text import Text, Layer, Span, SpanList


def dict_to_layer(layer_dict: dict, text: Text) -> Layer:
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
                    span = layer.add_span(Span(parent=parent_layer[r['_index_']]))
                    for attr in layer.attributes:
                        setattr(span, attr, r[attr])
        else:
            for rec in layer_dict['spans']:
                span = parent_layer[rec['_index_']].mark(layer.name)
                for attr in layer.attributes:
                    setattr(span, attr, rec[attr])
    elif layer.enveloping:
        enveloped_layer = text[layer.enveloping]
        if layer.ambiguous:
            pass  # TODO
        else:
            for rec in layer_dict['spans']:
                span = SpanList(layer=layer)
                for i in rec['_index_']:
                    parent = enveloped_layer[i]
                    span.spans.append(parent)
                for attr in layer.attributes:
                    setattr(span, attr, rec[attr])
                layer.add_span(span)
    else:
        layer = layer.from_records(layer_dict['spans'], rewriting=True)
    return layer


def import_dict(text_dict: dict) -> Text:
    text = Text(text_dict['text'])
    text.meta = text_dict['meta']
    for layer_dict in text_dict['layers']:
        layer = dict_to_layer(layer_dict, text)
        text[layer.name] = layer

    return text
