import json
from . import export_dict

def export_json(text:'Text', file:str=None):
    """
    Exports text object to json.
    If file is None, returns json string,
    otherwise dumps json string to file and returns None.
    """
    text_dict = export_dict(text)
    if file:
        with open(file, 'w') as out_f:
            json.dump(text_dict, fp=out_f, ensure_ascii=False)
    else:
        return json.dumps(text_dict, ensure_ascii=False)
