# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.core import as_unicode, overrides
from estnltk.names import *

from collections import Counter
from pprint import pprint

import json
    

class Corpus(object):
    
    @staticmethod
    def construct(data):
        return construct_corpus(data)
    
    @staticmethod
    def from_json(data):
        return construct_corpus(data)
        
    def to_json(self):
        return json.loads(json.dumps(self))
        
    # Methods for returning corpus elements
    def elements(self, what):
        raise NotImplementedError()
    
    @property
    def words(self):
        return self.elements(WORDS)
    
    @property
    def sentences(self):
        return self.elements(SENTENCES)
    
    @property
    def paragraphs(self):
        return self.elements(PARAGRAPHS)
    
    @property
    def documents(self):
        return self.elements(DOCUMENTS)
        
    # Methods for returning raw texts
    def texts(self, what):
        return [e.text for e in self.elements(what)]

    @property
    def word_texts(self):
        return self.texts(WORDS)
    
    @property    
    def sentence_texts(self):
        return self.texts(SENTENCES)
    
    @property
    def paragraph_texts(self):
        return self.texts(PARAGRAPHS)
    
    @property
    def document_texts(self):
        return self.texts(DOCUMENTS)
    
    # methods for returning spans    
    @property
    def word_spans(self):
        return [w.span for w in self.words]
        
    @property
    def sentence_spans(self):
        return [s.span for s in self.sentences]
        
    @property
    def paragraph_spans(self):
        return [p.span for p in self.paragraphs]
    
    @property
    def word_rel_spans(self):
        return [w.rel_span for w in self.words]
        
    @property
    def sentence_rel_spans(self):
        return [s.rel_span for s in self.sentences]
        
    @property
    def paragraph_rel_spans(self):
        return [p.rel_span for p in self.paragraphs]
        
    # methods for returning word specific data
    @property
    def lemmas(self):
        return [w.lemma for w in self.words]
        
    @property
    def postags(self):
        return [w.postag for w in self.words]
        
    @property
    def forms(self):
        return [w.form for w in self.words]
    
    @property
    def endings(self):
        return [w.ending for w in self.words]
    
    @property
    def labels(self):
        return [w.label for w in self.words]
        
    @property
    def roots(self):
        return [w.root for w in self.words]
        
    @property
    def clitics(self):
        return [w.clitic for w in self.words]
    
    @property
    def root_tokens(self):
        return [w.root_tokens for w in self.words]
    
    # methods for returning sentence specific data
    
    @property
    def clauses(self):
        raise NotImplementedError()
    
    @property
    def verb_phrases(self):
        raise NotImplementedError()
    
    # other methods
    
    def __repr__(self):
        return repr('Corpus')
    
    def apply(self, processor, **kwargs):
        '''Apply a textprocessor.TextProcessor instance on this corpus.'''
        return processor.process_corpus(self, inplace=True, **kwargs)


class List(list, Corpus):
    
    @overrides(Corpus)
    def elements(self, what):
        elements = []
        for e in self:
            if isinstance(e, Corpus):
                elements.extend(e.elements(what))
        return elements
        
    def __repr__(self):
        return repr('List')


class Dictionary(dict, Corpus):

    @overrides(Corpus)
    def elements(self, what):
        elements = []
        for k, v in self.items():
            if isinstance(v, Corpus):
                elements.extend(v.elements(what))
        return elements
        
    def __repr__(self):
        return repr('Dictionary')
    

class ElementMixin(dict):
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
        super(ElementMixin, self).__init__(data)
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
        

class Document(ElementMixin, Dictionary):
    '''Estnltk Document object.

    A document must have consistent indices throughout its structure.
    All absoulte indices and text splices must match top-level texts.
    '''
    
    def __init__(self, data=None, **kwargs):
        super(Document, self).__init__(data, **kwargs)
    
    
    @overrides(ElementMixin)
    def force_cast(self):
        super(Document, self).force_cast()
        
        def cast(w, cast_type):
            if not isinstance(w, cast_type):
                return cast_type(w)
            return w
        if SENTENCES in self:
            self[SENTENCES] = List([cast(w, Sentence) for w in self[SENTENCES]])
        if PARAGRAPHS in self:
            self[PARAGRAPHS] = List([cast(w, Paragraph) for w in self[PARAGRAPHS]])
            
    @overrides(Corpus)
    def elements(self, what):
        if what == DOCUMENTS:
            return [self]
        return super(Document, self).elements(what)
        
    def __repr__(self):
        return repr('Document({0})'.format(self.text[:24] + '...'))


class Paragraph(ElementMixin, Dictionary):
    '''Paragraph object.'''
    
    def __init__(self, data=None, **kwargs):
        super(Paragraph, self).__init__(data, **kwargs)
        
    @overrides(ElementMixin)
    def force_cast(self):
        super(Paragraph, self).force_cast()
        
        def cast(s):
            if not isinstance(s, Sentence):
                return Sentence(s)
            return w
            
        self[SENTENCES] = List([cast(s) for s in self[SENTENCES]])
        
    @overrides(ElementMixin)
    def assert_valid(self):
        super(Paragraph, self).assert_valid()
        assert SENTENCES in self
        
    @overrides(Corpus)
    def elements(self, what):
        if what == PARAGRAPHS:
            return [self]
        return super(Paragraph, self).elements(what)
        
    def __repr__(self):
        return repr('Paragraph({0})'.format(self.text[:24] + '...'))


class Sentence(ElementMixin, Dictionary):
    '''Sentence element of Estnltk corpora.
    
    Sentence uses WORDS attribute to list its words.
    '''
    
    def __init__(self, data=None, **kwargs):
        super(Sentence, self).__init__(data, **kwargs)
    
    @overrides(ElementMixin)
    def force_cast(self):
        super(Sentence, self).force_cast()
        
        def cast(w):
            if not isinstance(w, Word):
                return Word(w)
            return w
            
        self[WORDS] = List([cast(w) for w in self[WORDS]])
            
    
    @overrides(ElementMixin)
    def assert_valid(self):
        super(Sentence, self).assert_valid()
        assert WORDS in self
        self.assert_consequent_words()
        self.assert_word_splices()
            
    def assert_consequent_words(self):
        '''Check the START and END positions of consequent words.'''
        for p, n in zip(self[WORDS], self[WORDS][1:]):
            assert p.end <= n.start

    def assert_word_splices(self):
        '''Check that the word texts match the sentence texts.'''
        for word in self[WORDS]:
            assert word.text == self.text[word.rel_start:word.rel_end]
    
    @overrides(Corpus)
    def elements(self, what):
        if what == SENTENCES:
            return [self]
        return super(Sentence, self).elements(what)
        
    def __repr__(self):
        return repr('Sentence({0})'.format(self.text[:24] + '...'))
        

class Word(ElementMixin, Dictionary):
    '''Word element of Estnltk corpora.
    
    Word element can contain vast amount of different information
    starting from morphological analysis results to named entity
    labels.
    
    This is one of the central elements of the Estnltk corpora.
    '''
    
    def __init__(self, data=None, **kwargs):
        super(Word, self).__init__(data, **kwargs)
    
    @overrides(Corpus)
    def elements(self, what):
        if what == WORDS:
            return [self]
    
    def __repr__(self):
        return repr('Word({0})'.format(self.text))
    
    
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
    def endings(self):
        return [a[ENDING] for a in self.analysis]
    
    @property
    def ending(self):
        return most_frequent(self.endings)
    
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
        tokens = [tuple(a[ROOT_TOKENS]) for a in self.analysis]
        return list(most_frequent(tokens))


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
    elif len(elements) == 1:
        return elements[0]
        
    cntr = Counter()
    best_count = 0
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



def construct_corpus(data):
    if isinstance(data, Corpus):
        return data
    elif is_root_element(data):
        data = parse_root_element(data)
    elif isinstance(data, dict):
        return Dictionary(construct_corpus(v) for k, v in data.items())
    elif isinstance(data, list):
        return List(construct_corpus(e) for e in data)
    else:
        raise ValueError()
    return data


def is_root_element(data):
    '''Does the given element satisfy root element requirements:
    Contains all TEXT, START, END, REL_START, REL_END attributes.
    START = REL_START = 0
    END = REL_END     = len(TEXT)
    
    Parameters
    ----------
    data: dict
        The potential root element.
    
    Returns
    -------
    True
        If element satisfies root element requirements.
    False
        otherwise.
    '''
    return isinstance(data, dict) and \
           START in data and \
           END in data and \
           REL_START in data and \
           REL_END in data and \
           TEXT in data and \
           data[START] == 0 and \
           data[REL_START] == 0 and \
           data[END] == len(data[TEXT]) and \
           data[REL_END] == data[END]


def parse_root_element(data):
    if PARAGRAPHS in data:
        return Document(data)
    elif SENTENCES in data:
        return Paragraphs(data)
    elif WORDS in data:
        return Sentence(data)
