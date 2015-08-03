============
Estonian wikipedia dump json to estnltk.Text object importer
============================================================

Usage
-----

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
The top level layers are:
data, external_links, internal_links, sections, text.
Data contains categories, (list of) references, infobox, timestamp, title, url.
::
    {
    "data": {
        "categories": [
            "Oguusi keeled",
            "Aserbaid\u017eaan",
            "Turgi keeled"
        ],
        "infobox": [
            {
                "keelkond": "turgi keeledoguusi keeled'''aserbaid\u017eaani keel'''",
                "keelkonnav\u00e4rv": "altai",
                "kood 1": "az",
                "kood 2": "aze",
                "piirkond": "Kaukaasia",
                "riigid": "Aserbaid\u017eaanis, Iraanis, Gruusias, Venemaal, T\u00fcrgis",
                "riik": "Aserbaid\u017eaan}}",
                "r\u00e4\u00e4kijad": "45-50 miljonit"
            }
        ],
        "timestamp": "2014-02-18T19:43:10Z",
        "title": "Aserbaid\u017eaani keel",
        "url": "http://et.wikipedia.org/wiki/Aserbaid\u017eaani_keel"
    },

Links are now top level, recalculated to point to whole concatenated article text and point to obj[text] level.
::
    "external_links": [
        {
            "end": 948,
            "label": "Vikipeedia aserbaid\u017eaani keeles",
            "start": 917,
            "url": "http://az.wikipedia.org"
        }
    ],
    "internal_links": [
        {
            "end": 57,
            "label": "turgi keelte",
            "start": 45,
            "title": "turgi keeled",
            "url": "http://et.wikipedia.org/wiki/turgi_keeled"
        }..

Sections contains start and end point of sections, title, images, references, but not section text itself.
::
       "sections": [
        {
            "end": 801,
            "images": [
                {
                    "text": "pisi",
                    "url": "http://et.wikipedia.org/wiki/Pilt:Idioma_azer\u00ed.png"
                }
            ],
            "start": 0
        },

Text is a separate layer all the sections concatenated with section titles.
{start}Title
SectionText{end}

{start}Title2
Section2Text{end}
::
       "text": "Aserbaid\u017eaani keel\nAserbaid\u017eaani keel kuulub turgi keelte hulka. Peale Aserbaid\u017eaani k\u00f5neldakse seda Gruusias, Armeenias, Iraanis, Iraagis ja T\u00fcrgis.\nAserbaid\u017eaani keel kuulub oguusi keelte hulka,