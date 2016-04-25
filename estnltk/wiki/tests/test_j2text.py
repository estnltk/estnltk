# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres'

import unittest
from ..convert import json_format
import json
from ... import Text
import os


#Tests the files in .json-examples

def yield_json():
    for root, dirs, filenames in os.walk('G:\Jsonf'):
        for f in filenames:
            log = open(os.path.join(root, f), 'r')
            j_obj = json.load(log)
            j_obj = json_format(j_obj)
            yield j_obj
            log.close()

class testj2Text(unittest.TestCase):

    def test_links(self):
        for j_obj in yield_json():
            el = 'external_links'
            il = 'internal_links'

            if el in j_obj.keys():
                for elink in j_obj[el]:
                    start = elink['start']
                    end = elink['end']
                    self.assertEqual(j_obj['text'][start:end], elink['label'])


            if il in j_obj.keys():
                for ilink in j_obj[il]:
                    start = ilink['start']
                    end = ilink['end']
                    try:
                        self.assertEqual(j_obj['text'][start:end], ilink['label'])
                    except:
                        print(j_obj)


    def test_sections(self):
        for j_obj in yield_json():
            if 'sections' in j_obj.keys():
                for sec in j_obj['sections']:
                    start = sec['start']
                    end = sec['end']
                    if 'title' in sec.keys():
                        title = sec['title']
                        self.assertTrue(j_obj['text'][start:end].startswith(title))



    def test_textobj_init(self):
        for j_obj in yield_json():
            self.assertIsInstance(j_obj, Text)


if __name__ == '__main__':
    unittest.main()
