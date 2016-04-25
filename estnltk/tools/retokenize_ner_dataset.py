# -*- coding: utf-8 -*-
"""
This script is for retokenizing Estner training corpus.

It is required, because from time to time, Estnltk tokenizers change and this can
lower the efficiency of NE tagging, because training corpus and actual corpora have
different tokenization rules.

This script should be run every time something changes during tokenization.
"""
from __future__ import unicode_literals, print_function, absolute_import

from ..core import DEFAULT_NER_DATASET
from ..corpus import yield_json_corpus, write_json_corpus
from ..text import Text
from ..names import START, END, LABEL, NAMED_ENTITIES
from pprint import pprint
import sys


retokenized_docs = []

for doc in yield_json_corpus(DEFAULT_NER_DATASET):
    # get core data
    assert (doc.is_tagged('words') == True)
    assert (doc.is_tagged(LABEL) == True)
    assert (doc.is_tagged(NAMED_ENTITIES) == False)

    plain = doc.text
    spans = doc.named_entity_spans
    labels = doc.named_entity_labels

    # create a new text instance
    text = Text(plain)

    # tokenize the words with (possibly) new rules
    text.tokenize_words()

    # by default, words are not named entities
    for word in text['words']:
        word[LABEL] = 'O'

    # go through each previously annotated named entity and annotate respective words
    text['temp_layer'] = [{START: s, END: e, LABEL: label} for (s, e), label in zip(spans, labels)]
    for words, tmp_layer in zip(text.divide('words', 'temp_layer'), text['temp_layer']):
        label = tmp_layer[LABEL]
        first = True
        for w in words:
            if first:
                w[LABEL] = 'B-' + label
                first = False
            else:
                w[LABEL] = 'I-' + label
    del text['temp_layer']

    # print the words, labels for debugging
    print(text.get.word_texts.labels.as_dataframe)
    sys.stdout.flush()

    # add the documents
    retokenized_docs.append(text)

write_json_corpus(retokenized_docs, 'retokenized_estner.json')
