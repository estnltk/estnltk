from estnltk.converters import from_json_file, to_json_file, dict_to_text, text_to_dict


def legacy_to_current_json(input_file, output_file):
    """Converts file in legacy json format to current json format.

    """
    legacy_dict = from_json_file(input_file)
    to_json_file(text_to_dict(dict_to_text(legacy_dict)), output_file)
