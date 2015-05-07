# -*- coding: utf-8 -*-
''' Contains classes which model text documents and their contents'''
from __future__ import unicode_literals, print_function


class Token(dict):
    '''Token represents a single word in NER system.'''

    def __init__(self, *args, **kw):
        super(Token, self).__init__(*args, **kw)
        super(Token, self).__setitem__('F', [])
        self.next = None
        self.prew = None


    def __setitem__(self, key, val):
        # features with val=None are turned off, ignore them
        if val:
            super(Token, self).__setitem__(key, val)


    def features_to_string(self):
        return  " ".join(self['F'])


    def feature_list(self):
        return self['F']


    def __unicode__(self):
        return self.word


class Collection(object):
    '''A collection of NER documents.'''

    def __init__(self, documents):
        self.documents = documents


    @property
    def tokens(self):
        return (d for d in self.documents for t in d.tokens) 


class Document(object):
    '''A document is a collection of NER sentences.'''


    def __init__(self):
        self.docid = None
        self.snts = []
        self.tokens = []


    def __repr__(self):
        return " ".join(repr(snt) for snt in self.snts)


class Sentence(list):
    '''Sentence is a list of NER tokens.'''


    def __init__(self, *args):
        super(Sentence, self).__init__(*args)


    def __repr__(self):
        return " ".join(token.word for token in self)
