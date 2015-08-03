# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'

from .core import as_unicode
import re
from xml.etree.ElementTree import iterparse
import argparse
from bz2 import BZ2File
import time
from copy import copy
from .infoBox import infoBoxParser
from .sections import sectionsParser
from .references import referencesFinder,refsParser
from .categoryParser import categoryParser
from .jsonWriter import jsonWriter
from .cleaner import clean
from .internalLink import findBalanced
from .cleaner import dropSpans

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
    """leaves related articles and wikitables in place"""
    others = []
    spans = [i for i in findBalanced(text, open, close)]
    spanscopy = copy(spans)
    for i in range(len(spans)):
        start, end = spans[i]

        o = text[start:end]
        ol = o.lower()
        if 'vaata|' in ol or 'wikitable' in ol:
            spanscopy.remove(spans[i])
            continue
        others.append(o)
    text = dropSpans(spanscopy, text)

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

        if 'title' in tag:

        #Drop wikipedia internal pages.



            pageObj['title'] = text

            pageObj['url'] = linkBegin+text.replace(' ', '_')

            if verbose:
                print('-----------')
                print(pageObj['title'], end=' ')

        if 'timestamp' in tag:
            pageObj['timestamp'] = text

    #Drop redirects

        if 'text' in tag:

            for page in dropPages:
                if page in pageObj['title']:
                    if verbose:
                        dropcount += 1
                        print('Dropped Page count', dropcount, text.strip())
                    continue

            try:
                if '#REDIRECT' in text or '#suuna' in text:
                    if verbose:
                        dropcount += 1
                        print('Dropped Page count:', dropcount, text.strip())
                    continue
            except TypeError:
                print(pageObj)
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
            if '{' in text:
                text, pageObj['other'] = templatesCollector(text, '{', '}')

            text, catList = categoryParser(text)
            text = clean(text)
            pageObj['categories'] = catList

#SectionParser is where all the work with links, images etc gets done
            sectionobj = (sectionsParser(text))
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
        with BZ2File(inputFile) as xml_file:
            data = parse_and_remove(xml_file, "wikimedia/wikimedia")
            etWikiParser(data, outputDir, verbose)
    elif inputFile[-3:] == 'xml':
        print('XML', inputFile)
        data = parse_and_remove(inputFile, "wikimedia/wikimedia")
        etWikiParser(data, outputDir, verbose)
    else:
        print("WRONG FILE FORMAT! \nTry etwiki-latest-pages-articles.xml.bz2 from https://dumps.wikimedia.org/etwiki/latest/")


if __name__ == '__main__':
    main()
