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
    
    # clause specific
    
    @property
    def clause_indices(self):
        return [w.clause_index for w in self.words]
    
    @property
    def clause_annotations(self):
        return [w.clause_annotation for w in self.words]
    
    @property
    def clauses(self):
        return self.elements(CLAUSES)
    
    @property
    def verb_chains(self):
        return self.elements(VERB_CHAINS)
        
    @property
    def named_entities(self):
        return self.elements(NAMED_ENTITIES)
        
    @property
    def timexes(self):
        return self.elements(TIMEXES)

        
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
        data : dict
            The dictionary containing TEXT, START, END, REL_START and REL_END
            attributes. If not given, these attributes must be
            given as keyword arguments.
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
        elif what == WORDS:
            return [w for w in self[WORDS]]
        elif what == NAMED_ENTITIES:
            return self.named_entities
        elif what == CLAUSES:
            return self.clauses
        elif what == TIMEXES:
            return self.timexes
        elif what == VERB_CHAINS:
            return self.verb_chains
        return super(Sentence, self).elements(what)
        
    @property
    @overrides(Corpus)
    def named_entities(self):
        nes = []
        word_start = -1
        labels = self.labels + ['O'] # last is sentinel
        for i, l in enumerate(labels):
            if l.startswith('B-') or l == 'O':
                if word_start != -1:
                    ne = NamedEntity(self, word_start, i)
                    nes.append(ne)
                if l.startswith('B-'):
                    word_start = i
                else:
                    word_start = -1
        return nes
        
    @property
    @overrides(Corpus)
    def clauses(self):
        clauses = {}
        for i, w in enumerate(self[WORDS]):
            idx = w.clause_index
            clause = clauses.get(idx, [])
            clause.append(i)
            clauses[idx] = clause
        return [Clause(self, clauses[k]) for k in sorted(clauses.keys())]
    
    @property
    @overrides(Corpus)
    def timexes(self):
        timex_data = {}
        for i, w in enumerate(self[WORDS]):
            if TIMEXES in w:
                for timex in w[TIMEXES]:
                    data = timex_data.get(timex[TMX_ID], [])
                    data.append((i, timex))
                    timex_data[timex[TMX_ID]] = data
        timex_objects = []
        for k, timexes in timex_data.items():
            for (i, t1), (j, t2) in zip(timexes, timexes[1:]):
                assert i == j-1 # assert that timexes are consequent
            start_word = timexes[0][0]
            end_word = timexes[-1][0] + 1
            timex_objects.append(Timex(self, start_word, end_word, timexes[0][1]))
        return timex_objects
    
    @property
    @overrides(Corpus)
    def verb_chains(self):
        if VERB_CHAINS in self:
            return [VerbChain(self, chain[PHRASE], chain) for chain in self[VERB_CHAINS]]
        return []
    
    def __repr__(self):
        return repr('Sentence({0})'.format(self.text[:24] + '...'))
        

class ConsequentSentenceElement(ElementMixin):
    '''Some elements such as named entities and timexes may consist
    of more than a single word. This class encapsulates functionality
    to work with them.
    The word indices define a range [word_start, word_end)
    
    Parameters
    ----------
    sentence: :class:`estnltk.corpus.Sentence`
        The sentence containing the consequent elements.
    word_start: int
        The start index of the word (including)
    word_end: int
        The end index of the word (excluding)
        
    Attributes
    ----------
    sentence: :class:`estnltk.corpus.Sentence`
        The sentence containing the consequent elements.
    '''
    
    def __init__(self, sentence, word_start, word_end):
        start_word = sentence[WORDS][word_start]
        end_word = sentence[WORDS][word_end-1]
        rel_start = start_word.rel_start
        rel_end = end_word.rel_end
        text = sentence.text[rel_start:rel_end]
        data = {
            START: start_word.start,
            END: end_word.end,
            REL_START: rel_start,
            REL_END: rel_end,
            WORD_START: word_start,
            WORD_END: word_end,
            TEXT: text
        }
        self.sentence = sentence
        super(ConsequentSentenceElement, self).__init__(data)
        
    @overrides(ElementMixin)
    def assert_valid(self):
        super(ConsequentSentenceElement, self).assert_valid()
        assert WORD_START in self
        assert WORD_END in self
        
    @property
    def word_start(self):
        '''Returns
        --------
        int
            The start position of the first named entity word in the sentence.
        '''
        return self[WORD_START]
    
    @property
    def word_end(self):
        '''Returns
        --------
        int
            The position after the last entity word in the sentence.
            Therefore you can use `words[word_start:word_end]` to obtain
            the words of a named entity in the sentence.
        '''
        return self[WORD_END]
    
    @property
    def word_span(self):
        '''Returns
        -------
        (int, int)
            The start and end positions of the named entity words.
        '''
        return (self.word_start, self.word_end)
    
    @property
    def word_indices(self):
        '''Returns
        -------
        list of int
            The indices of words in the sentence.
        '''
        return list(range(self.word_start, self.word_end))
        
    @property
    def words(self):
        '''Returns
        -------
        list of :class:`estnltk.corpus.Word'
            words of the named entity.
        '''
        return [self.sentence[WORDS][i] for i in self.word_indices]


class NamedEntity(ConsequentSentenceElement):
    '''Named entities have to be constructed from sentences containing
    the labelled words. Named entity represents a group of words
    making up the named entity, such as *Toomas Hendrik Ilves*.
    
    Parameters
    ----------
    sentence: :class:estnltk.corpus.Sentence
        The sentence, where the named entity is found.
    word_start: int
        The index of the word in the sentence, where the named
        entity starts.
    word_end: int
        The index of the word in the sentence, where the named
        entity ends.
    '''
    
    def __init__(self, sentence, word_start, word_end):
        self[LABEL] = sentence[WORDS][word_start].label[2:]
        super(NamedEntity, self).__init__(sentence, word_start, word_end)
        
    
    @overrides(ConsequentSentenceElement)
    def assert_valid(self):
        super(NamedEntity, self).assert_valid()
        assert LABEL in self
        assert self[LABEL] != 'O'
        for i, w in enumerate(self.words):
            if i == 0:
                assert w.label == 'B-' + self.label
            else:
                assert w.label == 'I-' + self.label
    
    @property
    def label(self):
        '''The labels of named entity words have either prefixes
        **B-** or **I-**, denoting *beginning* and *inside* respectively.
        However, the real label is stored as a suffix, which can be
        retrieved using this property.
        
        Returns
        -------
        str
            The label of the named entity.
        '''
        return self[LABEL]
        
    @property
    def lemma(self):
        '''Returns
        --------
        str
            The named entity lemma ie the word lemmas separated by space.
        '''
        return ' '.join([w.lemma for w in self.words]).lower()
    
    def __repr__(self):
        return repr('NamedEntity({0}, {1})'.format(self.lemma, self.label))
        

class Timex(ConsequentSentenceElement):
    '''Temporal Expressions Tagger identifies temporal expression phrases in text and
    normalizes these expressions in a format similar to TimeML's TIMEX3.
    '''
    
    def __init__(self, sentence, word_start, word_end, data):
        for k, v in data.items():
            self[k] = v
        super(Timex, self).__init__(sentence, word_start, word_end)
        
        
    @overrides(ConsequentSentenceElement)
    def assert_valid(self):
        super(Timex, self).assert_valid()
        assert TMX_ID in self
        assert TMX_TYPE in self
        assert TMX_VALUE in self

    @property
    def id(self):
        '''Returns
        --------
        int
            The timex identificator.'''
        return self[TMX_ID]
    
    @property
    def type(self):
        '''Returns
        --------
        str
            One of the following: "DATE", "TIME", "DURATION", "SET"
        '''
        return self[TMX_TYPE]
    
    @property
    def value(self):
        '''Returns
        --------
        str
            calendrical value (largely follows TimeML TIMEX3 value format)
        '''
        return self[TMX_VALUE]
        
    @property
    def temporal_function(self):
        '''Returns
        --------
        str
            whether the "value" was found by heuristics/calculations (thus can be wrong): "true", "false"
        '''
        return self.get(TMX_TEMP_FUNCTION, None)
    
    @property
    def mod(self):
        '''Returns
        --------
        str
            Largely follows TimeML TIMEX3 mod format, with two additional values
            used to mark first/second half of the date/time (e.g. "in the first 
            half of the month"):  FIRST_HALF, SECOND_HALF;
        '''
        return self.get(TMX_MOD, None)
    
    @property
    def anchor_id(self):
        '''Returns
        --------
        int
            points to the temporal expression (by identifier) that this expression 
            has been anchored to while calculating or determining the value;
            0 -- means that the expression is anchored to document creation 
            time;
        '''
        return self.get(TMX_ANCHOR, None)
    
    @property
    def begin_point(self):
        '''Returns
        --------
        str
            in case of DURATION: points to the temporal expression (by identifier)
            that serves as a beginning point of this duration;
            "?" -- indicates problems on finding the beginning point;
        '''
        return self.get(TMX_BEGINPOINT, None)
    
    @property
    def end_point(self):
        '''Returns
        --------
        str
            in case of DURATION: points to the temporal expression (by identifier)
            that serves as an ending point of this duration;
            "?" -- indicates problems on finding the ending point;
        '''
        return self.get(TMX_ENDPOINT, None)
    
    @property
    def quant(self):
        '''Returns
        --------
        str
            Quantifier; Used only in some SET expressions, e.g. quant="EVERY"
        '''
        return self.get(TMX_QUANT, None)
    
    @property
    def freq(self):
        '''Returns
        --------
        str
            Used in some SET expressions, marks frequency of repetition, e.g.
            "three days in each month" will be have freq="3D"
        '''
        return self.get(TMX_FREQ, None)
    
    def __repr__(self):
        return repr('Timex({0}, {1}, {2}, [timex_id={3}])'.format(self.text, self.type, self.value, self.id))


class SparseSentenceElement(object):
    '''Sentence elements like clauses and verb chains usually span
    more than a single word and there can be gaps between the indices.
    SparseSentenceElement class contains common functinality for these elements.
    '''
    
    def __init__(self, sentence, indices):
        assert len(indices) > 0
        self._sentence = sentence
        self._word_indices = indices
        
    @property
    def sentence(self):
        return self._sentence
        
    @property
    def text(self):
        return ' '.join(self.text_groups)
    
    @property
    def text_groups(self):
        return [self.sentence.text[self.sentence[WORDS][start].rel_start:self.sentence[WORDS][end-1].rel_end] for start, end in self.word_group_spans]
    
    @property
    def words(self):
        return [self.sentence[WORDS][i] for i in self.word_indices]
        
    @property
    def word_indices(self):
        return self._word_indices
    
    @property
    def word_groups(self):
        return [[w for w in self.sentence[WORDS][start:end]] for (start, end) in self.group_word_spans]
    
    @property
    def word_group_spans(self):
        '''Return list of consequent index spans.'''
        start_idx = self.word_indices[0]
        last_idx = start_idx
        groups = []
        for i in self.word_indices[1:]:
            if i > start_idx + 1:
                groups.append((start_idx, last_idx+1))
                start_idx = i
            last_idx = i
        groups.append((start_idx, last_idx+1))
        return groups


class Clause(SparseSentenceElement):
    
    def __init__(self, sentence, indices):
        super(Clause, self).__init__(sentence, indices)
        self._clause_index = sentence[WORDS][indices[0]].clause_index
    
    @property
    def clause_index(self):
        return self._clause_index
     
    def __repr__(self):
        return repr('Clause({0} [clause_index={1}])'.format(self.text, self.clause_index))
        

class VerbChain(SparseSentenceElement):
    
    def __init__(self, sentence, indices, data):
        super(VerbChain, self).__init__(sentence, indices)
        self._data = data
    
    @property
    def data(self):
        return self._data
 
    @property
    def polarity(self):
        return self._data[POLARITY]
        
    @property
    def roots(self):
        return self._data[ROOTS]
        
    @property
    def lemma(self):
        '''Verb chain lemma. A unique identificator for the chain.'''
        return '_'.join(self.roots)
    
    @property
    def pattern(self):
        return '+'.join(self._data[PATTERN])
        
    @property
    def pattern_tokens(self):
        return self._data[PATTERN]
        
    @property
    def other_verbs(self):
        return self._data[OTHER_VERBS]
        
    @property
    def analysis_ids(self):
        return self._data[ANALYSIS_IDS]
        
    @property
    def morph(self):
        return self._data[MORPH]
        
    @property
    def clause_index(self):
        return self._data[CLAUSE_IDX]
        
    @property
    def word_indices(self):
        '''Consequent word indices.'''
        return list(sorted(self._word_indices))
        
    @property
    def word_indices_chain(self):
        '''The real order of word indices making up a chain.'''
        return self._word_indices
    
    def __repr__(self):
        return repr('VerbChain({0}, {1}, {2}, {3})'.format(self.text, self.pattern, self.lemma, self.polarity))


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
        
    @property
    def clause_index(self):
        return self.get(CLAUSE_IDX, None)
    
    @property
    def clause_annotation(self):
        return self.get(CLAUSE_ANNOTATION, None)
        
    @property
    def timex_data(self):
        '''Returns
        --------
        list of str
            List of dictionaries containing TIMEX data (TMX_ID, TMX_TYPE, TMX_VALUE) etc.
            Note that for disambiguated morphological data, there can be more
            timexes.
        '''
        return self.get(TIMEXES, [])


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
