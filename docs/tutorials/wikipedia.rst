========================================
Working with Estonian and Võru wikipedia
========================================
.. highlight:: python

Wikipedia is a free-access, free-content Internet encyclopedia, supported and hosted by the non-profit Wikimedia Foundation.
Those who can access the site can edit most of its articles, with the expectation that they follow the website's policies.
Wikipedia is ranked among the ten most popular websites and constitutes the Internet's largest and most popular general reference work.

Estonian version of the Wikipedia has over 130 000 articles as of 2015.
Võru dialect has also its own version containing about 5000 articles.


Downloading the Wikipedia dumps
===============================

Latest Estonian wikipedia:

http://dumps.wikimedia.org/etwiki/latest/etwiki-latest-pages-articles.xml.bz2

Latest Võru dialect wikipedia:

http://dumps.wikimedia.org/fiu_vrowiki/latest/fiu_vrowiki-latest-pages-articles.xml.bz2

It takes some work to turn the dumps into usable form, so if you don't want to do all of this by yourself,
you can download fully prepared (but older) articles (see :ref:`links_to_processed_wiki_dumps`).


.. _extracting_xml_articles:

Extracting articles from XML files
==================================

Let's assume you have downloaded both the Estonian and Võru wikipedia into ``wikidump`` subfolder and extracted the ``.xml`` files,
so that you have two files::

    wikidump/etwiki-latest-pages-articles.xml
    wikidump/fiu_vrowiki-latest-pages-articles.xml.bz2


Estnltk comes with a tool that can extract all the articles from the XML files and store them as JSON::

    $ python3 -m estnltk.wiki.parser -h
    usage: parser.py [-h] [-v] D I

    Parse Estonian Wikipedia dump file to Article Name.json files in a specified
    folder

    positional arguments:
      D              full path to output directory for the json files
      I              wikipedia dump file full path

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  Print written article titles and count.


To use it, let's create separate subfolders to both Estonian and Võru articles::

    mkdir wikidump/eesti
    mkdir wikidump/voru

And run the parser::

    python3 -m estnltk.wiki.parser wikidump/eesti/ wikidump/etwiki-latest-pages-articles.xml
    python3 -m estnltk.wiki.parser wikidump/voru/ wikidump/fiu_vrowiki-latest-pages-articles.xml.bz2


As a result, there will be many ``.json`` files with structure described in section :ref:`wiki_json_structure`.
NB! See section :ref:`wiki_convert` on how to access the articles using Estnltk.


.. _wiki_json_structure:

Json structure
--------------

The basic structure of an article.json::

    {
        "timestamp": "2015-03-22T08:25:09Z",
        "title": "Algriim",
        "url": "http://et.wikipedia.org/wiki/Algriim"
        "categories": [
          "Folkloristika",
          "Foneetika",
          "Kirjandusteadus"
    ],
        "sections": [
        {
            "text": "Algriim on sõnade algushäälikute koosõla, mida...",
            "internal_links": [
                {
                    "end": 32,
                    "label": "häälikute",
                    "start": 23,
                    "title": "häälik",
                    "url": "http://et.wikipedia.org/wiki/häälik"
                },
                {
                    "end": 112,
                    "label": "alliteratsiooniks",
                    "start": 95,
                    "title": "alliteratsioon",
                    "url": "http://et.wikipedia.org/wiki/alliteratsioon"

                },
             "external links": [
                {
                    "end": 125,
                    "label": "Suvine sats sõdurpoisse sõitis sõjaväkke",
                    "start": 85,
                    "url": "http://www.tartupostimees.ee/901454/suvine-sats-sodurpoisse-soitis-sojavakke/"
                }
            ],
                }


Sections
--------
The first section is always introduction and doesn´t have a title.

A section is a nested structure, if a section has subsections, they can be accessed like this::

    obj['sections'][0]['sections']

Other
-----

Other elements include objects like wikipedia templates in the form of::

    {{templatename|parameter1|etc}}

    "other": [
        "{{See artikkel| räägib üldmõistest; Herodotose teose kohta vaata artiklit [[Historia]]}}",
        "{{ToimetaAeg|kuu=oktoober|aasta=2012}}",
        "{{keeletoimeta}}"
    ]



References
----------

If there are references they are added as a top level field::

    "references": [
        {
            "text": "Kõiv, Mait. Inimene, ühiskond, kultuur. I osa: vanaaeg. 2006. Lk. 8."
        }
    ]

Each section has (if it has references) has a reference field in the form of::

    "references": [
                0
            ],
     "text": "Ajalugu (kreeka keeles  - \"historia\", mis ..."
        },

Internal Links
--------------

Internal links point to articles in et.wikipedia.org/wiki/.
Link parsing works if the brackets are balanced 99.99% of the time they are, on rare occasions (1/15000 files) can happen that internal links inside external link labels are not balanced correctly. Parser just ignores this.
::

            "internal_links": [
                {
                    "end": 15,
                    "label": "Tartu ülikoolis",
                    "start": 0,
                    "title": "Tartu ülikool",
                    "url": "http://et.wikipedia.org/wiki/Tartu_ülikool"
                },
                {
                    "end": 70,
                    "label": "Juri Lotman",
                    "start": 59,
                    "title": "Juri Lotman",
                    "url": "http://et.wikipedia.org/wiki/Juri_Lotman"
                },
                {
                    "end": 101,
                    "label": "kultuurisemiootika",
                    "start": 83,
                    "title": "kultuurisemiootika",
                    "url": "http://et.wikipedia.org/wiki/kultuurisemiootika"
                },
                {
                    "end": 134,
                    "label": "Tartu-Moskva koolkonna",
                    "start": 112,
                    "title": "Tartu-Moskva koolkond",
                    "url": "http://et.wikipedia.org/wiki/Tartu-Moskva_koolkond"
                },
                {
                    "end": 216,
                    "label": "Sign Systems Studies",
                    "start": 196,
                    "title": "Sign Systems Studies",
                    "url": "http://et.wikipedia.org/wiki/Sign_Systems_Studies"
                },
                {
                    "end": 290,
                    "label": "1964",
                    "start": 286,
                    "title": "1964",
                    "url": "http://et.wikipedia.org/wiki/1964"
                },
                {
                    "end": 325,
                    "label": "Tartu ülikooli semiootika osakond",
                    "start": 292,
                    "title": "Tartu üikooli semiootika osakond",
                    "url": "http://et.wikipedia.org/wiki/Tartu_ülikooli_semiootika_osakond"
                },
                {
                    "end": 343,
                    "label": "1992",
                    "start": 339,
                    "title": "1992",
                    "url": "http://et.wikipedia.org/wiki/1992"
                }
            ],
            "text": "Tartu ülikoolis tegutses rahvusvaheliselt tuntud semiootik Juri Lotman, kes on üks kultuurisemiootika rajajaid. Tartu-Moskva koolkonna kultuurisemiootika traditsiooni kannab Tartus ilmuv ajakiri \"Sign Systems Studies\", mis asutati (kui \"Trudy po znakovym sistemam – Semeiotike\") aastal 1964.\nTartu ülikooli semiootika osakond loodi aastal 1992.",
            "title": "Semiootika Tartus"


Text formatting
---------------
Bold/italics/bulletlists are marked in the dump, but are reformated as plain-text in json. Quotes, newlines are preserved.

Tables
------
Tables are under the corresponding section, separeted from text although unparsed (Json has /n instead of an actual newline)::

 "tables": [

		"<table>
		<tr><td>
		Andorra jaguneb 7 vallaks (''parròquia''):
		* [[Andorra la Vella]]
		* [[Canillo vald]]
		* [[Encampi vald]]
		* [[Escaldes-Engordany vald]]
		* [[La Massana vald]]
		* [[Ordino vald]]
		* [[Sant Julià de Lòria vald]]
		</td>
		<td>
		[[Pilt:Andora.png|250px]]</td></table>",

		"{| class="wikitable"\n! colspan="8" |Armeenia peamised asulad<br />2012. aasta andmed<ref>[http://www.armstat.am/file/doc/99471428.pdf www.armstat.am - GENERAL DESCRIPTION - ОБЩИЙ ОБЗОР]</ref>\n|-\n! # !! Linn !! Maakond !! Elanikke !! # !! Linn !! Maakond !! Elanikke \n|-\n! 1 \n| [[Jerevan]] || – || 1&#160;127&#160;300 \n! 11\n| Charentsavan || [[Kotajkhi maakond|Kotajkh]] || 25&#160;200 \n|-\n! 2\n| [[Gjumri]] || [[Širaki maakond|Širak]] || 145&#160;900 \n! 12\n| [[Sevan]] || [[Gegharkhunikhi maakond|Gegharkhunikh]] || 23&#160;500 \n|-\n! 3\n| [[Vanadzor]] || [[Lori maakond|Lori]] || 104&#160;900 \n! 13\n| [[Goris]] || [[Sjunikhi maakond|Sjunikh]] || 23&#160;100 \n|-\n! 4\n| [[Vagharšapat]] || [[Armaviri maakond|Armavir]] || 57&#160;800 \n! 14\n| [[Masis]] || [[Ararati maakond|Ararat]] || 22&#160;700 \n|-\n! 5\n| [[Hrazdan]] || [[Kotajkhi maakond|Kotajkh]] || 53&#160;700 \n! 15\n| [[Aštarak]] || [[Aragatsotni maakond|Aragatsotn]] || 21&#160;700 \n|-\n! 6\n| [[Abovjan]] || [[Kotajkhi maakond|Kotajkh]] || 47&#160;200 \n! 16\n| [[Ararat]] || [[Ararati maakond|Ararat]] || 21&#160;000 \n|-\n! 7\n| [[Kapan]] || [[Sjunikhi maakond|Sjunikh]] || 45&#160;500 \n! 17\n| [[Idževan]] || [[Tavuši maakond|Tavuš]] || 20&#160;700 \n|-\n! 8\n| [[Armavir]] || [[Armaviri maakond|Armavir]] || 34&#160;000 \n! 18\n| [[Arthik]] || [[Širaki maakond|Širak]] || 17&#160;400 \n|-\n! 9\n| [[Gavar]] || [[Gegharkhunikhi maakond|Gegharkhunikh]] || 25&#160;700 \n! 19\n| [[Sisian]] || [[Sjunikhi maakond|Sjunikh]] || 16&#160;800 \n|-\n! 10\n| [[Artašat]] || [[Ararati maakond|Ararat]] || 25&#160;600 \n! 20\n| [[Alaverdi]] || [[Lori maakond|Lori]] || 16&#160;400 \n|-\n|}"]

Images
------
Images are also under the corresponding section. From the image text links (both internal, external) are extracted::

                    "images": [
                {
                    "internal_links": [
                        {
                            "end": 9,
                            "label": "Dareios I",
                            "start": 0,
                            "title": "Dareios I",
                            "url": "http://et.wikipedia.org/wiki/Dareios_I"
                        },
                        {
                            "end": 28,
                            "label": "Behistuni raidkiri",
                            "start": 10,
                            "title": "Behistuni raidkiri",
                            "url": "http://et.wikipedia.org/wiki/Behistuni_raidkiri"
                        },
                        {
                            "end": 72,
                            "label": "6. sajand eKr",
                            "start": 59,
                            "title": "6. sajand eKr",
                            "url": "http://et.wikipedia.org/wiki/6._sajand_eKr"
                        }
                    ],
                    "text": "Dareios I Behistuni raidkiri, millel mainitakse Armeeniat. 6. sajand eKr.",
                    "url": "http://et.wikipedia.org/wiki/Pilt:Darius_I_the_Great's_inscription.jpg"
                }
            ],


.. _wiki_convert:

Converting articles to Estnltk JSON
===================================

The JSON files produced by ``estnltk.wiki.parser`` contains more structural data that can be
represented by Estnltk-s :py:class:`~estnltk.text.Text` class, thus you cannot directly use this JSON
to initiate :py:class:`~estnltk.text.Text` instances.

In Section :ref:`extracting_xml_articles`, we created two folders::

    wikidump/voru
    wikidump/eesti

containing article JSON files extracted from Estonian and Võru dialect wikipedia.
Let's create another subfolders::

    corpora/voru
    corpora/eesti

where we will store the converted JSON files.
The script ``estnltk.wiki.convert`` can be used for the job::

    python3 -m estnltk.wiki.convert wikidump/voru/ corpora/voru/
    python3 -m estnltk.wiki.convert wikidump/eesti corpora/eesti/


As a result, the folders contain large number of files in JSON format that can be used with Estnltk
:py:class:`~estnltk.text.Text` class.
Note that there is only plain text with unique data from the article dumps.
No tokenization, named entity extraction nor anything else has been done.

Structure
---------
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
::

    {start}Title
    SectionText{end}

    {start}Title2
    Section2Text{end}


       "text": "Aserbaid\u017eaani keel\nAserbaid\u017eaani keel kuulub turgi keelte hulka. Peale Aserbaid\u017eaani k\u00f5neldakse seda Gruusias, Armeenias, Iraanis, Iraagis ja T\u00fcrgis.\nAserbaid\u017eaani keel kuulub oguusi keelte hulka,


.. _links_to_processed_wiki_dumps:

Downloading the processed dumps
===============================

Just in case you do not want to extract the articles yourself, here are the links to processed files
from dumps downloaded on Sep 7 2015.

Estonian Wikipedia articles: http://ats.cs.ut.ee/keeletehnoloogia/estnltk/wiki_articles/eesti.zip

Võru dialect Wikipedia articles: http://ats.cs.ut.ee/keeletehnoloogia/estnltk/wiki_articles/voru.zip

