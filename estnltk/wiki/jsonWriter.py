# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
__author__ = 'Andres'

import json
import re
import os
#from estnltk import Text

fileCleanerRegEx = re.compile(r'[:\)[\(\?\*\\/]+')

def jsonWriter(jsonObj, dir):

    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(dir+re.sub(fileCleanerRegEx,'',jsonObj['title']+".json"), 'w', encoding='utf-8') as outfile:
        json.dump(jsonObj, outfile, sort_keys = True, indent = 4)




def jsonReader_internalLinksTest(dir):
    indir = dir
    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            log = open(os.path.join(root, f), 'r')
            #print(f)
            jObj = json.load(log)
            #print(jObj['sections'][0]['text'])
            sections = (jObj['sections'])
            for i in range(len(sections)):
                try:
                    lObj = (jObj['sections'][i]['internal_links'])
                    tObj = (jObj['sections'][i]['text'])
                    for link in lObj:
                        end = int(link['end'])
                        start = int(link['start'])
                        tlabel = tObj[start:end]
                        llabel = link['label']
                        #print(tlabel, llabel)
                        try:
                            assert tlabel == llabel
                        except AssertionError:
                            print(tlabel, llabel, file=sys.stderr)
                except KeyError:
                    #print(f, sections[i])
                    print(KeyError)
            #print(tObj.named_entities)

if __name__ == '__main__':
    jsonReader_internalLinksTest(r'G:\Json')