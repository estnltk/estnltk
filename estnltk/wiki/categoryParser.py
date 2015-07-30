# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres andresmt [at] ut [dot] ee'

import re

categoryRegEx = re.compile(r'\[\[Kategooria:(.+?)\]\]', re.I)

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