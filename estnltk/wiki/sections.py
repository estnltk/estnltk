# -*- coding: utf-8 -*-
__author__ = 'Andres'
import re
from pprint import pprint
from externalLink  import addExternalLinks
from internalLink import addIntLinks
from references import reffinder
import images
from categoryParser import categoryParser
from internalLink import relatedArticles
def sectionsParser(text, title, refsdict):
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
    textStartRE = re.compile(r"""\'\'\'""")
    #TODO:needs fixing. logic should be different.
    #TODO: this method should reveive text w shit cut out.


        #textStart = textStartRE.search(text).start()


    textStart = 0
    entries = re.split("\n=", text[textStart:])
    stack = [[]]
    intro = {}
    sectionTitleRegEx = re.compile(r'={1,}.+={2,}')
    section = {}
    section['text'] = entries[0]
    counts = []
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

    #add images, links, references,


    for section in sections:
        section = relatedArticles(section)
        section = reffinder(section, refsdict)
        section = images.imageParser(section)
        section = addExternalLinks(section)
        section = addIntLinks(section)



    #datastructure nesting thanks to Timo!
    if counts:
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

            pos += 1

        while len(stack) > 1:
            group = stack.pop()
            stack[-1][-1]['sections'] = group

    stack = stack[0]


    return stack
"""
if __name__ == '__main__':
    with open("armeenia.txt", encoding='utf-8') as f:
        text = f.read()

    
    entries = re.split("\n=", text)
    #pprint(entries)
    print(len(entries))
    titles = []
    textDict = {}
    sectionTitleRegEx = re.compile(r'={1,}.+={2,}')
    intro = entries[0]
    print('intro ', intro)
    textDict['intro']=intro
    counts = []
    sections = []
    objects = []
    #pprint(entries[1:])
    for i in entries[1:]:
        section = {}

        title = re.match(sectionTitleRegEx, i)
        if title:
            titleEnd = title.end()
            print(title)
            title = title.group()
            text = i[titleEnd:]
            count =  title.count('=')
            section['title']=title.strip('= ')
            section['text']=text
			#Hetkel obj tuple (taseme nr, dict)
            obj = count, section
            print(obj)
            objects.append(obj)
            sections.append(section)
            #print(title, count)
            counts.append(count)
    print(counts)
    print(len(counts))
    print(counts[47])

"""
if __name__ == '__main__':
    with open("bathumi.txt", encoding='utf-8') as f:
        text = f.read()

    print(sectionsParser(text, ''))

    #datastructure nesting thanks to Timo!
"""
    n = len(sections)
    pos = 0
    stack = [[]]
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
            #print(stack[-1][-1])
            stack[-1][-1]['sections'] = group
            levels.pop()
            continue
        pos += 1

    while len(stack) > 1:
        group = stack.pop()
        stack[-1].append(group)

    stack = stack[0]
    print(stack)
    #print (elems)
    #test
    for i in stack:
        pprint(i['title'])
        try:
            for j in i['sections']:
                pprint('     '+ j['title'])
        except:
            pass
            """