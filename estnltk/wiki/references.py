# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re
from .externalLink import addExternalLinks, ExtLinkBracketedRegex
from .internalLink import findBalanced, addIntLinks

referencesRegEx = re.compile(r'<ref>?(.+?)<?(/>|/ref>)', re.DOTALL|re.IGNORECASE)

referencesEndRegEx = re.compile(r'&lt;/ref&gt;', re.IGNORECASE)

def refsParser(refsDict):
    for key in refsDict:

        #does a ref contain external links
        value = refsDict[key]
        value = {'text':value}
        if ExtLinkBracketedRegex.search(value['text']):
            value = addExternalLinks(value)


        intlinks = [x for x in findBalanced(value['text'], openDelim='[[', closeDelim=']]')]
        #internal links
        if intlinks:
            value = addIntLinks(value)

        #handle unbracketed links
        if value['text'].startswith('http'):
            value['link'] = value['text']

        refsDict[key]=value

    newRefs = []
    for key in sorted(refsDict.keys()):
        newRefs.append(refsDict[key])

    return newRefs

refTagRegEx = re.compile('<ref (\d)+/>')

def reffinder(sectionObj):
    """
    add reference indeces to sectionobj['references']
    :param sectionObj
    :return: a section obj w references: field
    """
    text = sectionObj['text']
    reftags = [x for x in refTagRegEx.finditer(text)]
    if reftags:
        references = []
        for tag in reftags:
            references.append(int(tag.group(1)))

        sectionObj['references'] = references

        text = refTagRegEx.sub('', text)
        sectionObj['text'] = text

    return sectionObj

def referencesFinder(text):
    """
    :param text: takes the whole text of an article, searches for references, cleans the text,
    marks the reference indeces from zero inside the text.
    :return: the tagged text and a tag:reference dictionary to be used in sectionParser
    """
    references = referencesRegEx.finditer(text)
    count = 0
    refs = []
    spans = []
    for i in references:
        refs.append(i.group())
        spans.append(i.span())
        count += 1
    done = set()
    nameRegEx = re.compile(r"""(name=["']*.*?["']*)(\s|/|>)""")

    for index, obj in enumerate(refs):

        if obj.startswith('<ref name='):
                nameTag = re.escape(nameRegEx.search(obj).group(1))

                if nameTag not in done:
                    nameTag = re.escape(nameRegEx.search(obj).group(1))
                    indeces = [i for i, x in enumerate(refs) if re.search(nameTag, x)]
                    matches = [refs[i] for i in indeces]
                    full = max(matches, key=len)

                    for i in indeces:
                        refs[i] = full

                    done.add(nameTag)

    #eliminate <ref tag or other rudiments from the ref string

    for i in range(len(refs)):
        #print('SIIT', refs[i])
        lastindex = refs[i].rindex('<')
        firstindex = refs[i].index('>')+1
        refs[i]=refs[i][firstindex:lastindex]

    #Handle cite-references

    for i in range(len(refs)):
        if 'cite' in refs[i].lower():
            newText = ''
            values = refs[i].split('|')
            for j in values:
                if '=' in j:
                    first = j.index('=')
                    newText += j[first+1:].strip() + ';'
            refs[i] = newText
    #a ref string:position int dictionary
    refspos = {}
    c = 0
    for i in refs:
        if i not in refspos.keys():
            refspos[i] = c
            c +=1
        else:
            continue

    #print(refspos)

    #eliminate old, bad <ref> tags and insert clean  ones <ref 1..2..3/> to the same spot.
    newText = ''
    assert len(spans) == len(refs)
    #Could happen... havent yet.
    next = 0
    for i in range(len(spans)):
        start = spans[i][0]
        newText+=text[next:start]+'<ref '+str(refspos[refs[i]])+'/>'
        next = spans[i][1]

    newText+=text[next:]

    #switch keys:values in the dictionary for use in sectionsParser
    #positiontag:ref
    newDict  = {y:x for x,y in refspos.items()}

    return newText, newDict

if __name__ == '__main__':
    pass