from estnltk_core.converters import from_json_file, to_json_file, dict_to_text, text_to_dict
from estnltk.converters.serialisation_modules import legacy_v0

def legacy_to_current_json(input_file, output_file):
    """Converts file in legacy json format to current json format.
    """
    legacy_dict = from_json_file(input_file)
    if 'layers' in legacy_dict.keys():
        # Note: Normally, layers of legacy_v0 json do not have the "serialisation_module" attribute.
        # We need to assign that explicitly to get the converter working
        for layer_dict in legacy_dict['layers']:
            layer_dict["serialisation_module"] = legacy_v0.__version__
    to_json_file(text_to_dict(dict_to_text(legacy_dict)), output_file)
