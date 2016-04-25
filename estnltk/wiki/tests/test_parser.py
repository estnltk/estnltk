__author__ = 'Andres'

import os
import json
import sys
import unittest

def flatten(l, new=[]):
    """Flatten the nested list of sections"""
    for i in l:
        new.append(i)
        if 'sections' in i.keys():
            flatten(i['sections'], new)
            i.pop('sections', None)
    return new

def jsonReader():
    indir = 'G:\Jsonf'

    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            log = open(os.path.join(root, f), 'r')
            #print(f)
            jObj = json.load(log)
            yield jObj
            log.close()

class testParser(unittest.TestCase):

    def test_internal_links(self):

            for jObj in jsonReader():
                new = []
                sections = (jObj['sections'])
                sections = flatten(sections, new)
                for sec in sections:
                    try:
                        lObj = (sec['internal_links'])
                        tObj = (sec['text'])
                        for link in lObj:
                            end = int(link['end'])
                            start = int(link['start'])
                            tlabel = tObj[start:end]
                            llabel = link['label']

                            self.assertEqual(tlabel, llabel)
                    except KeyError:
                        pass

    def test_external_links(self):

            for jObj in jsonReader():
                new = []
                sections = (jObj['sections'])
                sections = flatten(sections, new)
                for sec in sections:
                    try:
                        lObj = (sec['external_links'])
                        tObj = (sec['text'])
                        for link in lObj:
                            end = int(link['end'])
                            start = int(link['start'])
                            tlabel = tObj[start:end]
                            llabel = link['label']

                            self.assertEqual(tlabel, llabel)
                    except KeyError:
                        pass




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

if __name__ == '__main__':
    unittest.main()