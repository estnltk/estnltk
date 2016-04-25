# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re
from .wikiextra import balancedSlicer as bSB

wikitableStartRegEx = re.compile(r'\{.+?wikitable')
tableRegEx = re.compile(r'<table>?.+?</table>', re.IGNORECASE|re.DOTALL)

def tableCollector(text):
    t = ''
    tables = []

    if "wikitable" in text:
        table = [x.start() for x in wikitableStartRegEx.finditer(text)]
        for start in table:
            tableContent, end = bSB(text[start:], openDelim='{', closeDelim='}')
            t += text[:start]+text[end+start:]
            tables.append(tableContent)

    if '</table>' in text.lower():
        tab = [x.group() for x in tableRegEx.finditer(text)]
        t = tableRegEx.sub('', text)
        tables.extend(tab)

    return t, tables
