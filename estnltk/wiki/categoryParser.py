# -*- coding: utf-8 -*-
__author__ = 'Andres'
import re

categoryRegEx = re.compile(r'\[\[Kategooria:(.+?)\]\]')
def categoryParser(text):
    kat = []
    #[[K:Antsla|Antsla, Antsla|
    for x in categoryRegEx.finditer(text):
        catName = x.group(1)
        if '|' in catName:
            catName = catName[:catName.index('|')]
        kat.append(catName)

    text = re.sub(categoryRegEx, '', text)

    return text, kat