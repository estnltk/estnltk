# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .javaprocess import JavaProcess, JAVARES_PATH
from .names import *

from pprint import pprint

import os
import json
import datetime


class TimexTagger(JavaProcess):
    """Class for extracting temporal (TIMEX) expressions."""
    
    def __init__(self):
        JavaProcess.__init__(self, 'Ajavt.jar', ['-pyvabamorf', '-r', os.path.join(JAVARES_PATH, 'reeglid.xml')])

    def tag_document(self, document, **kwargs):
        # get the arguments
        remove_unnormalized_timexes = kwargs.get('remove_unnormalized_timexes', True)
        creation_date = kwargs.get('creation_date', datetime.datetime.now())
        creation_date = creation_date.strftime('%Y-%m-%dT%H:%M')

        # add creation date to document
        document[CREATION_DATE] = creation_date

        # detect timexes
        input_data = {
            CREATION_DATE: creation_date,
            SENTENCES: [{WORDS: words} for words in document.divide()]
        }
        output = json.loads(self.process_line(json.dumps(input_data)))

        # process output
        timexes = collect_timexes(output)
        if remove_unnormalized_timexes:
            timexes = remove_unnormalized(timexes)

        text = document.text
        document[TIMEXES] = [fix_text(rebase_zero(timex), text) for tid, timex in sorted(timexes.items())]
        return document


RENAMING_MAP = {
    'temporalFunction': TMX_TEMP_FUNCTION,
    'anchorTimeID': TMX_ANCHOR,
    'beginPoint': TMX_BEGINPOINT,
    'endPoint': TMX_ENDPOINT,
}


def rename_attributes(timex):
    # rename javaStyle to python_style
    for oldKey, newKey in RENAMING_MAP.items():
        if oldKey in timex:
            timex[newKey] = timex[oldKey]
            del timex[oldKey]
    # trim "t" from id and anchor time
    for k, v in timex.items():
        if k in [TMX_ID, TMX_ANCHOR] and isinstance(v, str) and v.startswith('t'):
            timex[k] = int(v[1:])
    return timex

def collect_timexes(output):
    timexes = {}
    for sentidx, sentence in enumerate(output[SENTENCES]):
        for wordidx, word in enumerate(sentence[WORDS]):
            if TIMEXES in word:
                for timex in word[TIMEXES]:
                    timex = rename_attributes(timex)
                    timex[START] = word[START]
                    timex[END] = word[END]
                    # merge with existing reference to same timex, if it exists
                    tid = timex[TMX_ID]
                    if tid in timexes:
                        for k, v in timexes[tid].items():
                            if k == START:
                                timex[START] = min(v, timex[START])
                            elif k == END:
                                timex[END] = max(v, timex[END])
                            else:
                                timex[k] = v
                    timexes[tid] = timex
    return timexes

def remove_unnormalized(timexes):
    return dict((tid, timex) for tid, timex in timexes.items() if TMX_TYPE in timex and TMX_VALUE in timex)

def rebase_zero(timex):
    timex[TMX_ID] = timex[TMX_ID] - 1
    if TMX_ANCHOR in timex:
        timex[TMX_ANCHOR] = timex[TMX_ANCHOR]-1
    return timex

def fix_text(timex, text):
    timex[TEXT] = text[timex[START]:timex[END]]
    return timex