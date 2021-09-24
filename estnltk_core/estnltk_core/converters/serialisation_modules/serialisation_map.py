from estnltk_core.converters.serialisation_modules import legacy_v0
from estnltk_core.converters.serialisation_modules import syntax_v0

# default resolver is allwais called when serialisation module is unspecified
# do not use 'default' to call out default serialisation module
layer_converter_collection = {'legacy_v0': legacy_v0,
                              'syntax_v0': syntax_v0}
