# -*- coding: utf-8 -*-
"""This module defines extractors that can be used to match rules with Text layer attributes."""
from __future__ import unicode_literals, print_function, absolute_import

from ..names import *


def texts_simple(text, layer):
    return ({TEXT: text, START: start, END: end} for text, (start, end) in zip(text.texts(layer), text.spans(layer)))


def texts_multi(text, layer):
    plain_text = text.text
    for starts, ends in text.spans(layer):
        for start, end in zip(starts, ends):
            yield {TEXT: plain_text[start:end], START: start, END:end}


def lemmas(text):
    return ({TEXT: lemma, START: start, END: end} for lemma, (start, end) in zip(text.lemmas, text.word_spans))


def postags(text):
    return ({TEXT: postag, START: start, END: end} for postag, (start, end) in zip(text.postags, text.word_spans))


def cases(text):
    return ({TEXT: case, START: start, END: end} for case, (start, end) in zip(text.cases, text.word_spans))


def ner_labels(text):
    for label, (start, end) in zip(text.named_entity_labels, text.named_entity_spans):
        yield {TEXT: label, START: start, END: end}


def timex_types(text):
    return ({TEXT: type, START: start, END: end} for type, (start, end) in zip(text.timex_types, text.timex_spans))

