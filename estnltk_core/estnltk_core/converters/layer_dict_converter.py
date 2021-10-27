from estnltk_core.converters.default_serialisation import layer_to_dict as default_layer_to_dict
from estnltk_core.converters.default_serialisation import dict_to_layer as default_dict_to_layer
from .serialisation_modules.serialisation_map import layer_converter_collection


def layer_to_dict(layer):
    if layer.serialisation_module is None:
        return default_layer_to_dict(layer)

    if layer.serialisation_module in layer_converter_collection:
        return layer_converter_collection[layer.serialisation_module].layer_to_dict(layer)

    raise ValueError('serialisation module not registered in serialisation map: ' + layer.serialisation_module)


def dict_to_layer(layer_dict: dict, text_object=None, serialisation_module=None):
    if serialisation_module is None:
        serialisation_module = layer_dict.get('serialisation_module')

    # nothing is specified, we run default
    if serialisation_module is None:
        return default_dict_to_layer(layer_dict, text_object)

    if serialisation_module in layer_converter_collection:
        return layer_converter_collection[serialisation_module].dict_to_layer(layer_dict, text_object)

    raise ValueError('serialisation module not registered in serialisation map: ' + serialisation_module)
