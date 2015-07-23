# -*- coding: utf-8 -*-

__author__ = 'Andres'

import json
import re
import os
from estnltk import Text

fileCleanerRegEx = re.compile(r'[:\\/]+')
def jsonWriter(jsonObj, dir=''):
    with open("./Json/"+re.sub(fileCleanerRegEx,'',jsonObj['title']+".json"), 'w', encoding='utf-8') as outfile:
        json.dump(jsonObj, outfile, sort_keys = True, indent = 4)

def jsonReader(dir):
    indir = dir
    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            log = open(os.path.join(root, f), 'r')
            print(f)
            jObj = json.load(log)
            #print(jObj['sections'][0]['text'])
            tObj = Text(jObj['sections'][0]['text'])
            print(tObj.named_entities)
if __name__ == '__main__':
    jsonReader(r'C:\Users\Andres\PycharmProjects\wikiXMLParser\Json')