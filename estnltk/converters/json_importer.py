import json
from . import import_dict

def _convert_list_to_tuple(d):
    for key, value in d.items():
        if isinstance(value, list):
            d[key] = tuple(value)
    return d

def import_json(json_text:str=None, file:str=None, file_encoding:str='utf-8') -> 'Text':
    """Imports Text object from json.
    If file is None, then loads corresponding dictionary 
    from json_text, otherwise, loads the dictionary from 
    the json format file. 
    In both cases, the loaded dictionary is finally 
    converted to a Text object, and returned.
    
    Note: on the Windows platform, loading a text file 
    without specifying the encoding likely raises 
    UnicodeEncodeError, so the parameter file_encoding
    (default: 'utf-8') must be used to reinforce the 
    encoding.
    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            text_dict = json.load(fp=in_f, object_hook=_convert_list_to_tuple)
    elif json_text:
        text_dict = json.loads(json_text, object_hook=_convert_list_to_tuple)
    else:
        raise TypeError("either 'text_json' or 'file' argument needed")
    return import_dict(text_dict)