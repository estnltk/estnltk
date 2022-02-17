#   
#   This is a registry for serialisation modules. 
#   Basic serialisation functions (such as text_to_json(...) and json_to_text(...)) are
#   defined in the estnltk_core package, but used commonly across all the packages
#   of EstNLTK. 
#   Other packages of EstNLTK also extend the serialisation possibilities. 
#   In order to make serialisation extensions usable across all the packages of EstNLTK, 
#   we use a global serialisation registry, which is defined in estnltk_core and
#   updated in other packages. 
#
from types import ModuleType

class SerialisationRegistry:
    def __init__(self):
        self._layer_converters = {}

    def __setitem__(self, serialisation_module_name:str, serialisation_module: ModuleType):
        self._layer_converters[serialisation_module_name] = serialisation_module

    def __getitem__(self, serialisation_module_name:str):
        if serialisation_module_name in self:
            return self._layer_converters[serialisation_module_name]
        raise ValueError('serialisation module not registered: ' + serialisation_module_name)

    def __contains__(self, serialisation_module_name:str):
        return serialisation_module_name in self._layer_converters.keys()

    def keys(self):
        return list(self._layer_converters.keys())

# Note: do not add default serialisation to the registry.
# default serialisation is always used when serialisation module is unspecified.
# do not use 'default' to call out default serialisation module
SERIALISATION_REGISTRY = SerialisationRegistry()
"""
This is a registry for serialisation modules. 
Basic serialisation functions (such as text_to_json(...) and json_to_text(...)) are 
defined in the estnltk_core package, but used commonly across all the packages 
of EstNLTK. 
Other packages of EstNLTK also extend the serialisation possibilities. 
In order to make serialisation extensions usable across all the packages of EstNLTK, 
we use a global serialisation registry, which is defined in estnltk_core and 
updated in other packages. 
"""