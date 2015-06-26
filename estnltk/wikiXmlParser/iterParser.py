# -*- coding: utf-8 -*-

__author__ = 'Andres'

#incremental XML parsing
import re
from infoBox import infoBoxParser
from pprint import pprint
from xml.etree.ElementTree import iterparse
from sections import sectionsParser

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



data = parse_and_remove('G:\WikiDumper\etwiki-latest-pages-articles.xml', "wikimedia/wikimedia" )
linkBegin = "http://et.wikipedia.org/wiki/"
#G:\WikiDumper\etwiki-latest-pages-articles.xml

ib = re.compile(r'\{\{[A-Za-zÄÖÕÜäöõü ]+\n')
pageObj = {}
count = 0
for tag, text in data:
    tag, text = str(tag), str(text)
    if '#REDIRECT' in text:
        print('REDIRECT')
        continue
    if 'title' in tag:
        pageObj['title'] = text
        pageObj['url'] = linkBegin+text.replace(' ', '_')
        print('-----------')
        print(pageObj['title'])
        print(pageObj['url'])
    if 'timestamp' in tag:
        pageObj['timestamp'] = text
        print(pageObj['timestamp'])

    if 'text' in tag:
        try:
            #SectionParser is where all the work with links, images etc gets done
            sectionobj = (sectionsParser(text, pageObj['title']))
            pageObj['sections'] = sectionobj
            print(pageObj['sections'])
        except AttributeError:
            count += 1
            print(text)
        if re.search(ib, text):
            pageObj['infobox'] = infoBoxParser(text)
            print(pageObj['infobox'])







