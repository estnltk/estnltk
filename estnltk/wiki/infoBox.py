# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'

import re
from pprint import pprint
from .wikiextra import balancedSlicer as bSB

linkBegin = "http://et.wikipedia.org/wiki/"
clean = re.compile(r'(\<br\>|\&nbsp\;)')
infobStartRegEx = re.compile(r"(?!\<ref\>\n)\{\{[^\}]+?\n ?\|.+?=" , re.DOTALL)

def infoBoxParser(text):
    t = ''
    infob = [x for x in re.finditer(infobStartRegEx, text)]
    infobs = []
    if infob:
        for i in infob:
            start = i.start()
            infobContent, end = bSB(text[start:], openDelim='{', closeDelim='}')
            #print('Infobox:', text[start:end])
            infobContent = clean.sub('', infobContent)
            t += text[:start]+text[end+start:]
            if infobContent:
                infobContent = infobContent.replace('[', '').replace(']', '').splitlines()  #.replace('|', '').split('\n'))
                infobDict = {}
                for line in infobContent:
                    line = line.strip('|  ').strip(' ')
                    line = line.split('=')
                    if len(line) == 2:
                        if line[0] and line[1]:
                            l = line[1].strip('[').strip(']').strip()
                            if '|' in l:
                                l = l.split('|')[1]
                            infobDict[line[0].strip()]= l
            infobs.append(infobDict)

        return t, infobs



#pprint.pprint(infobDict)
if __name__ == '__main__':
    with open("amhara", encoding='utf-8') as f:
        t = f.read()

    t, b = (infoBoxParser(t))
    pprint(b)
    pprint(t)