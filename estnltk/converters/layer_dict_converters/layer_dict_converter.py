from . import default_v0
from . import default_v1
from . import syntax_v0

DEFAULT_LAYER_DICT_CONVERTER = default_v1
DEFAULT_SYNTAX_LAYER_DICT_CONVERTER = 'syntax_v0'

layer_converter_collection = {None: default_v0,
                              'default_v0': default_v0,
                              DEFAULT_LAYER_DICT_CONVERTER.__version__: DEFAULT_LAYER_DICT_CONVERTER,
                              DEFAULT_SYNTAX_LAYER_DICT_CONVERTER: syntax_v0}


def layer_to_dict(layer):
    converter = layer.meta.get('dict_converter')
    return layer_converter_collection[converter].layer_to_dict(layer)


def dict_to_layer(layer_dict: dict, text_object=None):
    converter = layer_converter_collection[layer_dict.get('meta', {}).get('dict_converter')]
    return converter.dict_to_layer(layer_dict, text_object)
