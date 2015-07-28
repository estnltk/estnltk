# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres'

import argparse
from .json2Text import json_format
import json

"""
This Test takes a etWikiParsed .json file as an argument and tests the internal and external link positions
And the positions of sections. And the initiation of estnltk.Text object
"""
def test_links(j_obj):

    el = 'external_links'
    il = 'internal_links'

    if el in j_obj.keys():
        for elink in j_obj[el]:
            start = elink['start']
            end = elink['end']
            assert j_obj['text'][start:end] == elink['label']
            print('External Links: OK!')
    if il in j_obj.keys():
        for ilink in j_obj[il]:
            start = ilink['start']
            end = ilink['end']
            assert j_obj['text'][start:end] == ilink['label']
            print('Internal Links: OK!')


def test_sections(j_obj):
    if 'sections' in j_obj.keys():
        for sec in j_obj['sections']:
            start = sec['start']
            end = sec['end']
            if 'title' in sec.keys():
                title = sec['title']
                assert j_obj['text'][start:end].startswith(title)
            print('Sections OK!')


def test_textinit(j_obj):
    pass


def main():
    parser = argparse.ArgumentParser(description='Tests json2Text.py with etWikiParsed Json file as input')
    parser.add_argument('input', metavar='I', type=str,
                       help='directory of json files')

    args = parser.parse_args()
    inp = args.input
    log = open(inp, 'r')
    j_obj = json.load(log)
    j_obj = json_format(j_obj)
    test_sections(j_obj)
    test_links(j_obj)
    test_textinit(j_obj)
    print('Done!')

if __name__ == '__main__':
    main()