# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .core import as_unicode
from .names import *
from .vabamorf import morf as vabamorf
from .ner import NerTagger
from .timex import TimexTagger

import nltk.data
from nltk.tokenize.regexp import WordPunctTokenizer

import json
from copy import deepcopy
import codecs

# default functionality
sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
word_tokenizer = WordPunctTokenizer()
nertagger = None
timextagger = None

def load_default_ner_tagger():
    global nertagger
    if nertagger is None:
        nertagger = NerTagger()
    return nertagger

def load_default_timex_tagger():
    global timextagger
    if timextagger is None:
        timextagger = TimexTagger()
    return timextagger

class Text(dict):
    """Text class of estnltk.
    We represent each text as a dictionary, in order to make it easy to store as JSON.
    """

    def __init__(self, text_or_instance, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        if isinstance(text_or_instance, dict):
            super(Text, self).__init__(text_or_instance)
            self[TEXT] = as_unicode(self[TEXT], encoding)
        else:
            super(Text, self).__init__()
            self[TEXT] = as_unicode(text_or_instance, encoding)
        self.__kwargs = kwargs
        self.__load_functionality(**kwargs)
        self.__find_what_is_computed()

    def __load_functionality(self, **kwargs):
        self.__sentence_tokenizer = kwargs.get(
            'sentence_tokenizer', sentence_tokenizer)
        self.__word_tokenizer = kwargs.get(
            'word_tokenizer', word_tokenizer)
        self.__ner_tagger = kwargs.get( # ner models take time to load, load only when needed
            'ner_tagger', None)
        self.__timex_tagger = kwargs.get( # lazy loading for timex tagger
            'timex_tagger', None)

    def get_kwargs(self):
        return self.__kwargs

    def __find_what_is_computed(self):
        computed = set()
        if SENTENCES in self:
            computed.add(SENTENCES)
        if WORDS in self:
            computed.add(WORDS)
            if ANALYSIS in self[WORDS][0]:
                computed.add(ANALYSIS)
            if LABEL in self:
                computed.add(LABEL)
        if NAMED_ENTITIES in self:
            computed.add(NAMED_ENTITIES)
        self.__computed = computed
        return computed

    def is_computed(self, element):
        return element in self.__computed

    def __texts(self, element):
        text = self.text
        texts = []
        for data in self[element]:
            texts.append(text[data[START]:data[END]])
        return texts

    def __spans(self, element):
        spans = []
        for data in self[element]:
            spans.append((data[START], data[END]))
        return spans

    def __str__(self):
        return self[TEXT]

    def __unicode__(self):
        return self[TEXT]

    # ///////////////////////////////////////////////////////////////////
    # RETRIEVING AND COMPUTING PROPERTIES
    # ///////////////////////////////////////////////////////////////////

    @property
    def text(self):
        return self[TEXT]

    def compute(self, element):
        if element == SENTENCES:
            self.compute_sentences()
        elif element == WORDS:
            self.compute_words()
        elif element == ANALYSIS:
            self.compute_analysis()

    def compute_sentences(self):
        if self.is_computed(SENTENCES):
            self.__computed.remove(SENTENCES)
        tok = self.__sentence_tokenizer
        spans = tok.span_tokenize(self.text)
        dicts = []
        for start, end in spans:
            dicts.append({'start': start, 'end': end})
        self[SENTENCES] = dicts
        self.__computed.add(SENTENCES)

    @property
    def sentences(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self[SENTENCES]

    @property
    def sentence_texts(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__texts(SENTENCES)

    @property
    def sentence_spans(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__spans(SENTENCES)

    def compute_words(self):
        if self.is_computed(WORDS):
            self.__computed.remove(WORDS)
        tok = self.__word_tokenizer
        spans = tok.span_tokenize(self.text)
        dicts = []
        for start, end in spans:
            dicts.append({'start': start, 'end': end})
        self[WORDS] = dicts
        self.__computed.add(WORDS)

    def compute_analysis(self):
        if self.is_computed(ANALYSIS):
            self.__computed.remove(ANALYSIS)
        if not self.is_computed(WORDS):
            self.compute_words()
        tok = self.__word_tokenizer
        all_analysis = vabamorf.analyze(self.word_texts, **self.__kwargs)
        for word, analysis in zip(self.words, all_analysis):
            word[ANALYSIS] = analysis[ANALYSIS]
            word[TEXT] = analysis[TEXT]
        self.__computed.add(ANALYSIS)

    @property
    def words(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self[WORDS]

    @property
    def word_texts(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self.__texts(WORDS)

    @property
    def word_spans(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self.__spans(WORDS)

    @property
    def analysis(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return [word[ANALYSIS] for word in self.words]

    def __get_key(self, dicts, element):
        matches = []
        for dict in dicts:
            if element in dict:
                matches.append(dict[element])
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            if element == ROOT_TOKENS:
                return matches
            return '|'.join(sorted(set(matches)))

    def __get_analysis_element(self, element):
        return [self.__get_key(word[ANALYSIS], element) for word in self.words]

    @property
    def roots(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ROOT)

    @property
    def lemmas(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(LEMMA)

    @property
    def endings(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ENDING)

    @property
    def forms(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(FORM)

    @property
    def postags(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(POSTAG)

    @property
    def root_tokens(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ROOT_TOKENS)

    def compute_labels(self):
        if self.__ner_tagger is None:
            self.__ner_tagger = load_default_ner_tagger()
        self.__ner_tagger.tag_document(self)
        self.__computed.add(LABEL)

    @property
    def labels(self):
        if not self.is_computed(LABEL):
            self.compute_labels()
        return [word[LABEL] for word in self.words]

    def compute_named_entities(self):
        nes = []
        word_start = -1
        labels = self.labels + ['O'] # last is sentinel
        words = self.words
        label = 'O'
        for i, l in enumerate(labels):
            if l.startswith('B-') or l == 'O':
                if word_start != -1:
                    nes.append({START: words[word_start][START],
                                END: words[i-1][END],
                                LABEL: label})
                if l.startswith('B-'):
                    word_start = i
                    label = l[2:]
                else:
                    word_start = -1
        self[NAMED_ENTITIES] = nes
        self.__computed.add(NAMED_ENTITIES)

    @property
    def named_entities(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        phrases = self.split_by(NAMED_ENTITIES)
        return [' '.join(phrase.lemmas) for phrase in phrases]

    @property
    def named_entity_texts(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return self.__texts(NAMED_ENTITIES)

    @property
    def named_entity_spans(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return self.__spans(NAMED_ENTITIES)

    @property
    def named_entity_labels(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return [ne[LABEL] for ne in self[NAMED_ENTITIES]]

    def compute_timexes(self):
        if self.__timex_tagger is None:
            self.__timex_tagger = load_default_timex_tagger()
        self.__timex_tagger.tag_document(self, **self.__kwargs)
        self.__computed.add(TIMEXES)

    @property
    def timexes(self):
        if not self.is_computed(TIMEXES):
            self.compute_timexes()
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
            timex_objects.append(timexes[0][1])
        return timex_objects

    @property
    def timex_texts(self):
        return [timex[TEXT] for timex in self.timexes]

    @property
    def timex_values(self):
        return [timex[TMX_VALUE] for timex in self.timexes]

    # ///////////////////////////////////////////////////////////////////
    # SPELLCHECK
    # ///////////////////////////////////////////////////////////////////
    def spellcheck_words(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return [data[SPELLING] for data in vabamorf.spellcheck(self.word_texts, suggestions=False)]

    def spellcheck_suggestions(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return [data[SUGGESTIONS] for data in vabamorf.spellcheck(self.word_texts, suggestions=True)]

    def spellcheck(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return vabamorf.spellcheck(self.word_texts, suggestions=True)

    def fix_spelling(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        text = self.text
        fixed = vabamorf.fix_spelling(self.word_texts, join=False)
        spans = self.word_spans
        assert len(fixed) == len(spans)
        if len(spans) > 0:
            newtoks = []
            lastend = 0
            for fix, (start, end) in zip(fixed, spans):
                newtoks.append(text[lastend:start])
                newtoks.append(fix)
                lastend = end
            newtoks.append(text[lastend:])
            self[TEXT] = ''.join(newtoks)
            self.__computed.clear()

    # ///////////////////////////////////////////////////////////////////
    # SPLITTING
    # ///////////////////////////////////////////////////////////////////

    def __divide_to_spans(self, spans, elemlist):
        """TODO: make more efficient, currently O(n^2)."""
        N = len(spans)
        splits = [[] for _ in range(N)]
        for elem in elemlist:
            for spanidx, span in enumerate(spans):
                if elem[START] >= span[0] and elem[END] <= span[1]:
                    new_elem = deepcopy(elem)
                    new_elem[START] = elem[START] - span[0]
                    new_elem[END] = elem[END] - span[0]
                    splits[spanidx].append(new_elem)
                    break
        return splits

    def split_by(self, element):
        if not self.is_computed(element):
            self.compute(element)
        text = self.text
        split_spans = self.__spans(element)
        N = len(split_spans)
        results = [{TEXT: text[start:end]} for start, end in split_spans]
        for elem in self:
            if isinstance(self[elem], list):
                splits = self.__divide_to_spans(split_spans, self[elem])
                for idx in range(N):
                    results[idx][elem] = splits[idx]
        return [Text(res) for res in results]

    def split_by_sentences(self):
        return self.split_by(SENTENCES)

    def split_by_words(self):
        return self.split_by(WORDS)

    def get_elements_in_span(self, element, span):
        items = []
        if element in self:
            for item in self[element]:
                if item[START] >= span[0] and item[END] <= span[1]:
                    items.append(item)
        return items



def read_corpus(fnm):
    """Function to read a JSON corpus from a file.
    A JSON corpus contains one document per line, encoded in JSON.

    Parameters
    ----------
    fnm: str
        The filename of the corpus.

    Returns
    -------
    list of Text
    """
    documents = []
    with codecs.open(fnm, 'rb', 'ascii') as f:
        line = f.readline()
        while line != '':
            documents.append(Text(json.loads(line)))
            line = f.readline()
    return documents

if __name__ == '__main__':
    text = Text("See on esimene lause. See on teine lause!")
    from pprint import pprint
    print (text.lemmas)
    sents = text.split_by(SENTENCES)
    pprint (sents[1].lemmas)
