# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'

from ..core import as_unicode
import re
from xml.etree.ElementTree import iterparse
import argparse
from bz2 import BZ2File
import time
from .infoBox import infoBoxParser
from .sections import sectionsParser
from .references import referencesFinder,refsParser
from .categoryParser import categoryParser
from .jsonWriter import jsonWriter
from .cleaner import clean
from .internalLink import findBalanced
from .cleaner import dropSpans
from .tableCollector import tableCollector
# Matches bold/italic
bold_italic = re.compile(r"'''''(.*?)'''''")
bold = re.compile(r"'''(.*?)'''")
italic_quote = re.compile(r"''\"([^\"]*?)\"''")
italic = re.compile(r"''(.*?)''")
quote_quote = re.compile(r'""([^"]*?)""')

# Matches space
spaces = re.compile(r' {2,}')

# Matches dots
dots = re.compile(r'\.{4,}')

linkBegin = "http://et.wikipedia.org/wiki/"
#infobox
ib = re.compile(r'(?!\<ref>)\{\{[^\}]+?\n ?\|.+?=')
dropPages = ['Mall:', 'Portaal:', 'Kategooria:', 'Vikipeedia:',
             'MediaWiki:', 'Moodul:', 'Juhend:']

count = 0
dropcount = 0
def parse_and_remove(filename, path):
    path_parts = path.split('/')
    doc = iterparse(filename, ('start', 'end'))
    tag_stack = []
    elem_stack = []
    for event, elem in doc:
        if event == 'start' in elem.tag:
            tag_stack.append(elem.tag)
            elem_stack.append(elem)
        elif event == 'end':
            eletag = elem.tag
            elemtext = elem.text
            yield eletag, elemtext

            if tag_stack == path_parts:
                yield elem
                elem_stack[-2].remove(elem)
            try:
                tag_stack.pop()
                elem_stack.pop()
            except IndexError:
                pass



def templatesCollector(text, open, close):
    others = []
    spans = [i for i in findBalanced(text, open, close)]
    for start, end in spans:
        o = text[start:end]
        others.append(o)
    text = dropSpans(spans, text)

    return text, others



def etWikiParser(data, outputdir, verbose = False):
    global dropcount

    if not outputdir[-1] == r'/':
        outputdir += r'/'

    totalwriter = 0
    totalComp = 0
    totalTime = 0
    pageObj = {}
    for tag, text in data:
        if tag and text:
            tag, text = as_unicode(tag), as_unicode(text)
            #print(tag, text)
    #FIXME: py2 unicode issue
        if 'title' in tag:

        #Drop wikipedia internal pages.

            for page in dropPages:
                if page in text:
                    if verbose:
                        dropcount += 1
                        print('Dropped Page count', dropcount, text.strip())
                    continue

            pageObj['title'] = text
            pageObj['url'] = linkBegin+text.replace(' ', '_')

            if verbose:
                print('-----------')
                print(pageObj['title'], end=' ')

        if 'timestamp' in tag:
            pageObj['timestamp'] = text

    #Drop redirects

        if 'text' in tag:
            if '#REDIRECT' in text or '#suuna' in text:
                if verbose:
                    dropcount += 1
                    print('Dropped Page count:', dropcount, text.strip())
                continue

            compStart = time.time()

    #Finds and marks nicely all the references in the article, returns a tag:reference dictionary
            text, refsDict = referencesFinder(text)

    #Infoboxes
            m = re.search(ib, text)
            if m:
                text, pageObj['infobox'] = infoBoxParser(text)

#Finds links in references TODO: find unbracketed external links

            if refsDict:
                refsDict = refsParser(refsDict)
                pageObj['references'] = refsDict
#Categories, cleaning, and other element.

            text, catList = categoryParser(text)
            text = clean(text)
            pageObj['categories'] = catList

            if '{' in text:
                text, pageObj['other'] = templatesCollector(text, '{', '}')


#SectionParser is where all the work with links, images etc gets done
            sectionobj = (sectionsParser(text, refsDict))
            pageObj['sections'] = sectionobj


            #Precious time

            thisComp = time.time() - compStart
            totalComp += thisComp
            #print('Progtime : ',thisComp , totalComp)
            timestart = time.time()
            jsonWriter(pageObj, outputdir, verbose)
            thisWrite = time.time()-timestart
            totalwriter += thisWrite
            #print('Writetime: ' , thisWrite ,totalwriter)


            pageObj = {}
            totalTime +=thisComp + thisWrite
            #print('Totaltime: ' , totalTime)


def main():

    parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')


    parser.add_argument('directory', metavar='D', type=str,
                       help='full path to output directory for the json files')

    parser.add_argument('inputfile', metavar='I', type=str,
                       help='wikipedia dump file full path')

    parser.add_argument("-v", "--verbose", action="store_true",
                        help='Print written article titles and count.')


    args = parser.parse_args()
    outputDir = args.directory
    inputFile = args.inputfile
    verbose = args.verbose

    if inputFile[-3:] == 'bz2':
        print('BZ2', inputFile)
        with BZ2File(inputFile, 'utf-8') as xml_file:
            data = parse_and_remove(xml_file, "wikimedia/wikimedia")
            etWikiParser(data, outputDir, verbose)
    elif inputFile[-3:] == 'xml':
        print('XML', inputFile)
        data = parse_and_remove(inputFile, "wikimedia/wikimedia")
        etWikiParser(data, outputDir, verbose)
    else:
        print("WRONG FILE FORMAT! \nTry etwiki-latest-pages-articles.xml.bz2 from https://dumps.wikimedia.org/etwiki/latest/")

"""
Go through dictionary
def myprint(d):
  for k, v in d.iteritems():
    if isinstance(v, dict):
      myprint(v)
    else:
      print "{0} : {1}".format(k, v)
"""

if __name__ == '__main__':
    main()
    t = """&lt;center&gt;&lt;div style=&quot;text-align: center; margin: 0 10% 1em 10%;&quot;&gt;
{| align=center class=&quot;disputeabout&quot; style=&quot;background: beige; border: 1px solid #aaa; padding: .2em; margin-bottom: 3px; font-size: 95%; width: auto;&quot;
| valign=&quot;top&quot; style=&quot;padding: .2em&quot; | [[Pilt:Stop_hand.png|45px|Vaidlustatud]]
| style=&quot;padding: 0.1em&quot; width = 320| '''Artikli selle osa faktiline õigsus on vaieldav.'''&lt;br&gt;
''Vaieldav on allikate selline liigitus.''
|-
|colspan=2 align=center|&lt;div style=&quot;font-size: 90%;&quot;&gt;Vaata lähemalt selle artikli [[:{{NAMESPACE}} talk:{{PAGENAME}}|aruteluleheküljelt]].&lt;/div&gt;
|}
&lt;/div&gt;&lt;/center&gt;
*[[Esemelised ajalooallikad]] ehk [[muistis]]ed: [[kinnismuistis]]ed ja [[irdmuistis]]ed
*[[Kirjalikud ajalooallikad]]: [[ürik]]ud, [[kroonika]]d, [[seadus]]ed, [[memuaarid]], [[statistilised materjalid]] jne
*[[Suulised ajalooallikad]]: [[pärimus]]ed, [[rahvaluule]] ([[legend]]id, [[müüt|müüdid]], [[muinasjutt|muinasjutud]])
*[[Etnoloogilised ajalooallikad]]: [[tava]]d, [[komme|kombed]] ja [[traditsioon]]id
*[[Lingvistilised ajalooallikad]]: [[Keel (keeleteadus)|keel]] ja [[murre|murded]]
*[[Audiovisuaalsed ajalooallikad]]: [[foto]]d, [[film]]id ja [[helisalvestis]]ed"""

    text, other = templatesCollector(t, '{', '}')
    #print(text, ' OTHER ',  other)