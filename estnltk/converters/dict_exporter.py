def layer_to_dict(layer, text):
    assert '_index_' not in layer.attributes
    layer_dict = {'name':layer.name,
                  'attributes': layer.attributes,
                  'parent': layer.parent,
                  '_base': layer._base,
                  'enveloping': layer.enveloping,
                  'ambiguous': layer.ambiguous,
                  'spans': []}
    if layer.parent:
        parent_spanlist = text[layer._base].spans
        records = layer.to_records()
        for span, record in zip(layer, records):
            index = parent_spanlist.index(span)
            if layer.ambiguous:
                for rec in record:
                    rec['_index_'] = index
            else:
                record['_index_'] = index
            layer_dict['spans'].append(record)
    elif layer.enveloping:
        enveloped_spanlist = text[layer.enveloping].spans
        
        records = []
        for spanlist in layer:
            index = [enveloped_spanlist.index(span) for span in spanlist]
            if layer.ambiguous:
                pass
                # TODO:
            else:
                record = {attr:getattr(spanlist, attr) for attr in layer.attributes}
                record['_index_'] = index
                records.append(record)
        layer_dict['spans'] = records
    else:
        layer_dict['spans'] = layer.to_records()
    
    return layer_dict


def export_dict(text):
    text_dict = {'text':text.text, 'layers':[]}
    for layer in text.list_layers():
        text_dict['layers'].append(layer_to_dict(layer, text))
    return text_dict
