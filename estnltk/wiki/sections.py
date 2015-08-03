 # -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re
from .externalLink  import addExternalLinks, ExtLinkBracketedRegex
from .internalLink import addIntLinks
from .references import reffinder
from .internalLink import relatedArticles
from .tableCollector import  tableCollector
from .images import imageRegEx, imageParser

def sectionsParser(text):
    """
    :param text: the whole text of an wikipedia article
    :return:  a list of nested section objects
 [{title: "Rahvaarv",
                text: "Eestis elab..."},
               {title: "Ajalugu",
                text: "..."},
                sections: [{title: "Rahvaarv",
                     text: "Eestis elab..."},
                    {title: "Ajalugu",
                    text: "..."}],],
"""

    textStart = 0

    #Split the text in sections. Hackish part, but seems to work fine.
    entries = re.split("\n=", text[textStart:])
    stack = [[]]
    intro = {}
    sectionTitleRegEx = re.compile(r'={1,}.+={2,}')
    section = {}
    section['text'] = entries[0]
    counts = []

    #Presumes the first section is always marked with 2 =
    #First count is always 3. (\n=)= First Section of an Article ==
    #Parens is omitted. Leaves three = marks.

    counts.append(3)
    sections = []
    sections.append(section)
    for i in entries[1:]:
        section = {}
        title = re.match(sectionTitleRegEx, i)
        if title:
            titleEnd = title.end()
            title = title.group()
            text = i[titleEnd:]
            level =  title.count('=')
            section['title']=title.strip('= ')
            section['text']=text

            sections.append(section.copy())
            counts.append(level)

    #add images, links, references, tables

    for section in sections:
        text = section['text']
        if 'wikitable' in text or '</table>' in text.lower():
            section['text'], section['tables'] = tableCollector(text)

        section = relatedArticles(section)

        if '<ref' in text:
            section = reffinder(section)

        if imageRegEx.search(text):
            section = imageParser(section)

        section['text'] = section['text'].strip()

        if ExtLinkBracketedRegex.search(text):
            section = addExternalLinks(section)


        if '[[' in text:
            section = addIntLinks(section)

        #clean uneven brackets and whatnot

        #take extlink start:end w regex.
        el = 'external_links'
        if el in section.keys():

            #section['text'] = section['text'].replace('[', '').replace(']', '')
            text = section['text']

            for link in section[el]:

                label = link['label']
                label = re.compile(re.escape(label))
                m = label.search(text)
                #if there are unbalanced brackets in the external
                #links label inside text then it fails to mark the start and end
                try:
                    link['start'] = m.start()
                    link['end'] = m.end()
                except AttributeError:
                    print('Problem with external links start:end position!')
                    print(label)
                    print(text)





    #datastructure nesting thanks to Timo!
    if counts:
        assert len(counts) == len(sections)

        n = len(sections)
        pos = 0

        levels = [counts[0]]

        while pos < n:
            count = counts[pos]
            elem = sections[pos]
            level = levels[-1]
            if count == level:
                stack[-1].append(elem)
            elif count >= level:
                stack.append([elem])
                levels.append(count)
            else:
                group = stack.pop()
                stack[-1][-1]['sections'] = group
                levels.pop()
                continue

            pos += 1

        while len(stack) > 1:
            group = stack.pop()
            stack[-1][-1]['sections'] = group

    stack = stack[0]


    return stack
