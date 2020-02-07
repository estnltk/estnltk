# -*- coding: utf-8 -*-
"""Contains classes which model text documents, sentences and tokens"""
from __future__ import unicode_literals, print_function


class Token(dict):
    """Token represents a single word in NER system."""
    __slots__ = ('word', 'lemma', 'morph', 'label', 'next', 'prew')

    def __init__(self, word=None, lemma=None, morph=None, label=None, next=None, prew=None):
        super(Token, self).__init__(F=[])
        self.word = word
        self.lemma = lemma
        self.morph = morph
        self.label = label
        self.next = next
        self.prew = prew

    def __setitem__(self, key, val):
        # features with val=None are turned off, ignore them
        if val:
            super(Token, self).__setitem__(key, val)

    def features_to_string(self):
        return " ".join(self['F'])

    def feature_list(self):
        return self['F']

    def __unicode__(self):
        return self.word


class Document(object):
    """A document is a collection of NER sentences."""
    __slots__ = ('docid', 'sentences')

    def __init__(self, docid=None, sentences=None):
        self.docid = docid
        self.sentences = sentences

    @property
    def tokens(self):
        for s in self.sentences:
            for t in s:
                yield t

    def __repr__(self):
        return " ".join(repr(snt) for snt in self.sentences)


class Sentence(list):
    """Sentence is a list of NER tokens."""

    def __init__(self, *args):
        super(Sentence, self).__init__(*args)

    def __repr__(self):
        return " ".join(token.word for token in self)
