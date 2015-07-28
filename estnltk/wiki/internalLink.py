# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import


__author__ = 'Andres'
import re
from .images import imageRegEx
from .images import imageParser
from .externalLink import addExternalLinks
from pprint import pprint

urlBegin = "http://et.wikipedia.org/wiki/"
wgUrlProtocols = [
     'bitcoin:', 'ftp://', 'ftps://', 'geo:', 'git://', 'gopher://', 'http://',
     'https://', 'irc://', 'ircs://', 'magnet:', 'mailto:', 'mms://', 'news:',
     'nntp://', 'redis://', 'sftp://', 'sip:', 'sips:', 'sms:', 'ssh://',
     'svn://', 'tel:', 'telnet://', 'urn:', 'worldwind://', 'xmpp:', '//'
]
EXT_LINK_URL_CLASS = r'[^][<>"\x00-\x20\x7F\s]'
ExtLinkBracketedRegex = re.compile('\[(((?i)' + '|'.join(wgUrlProtocols) + ')' +
                                   EXT_LINK_URL_CLASS + r'+)\s*([^\]\x00-\x08\x0a-\x1F]*?)\]', re.S | re.U)

relatedRegEx = re.compile(r'\{\{vaata(.+?)\}\}', re.IGNORECASE)
intLinkRegex = re.compile(r'\[\[.*?\|?.+?\]\]\w*')

def relatedArticles(sectionObject):
    text = sectionObject['text']
    related = [x.group(1).strip('|') for x in relatedRegEx.finditer(text)]
    if related:
        sectionObject['related_articles'] = related
        text = re.sub(relatedRegEx, '', text)
        sectionObject['text'] = text
    return sectionObject

def bracketsParser(sectionObject):
    """
    call it after the images have been parsed
    :param sectionObject:
    :return: a list of link objects
    links = [
        { ... etünonüüm ... },
        {
              start: 32.
              end: 41
              text: "Pytheasel" # lilngi tekst ( text[start:end] )
              title: "Pytheas" # lingi pealkiri
              url: "http://et.wikipedia.org/wiki/Pytheas" # lingi wikipedia URL
        }, ....
    ]
     #linkRegEx = re.compile(r'\[\[\(A-Za-z0-9äöüõÄÖÕÜ\| \]\]')

    """
    text = sectionObject['text']
    spans = findBalanced(text, '[[', ']]')
    obj = {}
    links = []
    images = []
    for start, end in spans:
        balanced = text[start:end]
        print(balanced)



        if re.match(imageRegEx, balanced):
            obj = imageParser(balanced)
            images.append(obj)

        else:
            obj = linkParser(balanced, start, end)
            links.append(obj)


    if images:
        sectionObject['images'] = images
    if links:
        sectionObject['links'] = links



    return sectionObject

#function from wikiextractor.py

def linkParser(textInBrackets, start, end):
    """

    :param textInBrackets:
    :return:
    """

    if '|' in textInBrackets:
        textInBrackets = textInBrackets.split('|')
        #print(len(textInBrackets))
        text = textInBrackets[1]
        title = textInBrackets[0]
        url = urlBegin + textInBrackets[0]

    else:

        text = textInBrackets
        title = textInBrackets
        url = urlBegin+textInBrackets

    start = start + 2
    end = end - 2
    return {'start':start, 'end':end, 'text':text, 'title':title,'url':url}

    #if len(textInBrackets)>


def findBalanced(text, openDelim, closeDelim):
    """
    Assuming that text contains a properly balanced expression
    :param openDelim: as opening delimiters and
    :param closeDelim: as closing delimiters.
    :return: an iterator producing pairs (start, end) of start and end
    positions in text containing a balanced expression.
    """
    openPat = '|'.join([re.escape(x) for x in openDelim])
    # pattern for delimiters expected after each opening delimiter
    afterPat = {o: re.compile(openPat+'|'+c, re.DOTALL) for o,c in zip(openDelim, closeDelim)}
    stack = []
    start = 0
    cur = 0
    end = len(text)
    startSet = False
    startPat = re.compile(openPat)
    nextPat = startPat
    while True:
        next = nextPat.search(text, cur)
        if not next:
            return
        if not startSet:
            start = next.start()
            startSet = True
        delim = next.group(0)
        if delim in openDelim:
            stack.append(delim)
            nextPat = afterPat[delim]
        else:
            opening = stack.pop()
            # assert opening == openDelim[closeDelim.index(next.group(0))]
            if stack:
                nextPat = afterPat[stack[-1]]
            else:
                yield start, next.end()
                nextPat = startPat
                start = next.end()
                startSet = False
        cur = next.end()

def addIntLinks(sectionObj):

    t = sectionObj['text']
    spans = [(m.start(), m.end()) for m in intLinkRegex.finditer(t)]

    if spans:
        text = ''
        links = []
        link = {}

        lastEnd = 0
        for index in range(len(spans)):
            start = spans[index][0]
            end = spans[index][1]
            try:
                nextStart = spans[index+1][0]
            except IndexError:
                nextStart = None

            linktext = t[start:end].replace('[', '').strip('{}:;-., ')
            if '|' in linktext:
                linktext = linktext.split('|')
                label = linktext[1].replace(']', '')
                title = linktext[0]
                url = urlBegin + title

            else:

                label = linktext.replace(']', '')

                title = linktext[:linktext.index(']')]

                url = urlBegin+title


            text+=t[lastEnd:start]+label
            lastEnd = end
            link['start'] =len(text)- len(label)
            link['end'] = len(text)
            link['label'] = label
            link['title'] = title
            link['url'] = url.replace(' ', '_')
            links.append(link.copy())
            if nextStart == None:
                text+=t[end:nextStart]


        sectionObj['text'] = text
        sectionObj['internal_links'] = links

    return sectionObj

