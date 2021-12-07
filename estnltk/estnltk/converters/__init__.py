from estnltk_core.converters.dict_exporter import annotation_to_dict
from estnltk_core.converters.dict_exporter import text_to_dict
from estnltk_core.converters import layer_to_records
from estnltk_core.converters import span_to_records
from estnltk_core.converters.layer_dict_converter import layer_to_dict

from estnltk_core.converters.dict_importer import dict_to_annotation
from estnltk_core.converters.dict_importer import dict_to_text
from estnltk_core.converters import records_to_layer
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

from estnltk.converters.cg3.CG3_exporter import export_CG3
from estnltk.converters.cg3.CG3_importer import import_CG3

from estnltk.converters.tcf.TCF_exporter import export_TCF
from estnltk.converters.tcf.TCF_importer import import_TCF

# Update global serialization registry: add syntax & legacy serialization modules
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.converters.serialisation_modules import legacy_v0

if 'syntax_v0' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['syntax_v0'] = syntax_v0
if 'legacy_v0' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['legacy_v0'] = legacy_v0