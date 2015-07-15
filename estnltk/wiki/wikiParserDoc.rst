============
Estonian wikipedia dump json parser
============

Usage
-------------------

The easiest way to use the program is from the command line::

    python etWikiParser.py G:\Json G:\WikiDumper\etwiki-latest-pages-articles.xml.bz2
	
Output directory for .json files as #1 argument. The wikipedia articles dump file as #2 argument.

Optional flag -v or --verbose for printing Article Title and article count everytime.

Without the -v or --verbose option after every 50th article the count is printed without the titles.

If you want to invoke the program from code (which might be a bad idea, because it takes pretty long time
to process the whole dump) you can try for example::

    import estnltk.wiki.etWikiParser
    data = 'G:\WikiDumper\etwiki-latest-pages-articles.xml.bz2'
    outputdir = G:\Json
    etWikiParser(data, outputdir, verbose=True)

Json structure
-------------------

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
        "other": [],
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

A section is a nested structure, if a section has subsections, they can be accessed like this::
    
    obj['sections'][0]['sections']
   
Other elements include objects like wikipedia templates in the form of::
    
    {{templatename|parameter1|etc}}
    
    "other": [
        "{{See artikkel| räägib üldmõistest; Herodotose teose kohta vaata artiklit [[Historia]]}}",
        "{{ToimetaAeg|kuu=oktoober|aasta=2012}}",
        "{{keeletoimeta}}"
    ]
    
The first section is always introduction and doesn´t have a title.
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

