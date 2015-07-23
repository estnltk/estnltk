============
Estonian wikipedia dump json parser
============

Usage
-------------------

The easiest way to use the program is from the command line::

    python etWikiParser.py G:\Json G:\WikiDumper\etwiki-latest-pages-articles.xml.bz2
	
Output directory for .json files as #1 argument. The wikipedia articles dump file as #2 argument.

Optional flag -v or --verbose for printing Article Title and article count, dropped page and drop count everytime.

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
                

Sections
-------------------
The first section is always introduction and doesn´t have a title. 

A section is a nested structure, if a section has subsections, they can be accessed like this::
    
    obj['sections'][0]['sections']
   
Other
-------------------

Other elements include objects like wikipedia templates in the form of::
    
    {{templatename|parameter1|etc}}
    
    "other": [
        "{{See artikkel| räägib üldmõistest; Herodotose teose kohta vaata artiklit [[Historia]]}}",
        "{{ToimetaAeg|kuu=oktoober|aasta=2012}}",
        "{{keeletoimeta}}"
    ]
    

 
References
-------------------

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
-------------------

Internal links point to articles in et.wikipedia.org/wiki/.::

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
-------------------
Bold/italics/bulletlists are marked in the dump, but are reformated as plain-text in json. Quotes, newlines are preserved.

Tables
-------------------
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
-------------------
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
