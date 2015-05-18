# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .core import as_unicode, POSTAG_DESCRIPTIONS, CASES, PLURALITY, VERB_TYPES
from .names import *
from .vabamorf import morf as vabamorf
from .ner import NerTagger
from .timex import TimexTagger

import six
import pandas
import nltk.data
import regex as re
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
    """

    def __init__(self, text_or_instance, **kwargs):
        """Initialize an Text object.

        Keyword parameters
        ------------------
        sentence_tokenizer: nltk.Tokenizer
        word_tokenizer: nltk.Tokenizer
        ner_tagger: NerTagger
        timex_tagger: TimexTagger
        creation_date: datetime.datetime
            For timex expression, the anchor time.
        """
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
        return self

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
        return self

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
        return self

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
        return self

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
    def postag_descriptions(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return [POSTAG_DESCRIPTIONS.get(tag, '') for tag in self.__get_analysis_element(POSTAG)]

    @property
    def root_tokens(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ROOT_TOKENS)

    @property
    def descriptions(self):
        descs = []
        for postag, form in zip(self.postags, self.forms):
            desc = VERB_TYPES.get(form, '')
            if len(desc) == 0:
                toks = form.split(' ')
                if len(toks) == 2:
                    plur_desc = PLURALITY.get(toks[0], None)
                    case_desc = CASES.get(toks[1], None)
                    toks = []
                    if plur_desc is not None:
                        toks.append(plur_desc)
                    if case_desc is not None:
                        toks.append(case_desc)
                    desc = ' '.join(toks)
            descs.append(desc)
        return descs

    def compute_labels(self):
        if self.__ner_tagger is None:
            self.__ner_tagger = load_default_ner_tagger()
        self.__ner_tagger.tag_document(self)
        self.__computed.add(LABEL)
        return self

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
        return self

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
        return self

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
        """Fix spellin of the text.

        NB! Invalidates computed properties, which have to be recomputed in order to use.
        If accessing data using properties, they will be updated automatically, but
        direct use of the underlying dictionary will yield wrong results.
        """
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
        return self

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

    def __split_given_spans(self, spans):
        text = self.text
        N = len(spans)
        results = [{TEXT: text[start:end]} for start, end in spans]
        for elem in self:
            if isinstance(self[elem], list):
                splits = self.__divide_to_spans(spans, self[elem])
                for idx in range(N):
                    results[idx][elem] = splits[idx]
        return [Text(res) for res in results]

    def split_by(self, element):
        """Split the text into multiple instances by the given element.

        Parameters
        ----------
        element: str
            String determining the element, such as "sentences" or "words"

        Returns
        -------
        list of Text
        """
        if not self.is_computed(element):
            self.compute(element)
        return self.__split_given_spans(self.__spans(element))

    def split_by_sentences(self):
        return self.split_by(SENTENCES)

    def split_by_words(self):
        return self.split_by(WORDS)

    def split_by_regex(self, regex_or_pattern, flags=re.U, gaps=True):
        """Split the text into multiple instances using a regex.

        Parameters
        ----------
        regex_or_pattern: str or compiled pattern
            The regular expression to use for splitting.

        Keyword parameters
        ------------------
        flags: int (default: re.U)
            The regular expression flags (only used, when user has not supplied compiled regex).
        gaps: boolean (default: True)
            If True, then regions matched by the regex are not included in the resulting Text instances, which
            is expected behaviour.
            If False, then only regions matched by the regex are included in the result.

        Returns
        -------
        list of Text
            The Text instances obtained by splitting.
        """

        text = self[TEXT]
        regex = regex_or_pattern
        if isinstance(regex, six.string_types):
            regex = re.compile(regex_or_pattern, flags=flags)
        # else is assumed pattern
        last_end = 0
        spans = []
        if gaps: # compute cap spans
            for mo in regex.finditer(text):
                start, end = mo.start(), mo.end()
                if start > last_end:
                    spans.append((last_end, start))
                last_end = end
            if last_end < len(text):
                spans.append((last_end, len(text)))
        else: # use matched regions
            spans = [(mo.start(), mo.end()) for mo in regex.finditer(text)]
        return self.__split_given_spans(spans)


    # ///////////////////////////////////////////////////////////////////
    # FILTERING
    # ///////////////////////////////////////////////////////////////////

    def get_elements_in_span(self, element, span):
        items = []
        if element in self:
            for item in self[element]:
                if item[START] >= span[0] and item[END] <= span[1]:
                    items.append(item)
        return items


    # ///////////////////////////////////////////////////////////////////
    # AGGREGATE GETTER
    # ///////////////////////////////////////////////////////////////////

    @property
    def get(self):
        return ZipBuilder(self)


class ZipBuilder(object):
    """Helper class to aggregate various :py:class:`~estnltk.text.Text` properties in a simple way.
    Uses builder pattern.

    Example::

        text = Text('Alles see oli, kui käisin koolis')
        text.get.word_texts.lemmas.postags.as_dataframe

    test.get - this initiates a new :py:class:`~estnltk.text.ZipBuilder` instance on the Text object.

    .word_texts - adds word texts
    .postags - adds postags

    .as_dataframe - builds the final object and returns a dataframe
    """

    def __init__(self, text):
        self.__text = text
        self.__keys = []
        self.__values = []

    def __getattribute__(self, item):
        if not item.startswith('__') and item not in dir(self):
            self.__keys.append(item)
            self.__values.append(object.__getattribute__(self.__text, item))
            return self
        return object.__getattribute__(self, item)

    @property
    def as_dataframe(self):
        df = pandas.DataFrame.from_dict(self.as_dict)
        return df[self.__keys]

    @property
    def as_zip(self):
        return zip(*self.__values)

    @property
    def as_list(self):
        return self.__values

    @property
    def as_dict(self):
        return dict(zip(self.__keys, self.__values))




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
    text = Text('Esimene lause. Teine lause. Kolmas lause. See on neljas.')
    text.compute_sentences()
    text.compute_words()
    from pprint import pprint
    pprint (dict(text))
