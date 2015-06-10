# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .core import as_unicode, POSTAG_DESCRIPTIONS, CASES, PLURALITY, VERB_TYPES
from .core import VERB_CHAIN_RES_PATH
from .names import *
from .dividing import divide, divide_by_spans
from .vabamorf import morf as vabamorf
from .ner import NerTagger
from .timex import TimexTagger
from .wordnet_tagger import WordnetTagger
from .clausesegmenter import ClauseSegmenter
from .mw_verbs.verbchain_detector import VerbChainDetector
from .textcleaner import ESTONIAN, TextCleaner

import six
import pandas
import nltk.data
import regex as re
from nltk.tokenize.regexp import WordPunctTokenizer, RegexpTokenizer

from cached_property import cached_property
import json
from copy import deepcopy
from collections import defaultdict
from pprint import pprint
import codecs


# default functionality
paragraph_tokenizer = RegexpTokenizer('\n\n', gaps=True, discard_empty=True)
sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
word_tokenizer = WordPunctTokenizer()
nertagger = None
timextagger = None
textcleaner = TextCleaner()
clausesegmenter = None
verbchain_detector = None
wordnet_tagger = None


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


def load_default_clausesegmenter():
    global clausesegmenter
    if clausesegmenter is None:
        clausesegmenter = ClauseSegmenter()
    return clausesegmenter


def load_default_verbchain_detector():
    global verbchain_detector
    if verbchain_detector is None:
        verbchain_detector = VerbChainDetector(resourcesPath=VERB_CHAIN_RES_PATH)
    return verbchain_detector


class Text(dict):
    """Text class.

    """

    def __init__(self, text_or_instance, **kwargs):
        """Initialize an Text object.

        Keyword parameters
        ------------------
        sentence_tokenizer: nltk.Tokenizer
        word_tokenizer: nltk.Tokenizer
        ner_tagger: NerTagger
        timex_tagger: TimexTagger
        clause_segmenter: ClauseSegmenter
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
        self.__paragraph_tokenizer = kwargs.get(
            'paragraph_tokenizer', paragraph_tokenizer)
        self.__sentence_tokenizer = kwargs.get(
            'sentence_tokenizer', sentence_tokenizer)
        self.__word_tokenizer = kwargs.get(
            'word_tokenizer', word_tokenizer)
        self.__ner_tagger = kwargs.get( # ner models take time to load, load only when needed
            'ner_tagger', None)
        self.__timex_tagger = kwargs.get( # lazy loading for timex tagger
            'timex_tagger', None)
        self.__clause_segmenter = kwargs.get(
            'clause_segmenter', None)
        self.__verbchain_detector = kwargs.get(
            'verbchain_detector', None # lazy loading
        )
        self.__wordnet_tagger = kwargs.get(
            'wordnet_tagger', None # lazy loading
        )
        self.__text_cleaner = kwargs.get('text_cleaner', textcleaner)

    def get_kwargs(self):
        """Get the keyword arguments that were passed to the :py:class:`~estnltk.text.Text` when it was constructed."""
        return self.__kwargs

    def __find_what_is_computed(self):
        """Find out what kind of information is already computed. It uses keys such as "elements", "sentences" etc
           to *guess* what is computed and what is not.
           It does not perform extensive checks to see if the values of these keys are actually valid.
        """
        computed = set()
        if PARAGRAPHS in self:
            computed.add(PARAGRAPHS)
        if SENTENCES in self:
            computed.add(SENTENCES)
        if WORDS in self:
            computed.add(WORDS)
            if len(self[WORDS]) > 0:
                if ANALYSIS in self[WORDS][0]:
                    computed.add(ANALYSIS)
                    if len(self[WORDS][0][ANALYSIS]) and WORDNET in self[WORDS][0][ANALYSIS][0]:
                        computed.add(WORDNET)
                if LABEL in self:
                    computed.add(LABEL)
        if NAMED_ENTITIES in self:
            computed.add(NAMED_ENTITIES)
        if CLAUSES in self:
            computed.add(CLAUSES)
        self.__computed = computed
        return computed

    def is_computed(self, element):
        """Is the given element computed?"""
        return element in self.__computed

    def __texts(self, element, sep=' '):
        """Retrieve texts for given element.

        Parameters
        ----------

        sep: str
            Separator for elements that span more than one region.

        Returns
        -------
        list of str
            List of strings that make up given elements.
        """
        return self.__texts_from_spans(self.__spans(element), sep)

    def __texts_from_spans(self, spans, sep=' '):
        text = self.text
        texts = []
        for start, end in spans:
            if isinstance(start, list):
                texts.append(sep.join(text[s:e] for s, e in zip(start, end)))
            else:
                texts.append(text[start:end])
        return texts

    def __spans(self, element):
        """Retrieve (start, end) tuples denoting the spans of given elements.

        Returns
        -------
        list of (int, int)
            List of (start, end) tuples.
        """
        spans = []
        for data in self[element]:
            spans.append((data[START], data[END]))
        return spans

    def __starts(self, element):
        starts = []
        for data in self[element]:
            starts.append(data[START])
        return starts

    def __ends(self, element):
        ends = []
        for data in self[element]:
            ends.append(data[END])
        return ends

    def __str__(self):
        return self[TEXT]

    def __unicode__(self):
        return self[TEXT]

    # ///////////////////////////////////////////////////////////////////
    # STRING METHODS
    # ///////////////////////////////////////////////////////////////////

    def capitalize(self):
        return Text(self[TEXT].capitalize(), **self.__kwargs)

    def count(self, sub, *args):
        return self[TEXT].count(sub, *args)

    def endswith(self, suffix, *args):
        return self[TEXT].endswith(suffix, *args)

    def find(self, sub, *args):
        return self[TEXT].find(sub, *args)

    def index(self, sub, *args):
        return self[TEXT].index(sub, *args)

    def isalnum(self):
        return self[TEXT].isalnum()

    def isalpha(self):
        return self[TEXT].isalpha()

    def isdigit(self):
        return self[TEXT].isdigit()

    def islower(self):
        return self[TEXT].islower()

    def isspace(self):
        return self[TEXT].isspace()

    def istitle(self):
        return self[TEXT].istitle()

    def isupper(self):
        return self[TEXT].isupper()

    def lower(self):
        return Text(self[TEXT].lower(), **self.__kwargs)

    def lstrip(self, *args):
        return Text(self[TEXT].lstrip(*args), **self.__kwargs)

    def replace(self, old, new, *args):
        return Text(self[TEXT].replace(old, new, *args), **self.__kwargs)

    def rfind(self, sub, *args):
        return self[TEXT].rfind(sub, *args)

    def rindex(self, sub, *args):
        return self[TEXT].rindex(sub, *args)

    def rstrip(self, *args):
        return Text(self[TEXT].rstrip(*args), **self.__kwargs)

    def startswith(self, prefix, *args):
        return self[TEXT].startswith(prefix, *args)

    def strip(self, *args):
        return Text(self[TEXT].strip(*args), **self.__kwargs)


    # ///////////////////////////////////////////////////////////////////
    # RETRIEVING AND COMPUTING PROPERTIES
    # ///////////////////////////////////////////////////////////////////

    @cached_property
    def text(self):
        return self[TEXT]

    @cached_property
    def compute_mapping(self):
        return {
            PARAGRAPHS: self.compute_paragraphs,
            SENTENCES: self.compute_sentences,
            WORDS: self.compute_words,
            ANALYSIS: self.compute_analysis,
            TIMEXES: self.compute_timexes,
            NAMED_ENTITIES: self.compute_named_entities,
            CLAUSE_ANNOTATION: self.compute_clause_annotations,
            CLAUSES: self.compute_clauses,
            WORDNET: self.compute_wordnet
        }

    def compute(self, element):
        self.compute_mapping[element]()
        return self

    def compute_paragraphs(self):
        tok = self.__paragraph_tokenizer
        spans = tok.span_tokenize(self.text)
        dicts = []
        for start, end in spans:
            dicts.append({'start': start, 'end': end})
        self[PARAGRAPHS] = dicts
        self.__computed.add(PARAGRAPHS)
        return self

    @cached_property
    def paragraphs(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        return self[PARAGRAPHS]

    @cached_property
    def paragraph_texts(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        return self.__texts(PARAGRAPHS)

    @cached_property
    def paragraph_spans(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        return self.__spans(PARAGRAPHS)

    @cached_property
    def paragraph_starts(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        return self.__starts(PARAGRAPHS)

    @cached_property
    def paragraph_ends(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        return self.__ends(PARAGRAPHS)

    def compute_sentences(self):
        if not self.is_computed(PARAGRAPHS):
            self.compute_paragraphs()
        tok = self.__sentence_tokenizer
        text = self.text
        dicts = []
        for paragraph in self[PARAGRAPHS]:
            para_start, para_end = paragraph[START], paragraph[END]
            para_text = text[para_start:para_end]
            spans = tok.span_tokenize(para_text)
            for start, end in spans:
                dicts.append({'start': start+para_start, 'end': end+para_start})
        self[SENTENCES] = dicts
        self.__computed.add(SENTENCES)
        return self

    @cached_property
    def sentences(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self[SENTENCES]

    @cached_property
    def sentence_texts(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__texts(SENTENCES)

    @cached_property
    def sentence_spans(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__spans(SENTENCES)

    @cached_property
    def sentence_starts(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__starts(SENTENCES)

    @cached_property
    def sentence_ends(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        return self.__ends(SENTENCES)

    def compute_words(self):
        if not self.is_computed(SENTENCES):
            self.compute_sentences()
        tok = self.__word_tokenizer
        text = self.text
        dicts = []
        for sentence in self[SENTENCES]:
            sent_start, sent_end = sentence[START], sentence[END]
            sent_text = text[sent_start:sent_end]
            spans = tok.span_tokenize(sent_text)
            for start, end in spans:
                dicts.append({START: start+sent_start, END: end+sent_start, TEXT: sent_text[start:end]})
        self[WORDS] = dicts
        self.__computed.add(WORDS)
        return self

    def compute_analysis(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        sentences = self.divide(WORDS, SENTENCES)
        for sentence in sentences:
            texts = [word[TEXT] for word in sentence]
            all_analysis = vabamorf.analyze(texts, **self.__kwargs)
            for word, analysis in zip(sentence, all_analysis):
                word[ANALYSIS] = analysis[ANALYSIS]
                word[TEXT] = analysis[TEXT]
        self.__computed.add(ANALYSIS)
        return self

    @cached_property
    def words(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self[WORDS]

    @cached_property
    def word_texts(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return [word[TEXT] for word in self[WORDS]]

    @cached_property
    def word_spans(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self.__spans(WORDS)

    @cached_property
    def word_starts(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self.__starts(WORDS)

    @cached_property
    def word_ends(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return self.__ends(WORDS)

    @cached_property
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

    @cached_property
    def roots(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ROOT)

    @cached_property
    def lemmas(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(LEMMA)

    @cached_property
    def endings(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ENDING)

    @cached_property
    def forms(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(FORM)

    @cached_property
    def postags(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(POSTAG)

    @cached_property
    def postag_descriptions(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return [POSTAG_DESCRIPTIONS.get(tag, '') for tag in self.__get_analysis_element(POSTAG)]

    @cached_property
    def root_tokens(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        return self.__get_analysis_element(ROOT_TOKENS)

    @cached_property
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
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        if self.__ner_tagger is None:
            self.__ner_tagger = load_default_ner_tagger()
        self.__ner_tagger.tag_document(self)
        self.__computed.add(LABEL)
        return self

    @cached_property
    def labels(self):
        if not self.is_computed(LABEL):
            self.compute_labels()
        return [word[LABEL] for word in self.words]

    def compute_named_entities(self):
        if self.is_computed(ANALYSIS):
            self.compute_labels()
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

    @cached_property
    def named_entities(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        phrases = self.split_by(NAMED_ENTITIES)
        return [' '.join(phrase.lemmas) for phrase in phrases]

    @cached_property
    def named_entity_texts(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return self.__texts(NAMED_ENTITIES)

    @cached_property
    def named_entity_spans(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return self.__spans(NAMED_ENTITIES)

    @cached_property
    def named_entity_labels(self):
        if not self.is_computed(NAMED_ENTITIES):
            self.compute_named_entities()
        return [ne[LABEL] for ne in self[NAMED_ENTITIES]]

    def compute_timexes(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        if not self.is_computed(TIMEXES):
            if self.__timex_tagger is None:
                self.__timex_tagger = load_default_timex_tagger()
            self.__timex_tagger.tag_document(self, **self.__kwargs)
            self.__computed.add(TIMEXES)
        return self

    @cached_property
    def timexes(self):
        if not self.is_computed(TIMEXES):
            self.compute_timexes()
        return self[TIMEXES]

    @cached_property
    def timex_texts(self):
        return [timex[TEXT] for timex in self.timexes]

    @cached_property
    def timex_values(self):
        return [timex[TMX_VALUE] for timex in self.timexes]

    @cached_property
    def timex_types(self):
        return [timex[TMX_TYPE] for timex in self.timexes]

    @cached_property
    def timex_ids(self):
        return [timex[TMX_ID] for timex in self.timexes]

    @cached_property
    def timex_starts(self):
        if not self.is_computed(TIMEXES):
            self.compute_timexes()
        return self.__starts(TIMEXES)

    @cached_property
    def timex_ends(self):
        if not self.is_computed(TIMEXES):
            self.compute_timexes()
        return self.__ends(TIMEXES)

    @cached_property
    def timex_spans(self):
        if not self.is_computed(TIMEXES):
            self.compute_timexes()
        return self.__spans(TIMEXES)

    def compute_clause_annotations(self):
        if not self.is_computed(ANALYSIS):
            self.compute_analysis()
        if self.__clause_segmenter is None:
            self.__clause_segmenter = load_default_clausesegmenter()
        self.__computed.add(CLAUSE_ANNOTATION)
        return self.__clause_segmenter.tag(self)

    @cached_property
    def clause_annotations(self):
        if not self.is_computed(CLAUSE_ANNOTATION):
            self.compute_clause_annotations()
        return [word.get(CLAUSE_ANNOTATION, None) for word in self[WORDS]]

    @cached_property
    def clause_indices(self):
        if not self.is_computed(CLAUSE_ANNOTATION):
            self.compute_clause_annotations()
        return [word.get(CLAUSE_IDX, None) for word in self[WORDS]]

    def compute_clauses(self):
        if not self.is_computed(CLAUSE_ANNOTATION):
            self.compute_clause_annotations()

        def from_sentence(words):
            """Function that extracts clauses from a signle sentence."""
            clauses = defaultdict(list)
            start = words[0][START]
            end = words[0][END]
            clause = words[0][CLAUSE_IDX]
            for word in words:
                if word[CLAUSE_IDX] != clause:
                    clauses[clause].append((start, end))
                    start, clause = word[START], word[CLAUSE_IDX]
                end = word[END]
            clauses[clause].append((start, words[-1][END]))
            clauses = [(key, {START: [s for s, e in clause], END: [e for s, e in clause]}) for key, clause in clauses.items()]
            return [v for k, v in sorted(clauses)]

        clauses = []
        sentences = self.divide()
        for sentence in sentences:
            clauses.extend(from_sentence(sentence))

        self[CLAUSES] = clauses
        self.__computed.add(CLAUSES)
        return self

    @cached_property
    def clauses(self):
        if not self.is_computed(CLAUSES):
            self.compute_clauses()
        return self[CLAUSES]

    @cached_property
    def clause_texts(self):
        if not self.is_computed(CLAUSES):
            self.compute_clauses()
        return self.__texts(CLAUSES)

    def compute_verb_chains(self):
        if not self.is_computed(CLAUSES):
            self.compute_clauses()
        if self.__verbchain_detector is None:
            self.__verbchain_detector = load_default_verbchain_detector()
        sentences = self.divide()
        verbchains = []
        for sentence in sentences:
            chains = self.__verbchain_detector.detectVerbChainsFromSent(sentence)
            offset = 0
            for chain in chains:
                chain[PHRASE] = [idx+offset for idx in chain[PHRASE]]
                chain[START] = self[WORDS][chain[PHRASE][0]][START]
                chain[END] = self[WORDS][chain[PHRASE][-1]][END]
            offset += len(sentence)
            verbchains.extend(chains)
        self[VERB_CHAINS] = verbchains
        self.__computed.add(VERB_CHAINS)
        return self

    @cached_property
    def verb_chains(self):
        if not self.is_computed(VERB_CHAINS):
            self.compute_verb_chains()
        return self[VERB_CHAINS]

    @cached_property
    def verb_chain_texts(self):
        if not self.is_computed(VERB_CHAINS):
            self.compute_verb_chains()
        return self.__texts(VERB_CHAINS)

    @cached_property
    def verb_chain_patterns(self):
        return [vc[PATTERN] for vc in self.verb_chains]

    @cached_property
    def verb_chain_roots(self):
        return [vc[ROOTS] for vc in self.verb_chains]

    @cached_property
    def verb_chain_morphs(self):
        return [vc[MORPH] for vc in self.verb_chains]

    @cached_property
    def verb_chain_polarities(self):
        return [vc[POLARITY] for vc in self.verb_chains]

    @cached_property
    def verb_chain_tenses(self):
        return [vc[TENSE] for vc in self.verb_chains]

    @cached_property
    def verb_chain_moods(self):
        return [vc[MOOD] for vc in self.verb_chains]

    @cached_property
    def verb_chain_voices(self):
        return [vc[VOICE] for vc in self.verb_chains]

    @cached_property
    def verb_chain_clause_indices(self):
        return [vc[CLAUSE_IDX] for vc in self.verb_chains]

    @cached_property
    def verb_chain_starts(self):
        if not self.is_computed(VERB_CHAINS):
            self.compute_verb_chains()
        return self.__starts(VERB_CHAINS)

    @cached_property
    def verb_chain_ends(self):
        if not self.is_computed(VERB_CHAINS):
            self.compute_verb_chains()
        return self.__ends(VERB_CHAINS)

    @cached_property
    def verb_chain_other_verbs(self):
        return [vc[OTHER_VERBS] for vc in self.verb_chains]

    def compute_wordnet(self, **kwargs):
        global wordnet_tagger
        if wordnet_tagger is None: # cached wn tagger
            wordnet_tagger = WordnetTagger()
        self.__wordnet_tagger = wordnet_tagger
        self.__computed.add(WORDNET)
        if len(kwargs) > 0:
            return self.__wordnet_tagger.tag_text(self, **kwargs)
        return self.__wordnet_tagger.tag_text(self, **self.__kwargs)

    @cached_property
    def wordnet_annotations(self):
        if not self.is_computed(WORDNET):
            self.compute_wordnet()
        return [[a[WORDNET] for a in analysis] for analysis in self.analysis]

    @cached_property
    def synsets(self):
        synsets = []
        for wn_annots in self.wordnet_annotations:
            word_synsets = []
            for wn_annot in wn_annots:
                for synset in wn_annot.get(SYNSETS, []):
                    word_synsets.append(deepcopy(synset))
            synsets.append(word_synsets)
        return synsets

    @cached_property
    def word_literals(self):
        literals = []
        for word_synsets in self.synsets:
            word_literals = set()
            for synset in word_synsets:
                for variant in synset.get(SYN_VARIANTS):
                    if LITERAL in variant:
                        word_literals.add(variant[LITERAL])
            literals.append(list(sorted(word_literals)))
        return literals

    # ///////////////////////////////////////////////////////////////////
    # SPELLCHECK
    # ///////////////////////////////////////////////////////////////////

    @cached_property
    def spelling(self):
        """Flag incorrectly spelled words.
        Returns a list of booleans, where element at each position denotes, if the word at the same position
        is spelled correctly.
        """
        if not self.is_computed(WORDS):
            self.compute_words()
        return [data[SPELLING] for data in vabamorf.spellcheck(self.word_texts, suggestions=False)]

    @cached_property
    def spelling_suggestions(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return [data[SUGGESTIONS] for data in vabamorf.spellcheck(self.word_texts, suggestions=True)]

    @cached_property
    def spellcheck_results(self):
        if not self.is_computed(WORDS):
            self.compute_words()
        return vabamorf.spellcheck(self.word_texts, suggestions=True)

    def fix_spelling(self):
        """Fix spelling of the text.
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
            return Text(''.join(newtoks), **self.__kwargs)
        return self

    # ///////////////////////////////////////////////////////////////////
    # TEXTCLEANER
    # ///////////////////////////////////////////////////////////////////

    def is_valid(self):
        return self.__text_cleaner.is_valid(self[TEXT])

    @cached_property
    def invalid_characters(self):
        return self.__text_cleaner.invalid_characters(self[TEXT])

    def clean(self):
        return Text(self.__text_cleaner.clean(self[TEXT]), **self.__kwargs)

    # ///////////////////////////////////////////////////////////////////
    # SPLITTING
    # ///////////////////////////////////////////////////////////////////

    def __split_given_spans(self, spans, sep=' '):
        N = len(spans)
        results = [{TEXT: text} for text in self.__texts_from_spans(spans, sep=sep)]
        for elem in self:
            if isinstance(self[elem], list):
                splits = divide_by_spans(self[elem], spans, translate=True, sep=sep)
                for idx in range(N):
                    results[idx][elem] = splits[idx]
        return [Text(res) for res in results]

    def split_by(self, element, sep=' '):
        """Split the text into multiple instances by the given element.

        Parameters
        ----------
        element: str
            String determining the element, such as "sentences" or "words"
        sep: str (default: ' ')
            The separator to use to join texts of multi layer elements.

        Returns
        -------
        list of Text
        """
        if not self.is_computed(element):
            self.compute(element)
        return self.__split_given_spans(self.__spans(element), sep=sep)

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
    # DIVIDING
    # ///////////////////////////////////////////////////////////////////

    def divide(self, element=WORDS, by=SENTENCES):
        """Divide the Text into pieces by keeping references to original elements, when possible.
        This is not possible only, if the _element_ is a multispan.

        Parameters
        ----------

        element: str
            The element to collect and distribute in resulting bins.
        by: str
            Each resulting bin is defined by spans of this element.

        Returns
        -------
        list of (list of dict)
        """
        if not self.is_computed(element):
            self.compute(element)
        if not self.is_computed(by):
            self.compute(by)
        return divide(self[element], self[by])

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

    def __call__(self, props):
        for prop in props:
            self.__getattribute__(prop)
        return self

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

