import json

from . import dict_to_annotation
from . import dict_to_layer
from . import dict_to_text


def json_to_text(json_text: str = None, file: str = None, file_encoding: str = 'utf-8') -> 'Text':
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
            text_dict = json.load(fp=in_f)
    elif json_text:
        text_dict = json.loads(json_text)
    else:
        raise TypeError("either 'text_json' or 'file' argument needed")
    return dict_to_text(text_dict)


def json_to_texts(json_text: str = None, file: str = None, file_encoding: str = 'utf-8') -> 'Text':
    """Imports Text objects from json.

    If file is None, then loads corresponding list dictionaries
    from json_text, otherwise, loads the list of dictionaries from
    the json format file.
    In both cases, the list of loaded dictionaries is finally
    converted to a list of Text objects, and returned.

    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            return [dict_to_text(d) for d in json.load(fp=in_f)]
    if json_text:
        return [dict_to_text(d) for d in json.loads(json_text)]
    raise TypeError("either 'text_json' or 'file' argument needed")


def import_text_list_json(json_text: str=None, file: str=None, file_encoding: str='utf-8'):
    """Imports list of Text objects from json.
    If file is None, then loads corresponding dictionary
    from json_text, otherwise, loads the dictionary from
    the json format file.
    In both cases, the loaded dictionary is finally
    converted to a Text object, and returned.
    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            text_dict_list = json.load(fp=in_f)
    elif json_text:
        text_dict_list = json.loads(json_text)
    else:
        raise TypeError("either 'text_json' or 'file' argument needed")
    return [dict_to_text(text_dict) for text_dict in text_dict_list]


def json_to_layer(texts, json_str: str = None, file: str = None, file_encoding: str = 'utf-8'):
    """Imports list of Layer objects from json.
    If file is None, then loads corresponding dictionary
    from json_str, otherwise, loads the dictionary from
    the `file` in json format.
    In both cases, the loaded dictionary is finally
    converted to a list of Layer objects, and returned.
    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            layer_dict_list = json.load(fp=in_f)
    elif json_str:
        layer_dict_list = json.loads(json_str)
    else:
        raise TypeError("either 'json_str' or 'file' argument needed")
    return [dict_to_layer(layer_dict, text) for layer_dict, text in zip(layer_dict_list, texts)]


def json_to_layers(texts, json_str: str = None, file: str = None, file_encoding: str = 'utf-8'):
    """Imports list of Layer objects from json.

    If file is None, then loads corresponding dictionary
    from json_str, otherwise, loads the dictionary from
    the `file` in json format.
    In both cases, the loaded dictionary is finally
    converted to a list of Layer objects, and returned.

    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            layer_dict_list = json.load(fp=in_f)
    elif json_str:
        layer_dict_list = json.loads(json_str)
    else:
        raise TypeError("either 'json_str' or 'file' argument needed")
    return [dict_to_layer(layer_dict, text) for layer_dict, text in zip(layer_dict_list, texts)]


def json_to_annotation(span, json_str: str = None, file: str = None, file_encoding: str = 'utf-8'):
    """Imports list of Layer objects from json.
    If file is None, then loads corresponding dictionary
    from json_str, otherwise, loads the dictionary from
    the `file` in json format.
    In both cases, the loaded dictionary is finally
    converted to a list of Layer objects, and returned.
    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            layer_dict_list = json.load(fp=in_f)
    elif json_str:
        layer_dict_list = json.loads(json_str)
    else:
        raise TypeError("either 'json_str' or 'file' argument needed")
    return dict_to_annotation(span, layer_dict_list)
