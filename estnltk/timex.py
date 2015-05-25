# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .javaprocess import JavaProcess, JAVARES_PATH
from .names import *

from pprint import pprint

import os
import json
import datetime


RENAMING_MAP = {
    'temporalFunction': TMX_TEMP_FUNCTION,
    'anchorTimeID': TMX_ANCHOR,
    'beginPoint': TMX_BEGINPOINT,
    'endPoint': TMX_ENDPOINT,
}

def prepare_data(document, process_as_whole):
    """Depending on whether we want to process one sentence at a time or full corpus at a time, prepare the input"""
    sentences = [s for s in document.split_by_sentences()]
    lines = []
    if process_as_whole:
        document_data = {
            CREATION_DATE: document[CREATION_DATE],
            SENTENCES: [{WORDS: s.words} for s in sentences]
        }
        lines.append(json.dumps(document_data))
    else:
        for sentence in sentences:
            sentence_data = {
                CREATION_DATE: document[CREATION_DATE],
                WORDS: sentence.words
            }
            lines.append(json.dumps(sentence_data))
    return lines

def collect_timexes(output):
    for line in output:
        line = json.loads(line)
        pprint(line)


class TimexTagger(JavaProcess):
    """Class for extracting temporal (TIMEX) expressions."""
    
    def __init__(self):
        JavaProcess.__init__(self, 'Ajavt.jar', ['-pyvabamorf', '-r', os.path.join(JAVARES_PATH, 'reeglid.xml')])

    def tag_document(self, document, **kwargs):
        # get the arguments
        process_as_whole = kwargs.get('process_as_whole', True)
        remove_unnormalized_timexes = kwargs.get('remove_unnormalized_timexes', True)
        creation_date = kwargs.get('creation_date', datetime.datetime.now())
        creation_date = creation_date.strftime('%Y-%m-%dT%H:%M')

        # analysis is required to detect timexes
        if not document.is_computed(ANALYSIS):
            document.compute_analysis()

        # add creation date to document
        document[CREATION_DATE] = creation_date

        # prepare data and process
        output = [self.process_line(line) for line in prepare_data(document, process_as_whole)]

        # collect timex information from output
        collect_timexes(output)


    def tag_separately(self, document, creation_date, remove_unnormalized_timexes):
        sentences = document.split_by_sentences()
        sent_spans = document.sentence_spans
        for sentidx, sentence in enumerate(sentences):
            # prepare data for Java library
            self.add_word_texts(sentence)
            data = {
                WORDS: sentence.words,
                CREATION_DATE: creation_date
            }
            dump = json.dumps(data)
            # process data with timex library
            result = json.loads(self.process_line(dump))
            # process the result
            result = self.rename_attributes(result[WORDS])
            if remove_unnormalized_timexes:
                result = self.remove_timexes_with_no_value_type(result)
            # add timex data to original document
            doc_words = document.get_elements_in_span(WORDS, sent_spans[sentidx])
            assert len(doc_words) == len(result)
            for word, result_word in zip(doc_words, result):
                if TIMEXES in result_word:
                    word[TIMEXES] = result_word[TIMEXES]
        return document

    def tag_full(self, document, remove_unnormalized_timexes):
        temp_doc = {
            CREATION_DATE: document[CREATION_DATE],
            SENTENCES: document.split_by_sentences()
        }
        processed_sentences = json.loads(self.process_line(json.dumps(document)))[SENTENCES]
        for input_sentence, processed_sentence in zip(document[SENTENCES], processed_sentences):
            processed_sentence = self.rename_attributes( processed_sentence[WORDS] )
            if remove_unnormalized_timexes:
                processed_sentence = self.remove_timexes_with_no_value_type(processed_sentence)
            for i in range(len( input_sentence[WORDS] )):
                input_word = input_sentence[WORDS][i]
                processed_word = processed_sentence[i]
                if TIMEXES in processed_word:
                    input_word[TIMEXES] = processed_word[TIMEXES]
        return corpus

    def rename_attributes(self, sentence):
        for word in sentence:
            if TIMEXES in word:
                for timex in word[TIMEXES]:
                    # rename javaStyle to python_style
                    for oldKey, newKey in RENAMING_MAP.items():
                        if oldKey in timex:
                            timex[newKey] = timex[oldKey]
                            del timex[oldKey]
                    # trim "t" from id and anchor time
                    for k, v in timex.items():
                        if k in [TMX_ID, TMX_ANCHOR] and isinstance(v, str) and v.startswith('t'):
                            timex[k] = int(v[1:])
        return sentence

    # Removes timexes that have no value or type specified
    # ( e.g. anaphoric references 'samal ajal', 'tol ajal' etc. that were left unsolved )
    def remove_timexes_with_no_value_type(self, sentence):
        seenTimexes     = dict()
        timexesToRemove = dict()
        for word in sentence:
            if TIMEXES in word:
                newTimexes = []
                for timex in word[TIMEXES]:
                    if timex[TMX_ID] not in seenTimexes:
                        seenTimexes[timex[TMX_ID]] = 1
                        if TMX_TYPE not in timex or TMX_VALUE not in timex:
                            timexesToRemove[timex[TMX_ID]] = 1
                        else:
                            newTimexes.append( timex )
                    elif timex[TMX_ID] in seenTimexes and timex[TMX_ID] not in timexesToRemove:
                        newTimexes.append( timex )
                if newTimexes:
                    word[TIMEXES] = newTimexes
                else:
                    del word[TIMEXES]
        return sentence