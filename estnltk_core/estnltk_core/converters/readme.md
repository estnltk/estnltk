# Basic converters

## Text or BaseText, Layer, Annotation <-> dict

* `default_serialisation.py` -- the default serialisation module; provides default functions for converting between layers and dictionaries;

* `serialisation_registry.py` -- global serialisation registry, which makes layer serialisation extensions usable across all the packages of EstNLTK;

* `layer_dict_converter.py` -- provides main functions for converting between layers and dictionaries; combines together the default serialisation and serialisation extensions available in the global serialisation registry; 

* `dict_exporter.py` -- functions for converting annotations and `Text` objects into dictionaries;

* `dict_importer.py` -- functions for restoring annotations and `Text` objects from dictionaries;

## Text or BaseText, Layer, Annotation <-> json

* `json_converter.py` -- functions for converting between dictionary objects and JSON objects (strings), and for importing JSON objects to files/exporting JSON objects from files;

* `json_exporter.py` -- functions for converting annotations, layers and `Text` objects into JSON objects;

* `json_importer.py` -- functions for restoring annotations, layers and `Text` objects from JSON objects;

## unicode string <-> binary

* `unicode_binary.py` -- functions for converting between unicode strings and binary (encoded) strings. These conversions are required in communicating with external processes, such as Java programs;

