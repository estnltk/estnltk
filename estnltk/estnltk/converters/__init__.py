from .CG3_exporter import export_CG3

from estnltk_core.converters.dict_exporter import annotation_to_dict
from estnltk_core.converters.dict_exporter import text_to_dict
from estnltk_core.converters.layer_dict_converter import layer_to_dict

from estnltk_core.converters.dict_importer import dict_to_annotation
from estnltk_core.converters.dict_importer import dict_to_text
from estnltk_core.converters.layer_dict_converter import dict_to_layer

from estnltk_core.converters.json_converter import to_json
from estnltk_core.converters.json_converter import to_json_file
from estnltk_core.converters.json_converter import from_json
from estnltk_core.converters.json_converter import from_json_file

from estnltk_core.converters.json_exporter import annotation_to_json
from estnltk_core.converters.json_exporter import text_to_json
from estnltk_core.converters.json_exporter import layer_to_json
from estnltk_core.converters.json_exporter import layers_to_json

from estnltk_core.converters.json_importer import json_to_annotation
from estnltk_core.converters.json_importer import json_to_text
from estnltk_core.converters.json_importer import json_to_layer
from estnltk_core.converters.json_importer import json_to_layers

from .TCF_exporter import export_TCF
from .TCF_importer import import_TCF

from .texta_exporter import TextaExporter

# Update serialization map: add syntax & legacy serialization modules
from estnltk_core.converters.serialisation_modules.serialisation_map import layer_converter_collection
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.converters.serialisation_modules import legacy_v0

if 'syntax_v0' not in layer_converter_collection:
    layer_converter_collection['syntax_v0'] = syntax_v0
if 'legacy_v0' not in layer_converter_collection:
    layer_converter_collection['legacy_v0'] = legacy_v0