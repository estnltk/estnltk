# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
__author__ = 'Andres'

from .. import Text
from .jsonWriter import fileCleanerRegEx
import argparse
import codecs
import json
import os
import re

count = 0
printcount = 0

def parse_data(j_obj):
    data = {}
    keys = j_obj.keys()
    for key in keys:
        if key == 'sections':
            continue
        data[key] = j_obj[key]

    return data


def parse_text(sections, title):
    text = ''
    internal_links = []
    external_links = []
    start = 0
    flats = []
    flats = flatten(sections, flats)

    nl = '\n\n'
    el = 'external_links'
    il = 'internal_links'
    for section in flats:
        section['start'] = start
        if 'title' in section.keys():
            title = section['title']

        text += title+'\n'
        offset = len(text)

        if il in section.keys():
            for j in section[il]:
                j['start'] += offset
                j['end'] += offset
                internal_links.append(j)
        if el in section.keys():
            for j in section[el]:
                if 'start' in j: # TODO: Timo added the "if" construct, because some articles failed processing with python3, confirm it is okay
                    j['start'] += offset
                    j['end'] += offset
                external_links.append(j)

        text += section['text']+nl
        section['end'] = len(text)-2
        start = len(text)
        section.pop('text', None)
        section.pop(il, None)
        section.pop(el, None)



    return text, flats, internal_links, external_links


def flatten(l, new=[]):
    for i in l:
        new.append(i)
        if 'sections' in i.keys():
            flatten(i['sections'], new)
            i.pop('sections', None)
    return new


def json_format(j_obj):
    new = {}
    new['data'] = parse_data(j_obj)
    title = new['data']['title']
    text, sections, il, el  = parse_text(j_obj['sections'], title)
    if text:
        new['text'] = text
    if sections:
        new['sections'] = sections
    if il:
        new['internal_links'] = il
    if el:
        new['external_links'] = el
    return new


def json_2_text(inp, out, verbose = False):
    """Convert a Wikipedia article to Text object.
    Concatenates the sections in wikipedia file and rearranges other information so it
    can be interpreted as a Text object.

    Links and other elements with start and end positions are annotated
    as layers.

    Parameters
    ----------
    inp: directory of parsed et.wikipedia articles in json format

    out: output directory of .txt files

    verbose: if True, prints every article title and total count of converted files
             if False prints every 50th count
    Returns
    -------
    estnltk.text.Text
        The Text object.
    """

    for root, dirs, filenames in os.walk(inp):
        for f in filenames:
            log = codecs.open(os.path.join(root, f), 'r')
            j_obj = json.load(log)
            j_obj = json_format(j_obj)

            #not needed, cause the json_format takes care of the right structuring
            #text = Text(j_obj)

            textWriter(j_obj, out, verbose)

def textWriter(jsonObj, dir, verbose):
    global count
    global printcount
    if not os.path.exists(dir):
        os.makedirs(dir)

    with codecs.open(dir+re.sub(fileCleanerRegEx,'',jsonObj['data']['title']+".txt"), 'w', encoding='utf-8') as outfile:
        json.dump(jsonObj, outfile, sort_keys = True, indent = 4)

    count += 1
    printcount +=1

    if verbose:
        print(jsonObj['data']['title'], 'Count:', count)
    elif printcount == 50:
        print(count)
        printcount = 0


def main():


    parser = argparse.ArgumentParser(description='Convert Wikipedia .json files to Text .json files.')


    parser.add_argument('input', metavar='I', type=str,
                       help='Input folder containing extracted Wikipedia articles (in JSON format)')

    parser.add_argument('output', metavar='O', type=str,
                       help='Output folder for converted JSON files')

    parser.add_argument("-v", "--verbose", action="store_true",
                        help='Print written article titles and count.')

    args = parser.parse_args()
    inp = args.input
    out = args.output
    verbose = args.verbose

    if not os.path.exists(inp):
        print('Input directory does not exist!')

    if not os.path.exists(out):
        os.mkdir(out)

    json_2_text(inp, out, verbose)
    print('Done!')


if __name__ == '__main__':
    main()