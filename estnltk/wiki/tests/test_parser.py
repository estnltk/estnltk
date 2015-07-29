__author__ = 'Andres'

import os
import json
import sys

def jsonReader_TextImportTest(dir):
    indir = dir
    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            log = open(os.path.join(root, f), 'r')
            #print(f)
            jObj = json.load(log)
            #print(jObj['sections'][0]['text'])
            print(jObj['title'])
            print('---------------')

            printer(jObj['sections'])
            """sections = (jObj['sections'])
            for i in range(len(sections)):

                    tObj = Text(jObj['sections'][i]['text'])"""

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
                    #print(KeyError)
                    pass
            #print(tObj.named_entities)


def printer(flist):

    for i in flist:
        try:
            print(i['title'])
        except KeyError:
            print('intro')
        if "sections" in i.keys():
            printer(i['sections'])

def myprint(list):
  for i in list:
    if 'sections' in i.keys():
      myprint(i['sections'])
    if i['text']:
      print(i['text'])
