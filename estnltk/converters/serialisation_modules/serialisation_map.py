from estnltk.converters.serialisation_modules import legacy_v0
from estnltk.converters.serialisation_modules import default
from estnltk.converters.serialisation_modules import syntax_v0


layer_converter_collection = {legacy_v0.__version__: legacy_v0,
                              default.__version__: default,
                              syntax_v0.__version__: syntax_v0}
