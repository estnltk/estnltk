from pandas import DataFrame

def repr_html(layer, file=None):
    res = []
    if layer.ambiguous:
        for record in layer.to_records(True):
            first = True
            for rec in record:
                if not first:
                    rec['text'] = ''                    
                res.append(rec)
                first = False
    else:
        res = layer.to_records(True)
    df = DataFrame.from_records(res, columns=['text',]+list(layer.attributes))
    if file:
        df.to_html(file)
    return df
