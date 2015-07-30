============
Estonian wikipedia dump json to estnltk.Text object importer
============

Usage
-------------------

Again, the program is intended to be run from command line::

    usage: json2Text.py [-h] [-v] I O

    Import etWikiParsed wikipedia json files to estnltk.Text objects

    positional arguments:
      I              directory of json files
      O              wikipedia dump file relative or full path

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  Print written article titles and count.



From code you can do::
    from estnltk.wiki.json_2_text import json_2_text

    in = #input directory w parsed wikipedia .json files
    out = #output directory of Text objects with somewhat restructured layers

    json_2_text(in, out)

Structure
-------------------
