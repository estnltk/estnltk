# -*- coding: utf-8 -*-
__author__ = 'Andres'
import re
from itertools import chain
from pprint import pprint
from externalLink import addExternalLinks
from internalLink import findBalanced
referencesRegEx = re.compile(r'&lt;ref(.+?)(/&gt|/ref&gt);', re.DOTALL|re.IGNORECASE)
referencesEndRegEx = re.compile(r'&lt;/ref&gt;', re.IGNORECASE)

def referencesParser(sectionObject):
    """
    :param sectionObject: takes a section, searches for references, cleans the text,
    marks the references indexes from zero
    :return: section obj with key-value pair references: [0,1,2] (list of reference indeces)
    """
    obj = sectionObject

    return obj
if __name__ == '__main__':
    with open("armeenia.txt", encoding='utf-8') as f:
        data = f.read()


    references = referencesRegEx.finditer(data)
    refend = referencesEndRegEx.finditer(data)
    count = 0
    ends = []
    for i in references:
       # print(i.end())
       print(i.group())
       print('--------------------------')
       count += 1

    print(count)
