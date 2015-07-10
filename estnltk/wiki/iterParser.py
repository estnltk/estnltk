# -*- coding: utf-8 -*-
#from estnltk.wiki.iterParser import totalTime

__author__ = 'Andres'

#incremental XML parsing
import re
from xml.etree.ElementTree import iterparse
import argparse
from bz2 import BZ2File
from infoBox import infoBoxParser
from sections import sectionsParser
from references import referencesFinder,refsParser
from categoryParser import categoryParser
import time
from jsonWriter import jsonWriter
from cleaner import clean
from internalLink import findBalanced
from cleaner import dropSpans



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


def parse_and_remove(filename, path):
    path_parts = path.split('/')
    doc = iterparse(filename, ('start', 'end'))
    # Skip the root element
    #next(doc)

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




linkBegin = "http://et.wikipedia.org/wiki/"
#G:\WikiDumper\etwiki-latest-pages-articles.xml

ib = re.compile(r'(?!\<ref>)\{\{[^\}]+?\n ?\|.+?=')

count = 0

def templatesCollector(text, open, close):
    others = []
    spans = [i for i in findBalanced(text, open, close)]

    for start, end in spans:
        o = text[start:end]
        others.append(o)

    text = dropSpans(spans, text)

    return text, others

def main():



    parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')


    parser.add_argument('directory', metavar='D', type=str,
                       help='output directory for the json files')

    parser.add_argument('inputfile', metavar='I', type=str,
                       help='wikipedia dump file relative or full path')

    #group = parser.add_mutually_exclusive_group()
    #group.add_argument("-v", "--verbose", action="store_true")
    #group.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()
    ouputDir = args.directory

    if not ouputDir[-1] == r'/':
        ouputDir += r'/'

    inputFile = args.inputfile

    if inputFile[-3:] == 'bz2':
        print('BZ2', inputFile)
        with BZ2File(inputFile) as xml_file:
            data = parse_and_remove(xml_file, "wikimedia/wikimedia")
            wikiparser(data, ouputDir)
    elif  inputFile[-3:] == 'xml':
        print('XML', inputFile)
        data = parse_and_remove(inputFile, "wikimedia/wikimedia")
        wikiparser(data, ouputDir)
    else:
        print("WRONG FILE FORMAT! \nTry etwiki-latest-pages-articles.xml.bz2 from https://dumps.wikimedia.org/etwiki/latest/")

    path = "G:\WikiDumper\etwiki-latest-pages-articles.xml.bz2"


def wikiparser(data, outputdir):
    totalwriter = 0
    totalComp = 0
    totalTime = 0
    pageObj = {}
    for tag, text in data:
        tag, text = str(tag), str(text)


        if 'title' in tag:
            pageObj['title'] = text
            pageObj['url'] = linkBegin+text.replace(' ', '_')
            print('-----------')
            print(pageObj['title'])
            #print(pageObj['url'])
        if 'timestamp' in tag:
            pageObj['timestamp'] = text
            #print(pageObj['timestamp'])

     #   def refsParser(refsDict):
     #       for k, v in refsDict.items():
     #           pass



        if 'text' in tag:
            #if '#REDIRECT' or '#suuna' in text:
            #print('REDIRECT')
            #    continue
            compStart = time.time()
            #TOdO: remove junk from text
            m = re.search(ib, text)

            if m:
                mg  = m.group()
                text, pageObj['infobox'] = infoBoxParser(text)
                #print(pageObj['infobox'])
            #try:
            ##pprint(referencesFinder(text))
            #Finds and marks nicely all the references in the article, returns a tag:reference dictionary
            text, refsDict = referencesFinder(text)
            refsDict = refsParser(refsDict)
            #SectionParser is where all the work with links, images etc gets done
            text, catList = categoryParser(text)
            text = clean(text)
            pageObj['categories'] = catList
            #TODO:CLEAN

            text, pageObj['other'] = templatesCollector(text, '{', '}')

            sectionobj = (sectionsParser(text, pageObj['title'], refsDict))
            pageObj['sections'] = sectionobj


            #Precious time

            thisComp = time.time() - compStart
            totalComp += thisComp
            #print('Progtime : ',thisComp , totalComp)
            timestart = time.time()
            jsonWriter(pageObj, outputdir)
            thisWrite = time.time()-timestart
            totalwriter += thisWrite
            #print('Writetime: ' , thisWrite ,totalwriter)


            pageObj = {}
            totalTime +=thisComp + thisWrite
            print('Totaltime: ' , totalTime)
    #TODO.  pudi-padi, special pages


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