from estnltk.text import Text, Layer, SpanList


def import_dict(text_dict:dict) -> Text:
    text = Text(text_dict['text'])
    text.meta = text_dict['meta']
    for record in text_dict['layers']:
        layer = Layer(name=record['name'],
                      attributes=record['attributes'],
                      parent=record['parent'],
                      enveloping=record['enveloping'],
                      ambiguous=record['ambiguous']
                     )
        layer._base = record['_base']
        text[layer.name] = layer
        if layer.parent:
            parent_layer = text[layer._base]
            if layer.ambiguous:                
                for rec in record['spans']:
                    for r in rec:
                        try:
                            span = parent_layer[r['_index_']].mark(layer.name)
                        except NotImplementedError:
                            print(r['_index_'])
                            print(parent_layer[r['_index_']])
                            raise NotImplementedError
                        for attr in layer.attributes:
                            setattr(span, attr, r[attr])
            else:
                for rec in record['spans']:
                    span = parent_layer[rec['_index_']].mark(layer.name)
                    for attr in layer.attributes:
                        setattr(span, attr, rec[attr])
        elif layer.enveloping:
            enveloped_layer = text[layer.enveloping]
            if layer.ambiguous:
                pass # TODO
            else:
                for rec in record['spans']:
                    span = SpanList(layer=layer)
                    for i in rec['_index_']:
                        parent = enveloped_layer[i]
                        span.spans.append(parent)
                    for attr in layer.attributes:
                        setattr(span, attr, rec[attr])
                    layer.add_span(span)
        else:
            layer = layer.from_records(record['spans'], rewriting=True)
    
    return text