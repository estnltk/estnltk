# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.core import as_unicode
from estnltk.names import *

from collections import Counter
from itertools import izip

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
    

class Element(dict):
    '''Element is a basic composition object of Estnltk corpora.
    It must have TEXT, START, END, REL_START and REL_END attributes.
    '''
    
    def __init__(self, data=None, **kwargs):
        '''Initialize a corpus element.
        
        Parameters
        ----------
        data: dict
            The dictionary containing TEXT, START, END, REL_START and REL_END
            attributes. If not given, these attributes must be
            given as keyword arguments.
        
        Keyword parameters
        ------------------
        start: int
            The START attribute
        end: int
            The END attribute
        rel_start: int
            The REL_START attribute.
        rel_end: int
            The REL_END attribute.
        text: str
            The TEXT attribute.
        '''
        if data is None:
            data = kwargs
        super(Element, self).__init__(data)
        self.force_cast()
        self.assert_valid()

    def force_cast(self):
        '''Cast the necessary attributes to correct types.'''
        self[TEXT] = as_unicode(self.text)
        self[START] = int(self.start)
        self[END] = int(self.end)
        self[REL_START] = int(self.rel_start)
        self[REL_END] = int(self.rel_end)

    def assert_valid(self):
        '''Perform assertions to ensure sanity checks on the
        attribute values.'''
        assert self.start >= 0
        assert self.rel_start >= 0
        assert self.start <= self.end
        assert self.rel_start <= self.rel_end
        assert self.end - self.start == self.rel_end - self.rel_start
        assert len(self.text) == self.end - self.start

    @property
    def span(self):
        return (self.start, self.end)

    @property
    def rel_span(self):
        return (self.rel_start, self.rel_end)

    @property
    def start(self):
        return self[START]
    
    @property
    def end(self):
        return self[END]
    
    @property
    def rel_start(self):
        return self[REL_START]
        
    @property
    def rel_end(self):
        return self[REL_END]
        
    @property
    def text(self):
        return self[TEXT]
        

class Word(Element):
    '''Word element of Estnltk corpora.'''
    
    def __init__(self, data=None, **kwargs):
        super(Word, self).__init__(data, **kwargs)
    
    @property
    def analysis(self):
        return self.get(ANALYSIS, [])
    
    @property
    def lemmas(self):
        return [a[LEMMA] for a in self.analysis]
        
    @property
    def lemma(self):
        return most_frequent(self.lemmas)
    
    @property
    def postags(self):
        return [a[POSTAG] for a in self.analysis]
        
    @property
    def postag(self):
        return most_frequent(self.postags)
        
    @property
    def forms(self):
        return [a[FORM] for a in self.analysis]
    
    @property
    def form(self):
        return most_frequent(self.forms)
    
    @property
    def label(self):
        return self.get(LABEL, None)
        
    @property
    def roots(self):
        return [a[ROOT] for a in self.analysis]
        
    @property
    def root(self):
        return most_frequent(self.roots)
    
    @property
    def clitics(self):
        return [a[CLITIC] for a in self.analysis]
        
    @property
    def clitic(self):
        return most_frequent(self.clitics)
        
    @property
    def root_tokens(self):
        return [a[ROOT_TOKENS] for a in self.analysis]


def most_frequent(elements):
    '''Return the most frequent element from the list.
    In case of equal counts, return alphabetically first.
    
    Parameteres
    -----------
    elements: list of str
        The list of elements to choose the most frequent from.
        
    Returns
    -------
    str
        The most frequent (or alphabetically first) element
    None
        In case of empty input.
    '''
    if len(elements) == 0:
        return
    cntr = Counter()
    hest_count = 0
    best = []
    for e in elements:
        cntr[e] += 1
        if cntr[e] > best_count:
            best_count = cntr[e]
            best[:] = []
            best.append(e)
        elif cntr[e] == best_count:
            best.append(e)
    best.sort()
    return best[0]


class Sentence(Element):
    '''Sentence element of Estnltk corpora.'''
    
    def __init__(self, data=None, **kwargs):
        super(Element, self).__init__(data, **kwargs)
    
    @overrides(Element)
    def assert_valid(self):
        super(Sentence, self).is_valid()
        assert WORDS in self
        self.assert_consequent_words()
        self.assert_word_splices()
            
    def assert_consequent_words(self):
        for p, n in izip(self[WORDS], self[WORDS][1:]):
            assert p.end <= n.start

    def assert_word_splices(self):
        for word in self[WORDS]:
            assert word.text == self.text[word.rel_start:word.rel_end]
            

class Document(dict):
    '''Estnltk Document object.

    A document must have consistent indices throughout its structure.
    All absoulte indices and text splices must match top-level texts.
    '''
    
    def __init__(self, *args, **kwargs):
        dict.__init__(*args, **kwargs)


