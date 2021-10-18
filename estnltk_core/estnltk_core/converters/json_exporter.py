from typing import Sequence, Union
import json

from . import text_to_dict
from . import layer_to_dict
from . import annotation_to_dict


def annotation_to_json(annotation: Union['Annotation', Sequence['Annotation']], file: str = None,
                       file_encoding: str = 'utf-8'):
    """Exports Annotation or list of Annotation objects to json.
    If file is None, returns json string,
    otherwise dumps json string to file and returns None.

    Note: on the Windows platform, writing a text file
    without specifying the encoding likely raises
    "UnicodeEncodeError: 'charmap' codec can't encode
    character ...", so the parameter file_encoding
    (default: 'utf-8') must be used to reinforce the
    encoding.
    """
    d = annotation_to_dict(annotation)
    if file is None:
        return json.dumps(d, ensure_ascii=False)

    with open(file, 'w', encoding=file_encoding) as out_f:
        json.dump(d, fp=out_f, ensure_ascii=False)


def text_to_json(text: Union['BaseText', 'Text'], file: str = None, file_encoding: str = 'utf-8'):
    """Exports Text or BaseText object to json.
    If file is None, returns json string,
    otherwise dumps json string to file and returns None.
    
    Note: on the Windows platform, writing a text file 
    without specifying the encoding likely raises 
    "UnicodeEncodeError: 'charmap' codec can't encode 
    character ...", so the parameter file_encoding 
    (default: 'utf-8') must be used to reinforce the 
    encoding.
    """
    text_dict = text_to_dict(text)
    if file is None:
        return json.dumps(text_dict, ensure_ascii=False)

    with open(file, 'w', encoding=file_encoding) as out_f:
        json.dump(text_dict, fp=out_f, ensure_ascii=False)


def layer_to_json(layer: 'Layer',
                  file: str = None,
                  file_encoding: str = 'utf-8'):
    """Exports a Layer object to json.

    If file is None, returns json string,
    otherwise dumps json string to file and returns None.

    """
    layer_dict = layer_to_dict(layer)
    if file is None:
        return json.dumps(layer_dict, ensure_ascii=False)

    with open(file, 'w', encoding=file_encoding) as out_f:
        json.dump(layer_dict, fp=out_f, ensure_ascii=False)


def layers_to_json(layers: dict,
                   file: str = None,
                   file_encoding: str = 'utf-8'):
    """Exports a dict of layers to json.

    The dict of layers maps layer names to Layer objects of the same Text 
    (or BaseText) object.

    If file is None, returns json string,
    otherwise dumps json string to file and returns None.

    """
    layers_dict = {name: layer_to_dict(layer) for name, layer in layers.items()}
    if file is None:
        return json.dumps(layers_dict, ensure_ascii=False)

    with open(file, 'w', encoding=file_encoding) as out_f:
        json.dump(layers_dict, fp=out_f, ensure_ascii=False)
