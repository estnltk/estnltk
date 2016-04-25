# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres'

import re
from .wikiextra import balancedSlicer
#From wikiextractor
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


int_link_regex = re.compile('\[\[([^|]*?)\|?([^|]*?)\]\]')

def addExternalLinks(sectionObj):
    text = sectionObj['text']
    elinks_start = [x.start() for x in ExtLinkBracketedRegex.finditer(text)]

    if elinks_start:

        s = ''
        cur = 0
        extL = []
        extLinks = []
        spans = []
        for start in elinks_start:
            link, end = balancedSlicer(text[start:])
            spans.append((start,start+end))
            extL.append(link)

        for link, (start,end) in zip(extL, spans):
            pieces = link.split()

            s += text[cur:start]
            cur = end

            url = pieces[0][1:]
            label = ' '.join(i for i in pieces[1:])[:-1]
            s += label

            obj = {}

            obj['url']= url

            if '[[' in label and ']]' in label:
                intlinks = list(int_link_regex.finditer(label))
                for link in intlinks:
                    label = label.replace(link.group(), link.group(2))



            obj['label']= label
            sectionObj['text'] = s + text[cur:]
            extLinks.append(obj)
        sectionObj['external_links'] = extLinks
    return sectionObj

if __name__ == '__main__':
    pass