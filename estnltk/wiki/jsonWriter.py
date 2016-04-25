# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import sys
__author__ = 'Andres'

import json
import re
import os

import codecs


fileCleanerRegEx = re.compile(r'[:\)[\(\?\*\\/\"]+')
count = 0
printcount = 0
def jsonWriter(jsonObj, dir, verbose):
    global count
    global printcount
    if not os.path.exists(dir):
        os.makedirs(dir)

    with codecs.open(dir+re.sub(fileCleanerRegEx,'',jsonObj['title']+".json"), 'w', encoding='utf-8') as outfile:
        json.dump(jsonObj, outfile, sort_keys = True, indent = 4)

    count += 1
    printcount +=1

    if verbose:
        print('Count:', count)
    elif printcount == 50:
        print(count)
        printcount = 0

