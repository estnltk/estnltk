# Converters

'estnltk-core' provides functions for converting between EstNLTK's basic data structures (Text, Layer, Annotation) and dictionary and JSON formats. These functions are listed in the [`__init__.py`](__init__.py) file.

The folder [`serialisation_modules`](serialisation_modules) contains additional modules for layer to dict and dict to layer conversions:

* `legacy_v0` -- convert legacy layers used in EstNLTK's versions 1.6.0b to 1.6.3b;

* `syntax_v0` -- convert a syntactic analysis layer that has additional 'parent_span' and 'children' attributes; 

Note: if you add a new serialisation module, you should also update the global serialization registry, see the file  [`__init__.py`](__init__.py) for details.

Other converters listed here provide either application specific data import/export (e.g Weblicht TCF), or import from/export to specific markup format (e.g CONLL, CG3).  

* [`cg3`](cg3) -- tools for converting Text objects with morph_extended layer to cg3 format, and for restoring annotated Text objects from cg3 format files. Also includes helpers, such as converting from cg3 format to conll format; 

* [`tcf`](tcf) -- tools for converting Text objects to  Weblicht's [TCF XML format](https://weblicht.sfs.uni-tuebingen.de/weblichtwiki/index.php/The_TCF_Format), and restoring Text objects from the same format;

* [`conll`](conll) -- tools for importing Text objects from CONLL format files, and exporting to the same format. Allow to export/import syntactic analysis annotations, and named entity annotations;

* [`label_studio`](label_studio) -- tools for exporting Text objects' annotations to [Labelstudio](https://labelstud.io/) format, and importing back from the same format. Currently supported tasks: phrase labelling, text/sentence/word classification;