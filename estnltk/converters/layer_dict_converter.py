from estnltk.converters.serialisation_modules import legacy_v0
from estnltk.converters.serialisation_modules import default
from estnltk.converters.serialisation_modules import syntax_v0


layer_converter_collection = {legacy_v0.__version__: legacy_v0,
                              default.__version__: default,
                              syntax_v0.__version__: syntax_v0}


def layer_to_dict(layer):
    converter = layer.serialisation_module
    if converter is None:
        converter = default.__version__
    return layer_converter_collection[converter].layer_to_dict(layer)


def dict_to_layer(layer_dict: dict, text_object=None):
    converter = layer_converter_collection[layer_dict.get('serialisation_module', legacy_v0.__version__)]
    return converter.dict_to_layer(layer_dict, text_object)
