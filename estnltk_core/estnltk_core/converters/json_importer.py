from typing import Union
from collections.abc import Iterable
import json

from . import dict_to_annotation
from . import dict_to_layer
from . import dict_to_text


def json_to_text(json_text: str = None, file: str = None, file_encoding: str = 'utf-8') -> Union['BaseText', 'Text']:
    """Imports Text or BaseText object from json.
    If file is None, then loads corresponding dictionary 
    from json_text, otherwise, loads the dictionary from 
    the json format file. 
    In both cases, the loaded dictionary is finally 
    converted to a Text (or BaseText) object, and 
    returned.
    
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


def json_to_layer(texts: Union[list, 'BaseText', 'Text'], json_str: str = None, file: str = None, file_encoding: str = 'utf-8'):
    """Imports Layer object from json.
    The `texts` parameter must be a text object associated 
    with the layer. 
    If file is `None`, then loads corresponding dictionary 
    from json_str, otherwise, loads the dictionary from the 
    `file` in json format. In both cases, the loaded 
    dictionary is finally converted to a Layer object, and 
    returned. 
    
    Note: for backwards compatibility, you can also import 
    a list of Layer objects from json. In that case, the 
    `texts` parameter must be a list of Text objects, and 
    `json_str` (or `file`) must contain a list of layer 
    objects in JSON format. 
    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            layer_dict_list = json.load(fp=in_f)
    elif json_str:
        layer_dict_list = json.loads(json_str)
    else:
        raise TypeError("either 'json_str' or 'file' argument needed")
    if isinstance(layer_dict_list, dict) and not isinstance(texts, Iterable):
        # Convert a single Layer object
        return dict_to_layer(layer_dict_list, texts)
    else:
        # Check that arguments have proper / matching types
        if isinstance(layer_dict_list, dict) and \
           isinstance(texts, Iterable):
            raise TypeError('(!) Conflicting texts and json_str: '+\
                            'json_str should contain a list of layer dicts, not a single dict.')
        if not isinstance(layer_dict_list, dict) and \
           isinstance(layer_dict_list, Iterable) and \
           not isinstance(texts, Iterable):
            raise TypeError('(!) Conflicting texts and json_str: '+\
                            'texts should be a list of Text objects, not {}'.format(type(texts)))
        if len(layer_dict_list) != len(texts):
            raise ValueError('(!) Mismatching numbers of texts and layers: '+\
                              ('{} vs {}'.format(len(texts), len(layer_dict_list) )) )
    return [dict_to_layer(layer_dict, text) for layer_dict, text in zip(layer_dict_list, texts)]


def json_to_layers(text: Union['BaseText', 'Text'], json_str: str = None, file: str = None, file_encoding: str = 'utf-8'):
    """Imports a dict of layers of the same Text or BaseText object from json.
    If file is None, then loads corresponding dictionary
    from json_str, otherwise, loads the dictionary from
    the `file` in json format.
    In both cases, the loaded dictionary is finally
    converted to a list of Layer objects, and returned.

    """
    if file:
        with open(file, 'r', encoding=file_encoding) as in_f:
            layer_dict = json.load(fp=in_f)
    elif json_str:
        layer_dict = json.loads(json_str)
    else:
        raise TypeError("either 'json_str' or 'file' argument needed")
    return {name: dict_to_layer(layer, text) for name, layer in layer_dict.items()}


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
