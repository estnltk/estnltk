# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres'

import re

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


def addExternalLinks(sectionObj):
    text = sectionObj['text']
    elinks = [x for x in ExtLinkBracketedRegex.finditer(text)]

    if elinks:
        s = ''
        cur = 0
        extLinks = []
        for m in ExtLinkBracketedRegex.finditer(text):
            s += text[cur:m.start()]
            cur = m.end()

            url = m.group(1)
            label = m.group(3)

            s += label

            obj = {}
            obj['start'] = len(s)-len(label)
            obj['end']= len(s)
            obj['url']= url
            obj['label']= label
            sectionObj['text'] = s + text[cur:]
            extLinks.append(obj)
        sectionObj['external_links'] = extLinks
    return sectionObj

if __name__ == '__main__':
    pass