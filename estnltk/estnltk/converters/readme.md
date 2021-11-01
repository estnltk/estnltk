# Converters

'estnltk-core' provides functions for converting between EstNLTK's basic data structures (Text, Layer, Annotation) and dictionary and JSON formats. These functions are listed in the [`__init__.py`](__init__.py) file.

The folder [`serialisation_modules`](serialisation_modules) contains additional modules for layer to dict and dict to layer conversions:

* `legacy_v0` -- convert legacy layers used in EstNLTK's versions 1.6.0b to 1.6.3b;

* `syntax_v0` -- convert a syntactic analysis layer that has additional 'parent_span' and 'children' attributes; 

Note: if you add a new serialisation module, you should also update the global serialization registry, see the file  [`__init__.py`](__init__.py) for details.

Other converters listed here provide either application specific data import/export (e.g Weblicht TCF), or import from/export to specific markup format (e.g CONLL, CG3).  

## Text <-> CG3

`cg3_annotation_parser` -- functions for parsing VISL CG3 format lines; mainly used in importing morphological and syntactic data from .cg3 files;

`CG3_exporter` -- converts Text with morph_extended layer to cg3 format;

`CG3_importer` -- restores Text objects from cg3 format files;

## Text <-> CONLL

`conll_exporter` -- converts Text with syntactic analysis layer to CONLL format;

`conll_importer` -- restores Text objects with syntactic analysis layers from CONLL format files;

`conll_ner_exporter` -- converts Text object with named entity layer to CONLL format;

`conll_ner_importer` -- restores Text objects with named entity layers from CONLL format files;


## Text <-> TCF

`TCF_exporter` -- exports Text to TCF XML format for Weblicht service;

`TCF_importer` -- imports Text objects from Weblicht's TCF XML format;


