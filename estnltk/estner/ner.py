# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function


class Token(dict):
    '''Token represents a single word in NER system.'''
    
    def __init__(self, *args, **kw):
        super(Token, self).__init__(*args, **kw)
        super(Token, self).__setitem__('F', [])
        self.next = None
        self.prew = None
        self.predicted_label = 'O'
        
    def __setitem__(self, key, val):
        if val:
            super(Token, self).__setitem__(key, val)
            
    def features_to_string(self):
        try:
            s = " ".join(self['F'])
        except:
            print ('F:', self['F'])
            raise
        return s
        
    def feature_list(self):
        return self['F']
        
    def __str__(self):
        return self.word.encode("utf8")
        
    def __repr__(self):
        return self.word.encode("utf8")
        
    def __unicode__(self):
        return self.word


class Collection(object):
    '''Collection of NER documents.'''
    
    def __init__(self, documents):
        self.documents = documents
        
    @property
    def tokens(self):
        return (d for d in self.documents for t in d.tokens) 


class Document():
    '''A document is a collection of NER sentences.'''
    
    def __init__(self):
        self.docid = None
        self.snts = []
        self.tokens = []
        
    def __unicode__(self):
        return ". ".join(unicode(snt) for snt in self.snts)


class Sentence(list):
    '''Sentence is a list of NER tokens.'''
    
    def __init__(self, *args):
        super(Sentence, self).__init__(*args)
        
    def __unicode__(self):
        return " ".join(token.word for token in self)
        
    def __str__(self):
        return " ".join(token.word for token in self).encode('utf8')
