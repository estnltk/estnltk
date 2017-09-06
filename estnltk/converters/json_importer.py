import json
from . import import_dict

def _convert_list_to_tuple(d):
    for key, value in d.items():
        if isinstance(value, list):
            d[key] = tuple(value)
    return d

def import_json(json_text:str=None, file:str=None) -> 'Text':
    if file:
        with open(file, 'r') as in_f:
            text_dict = json.load(fp=in_f, object_hook=_convert_list_to_tuple)
    elif json_text:
        text_dict = json.loads(json_text, object_hook=_convert_list_to_tuple)
    else:
        raise TypeError("either 'text_json' or 'file' argument needed")
    return import_dict(text_dict)