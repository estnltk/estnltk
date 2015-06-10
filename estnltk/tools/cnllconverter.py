# -*- coding: utf-8 -*-
"""
Module that can read estner cnll files and write them as a JSON corpus.
"""
from __future__ import unicode_literals, print_function, absolute_import
import codecs
import json
import sys
from ..text import Text
from ..names import *

def get_texts_and_labels(sentence_chunk):
    """Given a sentence chunk, extract original texts and labels."""
    words = sentence_chunk.split('\n')
    texts = []
    labels = []
    for word in words:
        word = word.strip()
        if len(word) > 0:
            toks = word.split('\t')
            texts.append(toks[0].strip())
            labels.append(toks[-1].strip())
    return texts, labels

def parse_doc(doc):
    """Exract list of sentences containing (text, label) pairs."""
    word_spans = []
    sentence_spans = []
    sentence_chunks = doc.split('\n\n')
    sentences = []
    for chunk in sentence_chunks:
        sent_texts, sent_labels = get_texts_and_labels(chunk.strip())
        sentences.append(list(zip(sent_texts, sent_labels)))
    return sentences

def convert(document):
    """Convert a document to a Text object"""
    raw_tokens = []
    curpos = 0
    text_spans = []
    all_labels = []
    sent_spans = []
    word_texts = []
    for sentence in document:
        startpos = curpos
        for idx, (text, label) in enumerate(sentence):
            raw_tokens.append(text)
            word_texts.append(text)
            all_labels.append(label)
            text_spans.append((curpos, curpos+len(text)))
            curpos += len(text)
            if idx < len(sentence) - 1:
                raw_tokens.append(' ')
                curpos += 1
        sent_spans.append((startpos, curpos))
        raw_tokens.append('\n')
        curpos += 1
    return {
        TEXT: ''.join(raw_tokens),
        WORDS: [{TEXT: text, START: start, END: end, LABEL: label} for text, (start, end), label in zip(word_texts, text_spans, all_labels)],
        SENTENCES: [{START: start, END:end} for start, end in sent_spans]
    }

def parse_cnll(fnm):
    with codecs.open(fnm, 'rb', 'utf-8') as f:
        all = f.read()
        docs = all.split('\n--\n')
        for doc in docs:
            text = Text(convert(parse_doc(doc.strip())))
            print (json.dumps(text))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        parse_cnll(sys.argv[1])
