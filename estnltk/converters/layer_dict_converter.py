from estnltk.converters.serialisation_modules import default_v0
from estnltk.converters.serialisation_modules import default_v1
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.layer.layer import LAYER_DICT_CONVERTER_V0
from estnltk.layer.layer import LAYER_DICT_CONVERTER_V1
from estnltk.layer.layer import SYNTAX_LAYER_DICT_CONVERTER_V0


layer_converter_collection = {LAYER_DICT_CONVERTER_V0: default_v0,
                              LAYER_DICT_CONVERTER_V1: default_v1,
                              SYNTAX_LAYER_DICT_CONVERTER_V0: syntax_v0}


def layer_to_dict(layer):
    converter = layer.serialisation_module
    return layer_converter_collection[converter].layer_to_dict(layer)


def dict_to_layer(layer_dict: dict, text_object=None):
    converter = layer_converter_collection[layer_dict.get('serialisation_module', LAYER_DICT_CONVERTER_V0)]
    return converter.dict_to_layer(layer_dict, text_object)
