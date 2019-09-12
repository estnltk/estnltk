from estnltk.converters import serialisation_modules
from estnltk.converters.serialisation_modules import legacy_v0
from estnltk.converters.serialisation_modules import default
from estnltk.converters.serialisation_modules import syntax_v0


layer_converter_collection = {legacy_v0.__version__: legacy_v0,
                              default.__version__: default,
                              syntax_v0.__version__: syntax_v0}


def layer_to_dict(layer):
    if layer.serialisation_module is None:
        return serialisation_modules.default.layer_to_dict(layer)

    if layer.serialisation_module in layer_converter_collection:
        return layer_converter_collection[layer.serialisation_module].layer_to_dict(layer)

    raise ValueError('serialisation module not registered in serialisation map: ' + layer.serialisation_module)


def dict_to_layer(layer_dict: dict, text_object=None, serialisation_module=None):
    if serialisation_module is None:
        serialisation_module = layer_dict.get('serialisation_module')

    # nothing is specified, we run default
    if serialisation_module is None:
        # check for legacy format
        # TODO: to be removed by rewriting tests
        if 'meta' not in layer_dict:
            return serialisation_modules.legacy_v0.dict_to_layer(layer_dict, text_object)
        return serialisation_modules.default.dict_to_layer(layer_dict, text_object)

    if serialisation_module in layer_converter_collection:
        return layer_converter_collection[serialisation_module].dict_to_layer(layer_dict, text_object)

    raise ValueError('serialisation module not registered in serialisation map: ' + serialisation_module)
