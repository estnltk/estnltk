from estnltk_core.converters.default_serialisation import layer_to_dict as default_layer_to_dict
from estnltk_core.converters.default_serialisation import dict_to_layer as default_dict_to_layer
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
import estnltk_core.converters.relation_layer_serialisation_v0 as relations_serialisation

# Update global serialization registry: add default relations_serialisation
if relations_serialisation.__version__ not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY[relations_serialisation.__version__] = relations_serialisation


def layer_to_dict(layer):
    if layer.serialisation_module is None:
        return default_layer_to_dict(layer)

    if layer.serialisation_module in SERIALISATION_REGISTRY:
        return SERIALISATION_REGISTRY[layer.serialisation_module].layer_to_dict(layer)

    raise ValueError('serialisation module not registered in serialisation map: ' + layer.serialisation_module)


def dict_to_layer(layer_dict: dict, text_object=None, serialisation_module=None):
    if serialisation_module is None:
        serialisation_module = layer_dict.get('serialisation_module')

    # nothing is specified, we run default
    if serialisation_module is None:
        return default_dict_to_layer(layer_dict, text_object)

    if serialisation_module in SERIALISATION_REGISTRY:
        return SERIALISATION_REGISTRY[serialisation_module].dict_to_layer(layer_dict, text_object)

    raise ValueError('serialisation module not registered in serialisation map: ' + serialisation_module)
