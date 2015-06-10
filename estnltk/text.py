# -*- coding: utf-8 -*-
"""
Text module contains central functionality of Estnltk.
It sets up standard functionality for tokenziation and tagging and hooks it up with
:py:class:`~estnltk.text.Text` class.

"""
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
from .textcleaner import TextCleaner

import six
import pandas
import nltk.data
import regex as re
from nltk.tokenize.regexp import WordPunctTokenizer, RegexpTokenizer

from cached_property import cached_property
from copy import deepcopy
from collections import defaultdict
from pprint import pprint


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
    """Central class of Estnltk that is the main interface of performing
    all NLP operations.
    """

    def __init__(self, text_or_instance, **kwargs):
        """Initialize a new text instance.

        Parameters
        ----------
        text_or_instance: dict, Text, str, unicode
            If ``str`` or ``unicode``, creates a new Text object.
            If ``Text`` or ``dict``, acts essentially as a copy constructor.
            However, it does not create a deep copy.
        paragraph_tokenizer: nltk.tokenize.api.StringTokenizer
            Tokenizer for paragraphs.
        sentence_tokenizer: nltk.tokenize.api.StringTokenizer
            Tokenizer for sentences.
        word_tokenizer: nltk.tokenize.api.StringTokenizer
            Tokenizer for words.
        ner_tagger: estnltk.ner.NerTagger
            Tagger for annotating named entities.
        timex_tagger: estnltk.timex.TimexTagger
            Tagger for temporal expressions.
        creation_date: datetime.datetime
            The date the document was created. Relevant for temporal expressions tagging.
        clause_segmenter: estnltk.clausesegmenter.ClauseSegmenter
            Class for detecting clauses.
        verbchain_detector: estnltk.mw_verbs.verbchain_detector.VerbChainDetector
            Verb chain tagger.
        wordnet_tagger: estnltk.wordnet_tagger.WordnetTagger
            Tagger for synsets and relations.
        text_cleaner: estnltk.textcleaner.TextCleaner
            TextCleaner class.
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
        self.__find_what_is_tagged()

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

    def __find_what_is_tagged(self):
        """Find out what kind of information is already tagged.

        It uses existing layers to decide what information is present.
        Note that this is not bullet-proof and in certain situations the user should call
        tokenize_X, tag_X methods manually.
        It does not perform extensive checks to see if the values of these keys are actually valid.
        """
        tagged = set()
        if PARAGRAPHS in self:
            tagged.add(PARAGRAPHS)
        if SENTENCES in self:
            tagged.add(SENTENCES)
        if WORDS in self:
            tagged.add(WORDS)
            if len(self[WORDS]) > 0:
                if ANALYSIS in self[WORDS][0]:
                    tagged.add(ANALYSIS)
                    if len(self[WORDS][0][ANALYSIS]) and WORDNET in self[WORDS][0][ANALYSIS][0]:
                        tagged.add(WORDNET)
                if LABEL in self:
                    tagged.add(LABEL)
        if NAMED_ENTITIES in self:
            tagged.add(NAMED_ENTITIES)
        if CLAUSES in self:
            tagged.add(CLAUSES)
        self.__tagged = tagged
        return tagged

    def is_tagged(self, layer):
        """Is the given element tokenized/tagged?"""
        return layer in self.__tagged

    def texts(self, layer, sep=' '):
        """Retrieve texts for given layer.

        Parameters
        ----------

        sep: str
            Separator for multilayer elements (default: ' ').

        Returns
        -------
        list of str
            List of strings that make up given layer.
        """
        return self.texts_from_spans(self.spans(layer), sep)

    def texts_from_spans(self, spans, sep=' '):
        """Retrieve texts from a list of (start, end) position spans.

        Parameters
        ----------

        sep: str
            Separator for multilayer elements (default: ' ').

        Returns
        -------
        list of str
            List of strings that correspond to given spans.
        """
        text = self.text
        texts = []
        for start, end in spans:
            if isinstance(start, list):
                texts.append(sep.join(text[s:e] for s, e in zip(start, end)))
            else:
                texts.append(text[start:end])
        return texts

    def spans(self, layer):
        """Retrieve (start, end) tuples denoting the spans of given layer elements.

        Returns
        -------
        list of (int, int)
            List of (start, end) tuples.
        """
        spans = []
        for data in self[layer]:
            spans.append((data[START], data[END]))
        return spans

    def starts(self, layer):
        """Retrieve start positions of elements if given layer."""
        starts = []
        for data in self[layer]:
            starts.append(data[START])
        return starts

    def ends(self, layer):
        """Retrieve end positions of elements if given layer."""
        ends = []
        for data in self[layer]:
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
        """The raw underlying text that was used to initialize the Text instance."""
        return self[TEXT]

    @cached_property
    def layer_tagger_mapping(self):
        """Dictionary that maps layer names to taggers that can create that layer."""
        return {
            PARAGRAPHS: self.tokenize_paragraphs,
            SENTENCES: self.tokenize_sentences,
            WORDS: self.tokenize_words,
            ANALYSIS: self.tag_analysis,
            TIMEXES: self.tag_timexes,
            NAMED_ENTITIES: self.tag_named_entities,
            CLAUSE_ANNOTATION: self.tag_clause_annotations,
            CLAUSES: self.tag_clauses,
            WORDNET: self.tag_wordnet
        }

    def tag(self, layer):
        """Tag the annotations of given layer. It can automatically tag any built-in layer type."""
        mapping = self.layer_tagger_mapping
        if layer in mapping:
            mapping[layer]()
        return self

    def tokenize_paragraphs(self):
        """Apply paragraph tokenization to this Text instance. Creates ``paragraphs`` layer."""
        tok = self.__paragraph_tokenizer
        spans = tok.span_tokenize(self.text)
        dicts = []
        for start, end in spans:
            dicts.append({'start': start, 'end': end})
        self[PARAGRAPHS] = dicts
        self.__tagged.add(PARAGRAPHS)
        return self

    @cached_property
    def paragraphs(self):
        """Return the list of ``paragraphs`` layer elements."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        return self[PARAGRAPHS]

    @cached_property
    def paragraph_texts(self):
        """The list of texts representing ``paragraphs`` layer elements."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        return self.texts(PARAGRAPHS)

    @cached_property
    def paragraph_spans(self):
        """The list of spans representing ``paragraphs`` layer elements."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        return self.spans(PARAGRAPHS)

    @cached_property
    def paragraph_starts(self):
        """The start positions of ``paragraphs`` layer elements."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        return self.starts(PARAGRAPHS)

    @cached_property
    def paragraph_ends(self):
        """The end positions of ``paragraphs`` layer elements."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        return self.ends(PARAGRAPHS)

    def tokenize_sentences(self):
        """Apply sentence tokenization to this Text instance. Creates ``sentences`` layer.
        Automatically tokenizes paragraphs, if they are not already tokenized."""
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
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
        self.__tagged.add(SENTENCES)
        return self

    @cached_property
    def sentences(self):
        """The list of ``sentences`` layer elements."""
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
        return self[SENTENCES]

    @cached_property
    def sentence_texts(self):
        """The list of texts representing ``sentences`` layer elements."""
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
        return self.texts(SENTENCES)

    @cached_property
    def sentence_spans(self):
        """The list of spans representing ``sentences`` layer elements."""
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
        return self.spans(SENTENCES)

    @cached_property
    def sentence_starts(self):
        """The list of start positions representing ``sentences`` layer elements."""
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
        return self.starts(SENTENCES)

    @cached_property
    def sentence_ends(self):
        """The list of end positions representing ``sentences`` layer elements."""
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
        return self.ends(SENTENCES)

    def tokenize_words(self):
        """Apply word tokenization and create ``words`` layer.

        Automatically creates ``paragraphs`` and ``sentences`` layers.
        """
        if not self.is_tagged(SENTENCES):
            self.tokenize_sentences()
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
        self.__tagged.add(WORDS)
        return self

    def tag_analysis(self):
        """Tag ``words`` layer with morphological analysis attributes."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        sentences = self.divide(WORDS, SENTENCES)
        for sentence in sentences:
            texts = [word[TEXT] for word in sentence]
            all_analysis = vabamorf.analyze(texts, **self.__kwargs)
            for word, analysis in zip(sentence, all_analysis):
                word[ANALYSIS] = analysis[ANALYSIS]
                word[TEXT] = analysis[TEXT]
        self.__tagged.add(ANALYSIS)
        return self

    @cached_property
    def words(self):
        """The list of word elements in ``words`` layer."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return self[WORDS]

    @cached_property
    def word_texts(self):
        """The list of words representing ``words`` layer elements."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return [word[TEXT] for word in self[WORDS]]

    @cached_property
    def word_spans(self):
        """The list of spans representing ``words`` layer elements."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return self.spans(WORDS)

    @cached_property
    def word_starts(self):
        """The list of start positions representing ``words`` layer elements."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return self.starts(WORDS)

    @cached_property
    def word_ends(self):
        """The list of end positions representing ``words`` layer elements."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return self.ends(WORDS)

    @cached_property
    def analysis(self):
        """The list of analysis of ``words`` layer elements."""
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return [word[ANALYSIS] for word in self.words]

    def __get_key(self, dicts, element, sep):
        matches = []
        for dict in dicts:
            if element in dict:
                matches.append(dict[element])
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            if element == ROOT_TOKENS:
                return matches
            return sep.join(sorted(set(matches)))

    def get_analysis_element(self, element, sep='|'):
        """The list of analysis elements of ``words`` layer.

        Parameters
        ----------
        element: str
            The name of the element, for example "lemma", "postag".
        sep: str
            The separator for ambiguous analysis (default: "|").
            As morphological analysis cannot always yield unambiguous results, we
            return ambiguous values separated by the pipe character as default.
        """
        return [self.__get_key(word[ANALYSIS], element, sep) for word in self.words]

    @cached_property
    def roots(self):
        """The list of word roots.

        Ambiguous cases are separated with pipe character by default.
        Use :py:meth:`~estnltk.text.Text.get_analysis_element` to specify custom separator for ambiguous entries.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(ROOT)

    @cached_property
    def lemmas(self):
        """The list of lemmas.

        Ambiguous cases are separated with pipe character by default.
        Use :py:meth:`~estnltk.text.Text.get_analysis_element` to specify custom separator for ambiguous entries.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(LEMMA)

    @cached_property
    def endings(self):
        """The list of word endings.

        Ambiguous cases are separated with pipe character by default.
        Use :py:meth:`~estnltk.text.Text.get_analysis_element` to specify custom separator for ambiguous entries.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(ENDING)

    @cached_property
    def forms(self):
        """Tthe list of word forms.

        Ambiguous cases are separated with pipe character by default.
        Use :py:meth:`~estnltk.text.Text.get_analysis_element` to specify custom separator for ambiguous entries.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(FORM)

    @cached_property
    def postags(self):
        """The list of word part-of-speech tags.

        Ambiguous cases are separated with pipe character by default.
        Use :py:meth:`~estnltk.text.Text.get_analysis_element` to specify custom separator for ambiguous entries.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(POSTAG)

    @cached_property
    def postag_descriptions(self):
        """Human-readable POS-tag descriptions."""
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return [POSTAG_DESCRIPTIONS.get(tag, '') for tag in self.get_analysis_element(POSTAG)]

    @cached_property
    def root_tokens(self):
        """Root tokens of word roots."""
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return self.get_analysis_element(ROOT_TOKENS)

    @cached_property
    def descriptions(self):
        """Human readable word descriptions."""
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

    def tag_labels(self):
        """Tag named entity labels in the ``words`` layer."""
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        if self.__ner_tagger is None:
            self.__ner_tagger = load_default_ner_tagger()
        self.__ner_tagger.tag_document(self)
        self.__tagged.add(LABEL)
        return self

    @cached_property
    def labels(self):
        """Named entity labels."""
        if not self.is_tagged(LABEL):
            self.tag_labels()
        return [word[LABEL] for word in self.words]

    def tag_named_entities(self):
        """Tag ``named_entities`` layer.

        This automatically performs morphological analysis along with all dependencies.
        """
        if self.is_tagged(ANALYSIS):
            self.tag_labels()
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
        self.__tagged.add(NAMED_ENTITIES)
        return self

    @cached_property
    def named_entities(self):
        """The elements of ``named_entities`` layer."""
        if not self.is_tagged(NAMED_ENTITIES):
            self.tag_named_entities()
        phrases = self.split_by(NAMED_ENTITIES)
        return [' '.join(phrase.lemmas) for phrase in phrases]

    @cached_property
    def named_entity_texts(self):
        """The texts representing named entities."""
        if not self.is_tagged(NAMED_ENTITIES):
            self.tag_named_entities()
        return self.texts(NAMED_ENTITIES)

    @cached_property
    def named_entity_spans(self):
        """The spans of named entities."""
        if not self.is_tagged(NAMED_ENTITIES):
            self.tag_named_entities()
        return self.spans(NAMED_ENTITIES)

    @cached_property
    def named_entity_labels(self):
        """The named entity labels without BIO prefixes."""
        if not self.is_tagged(NAMED_ENTITIES):
            self.tag_named_entities()
        return [ne[LABEL] for ne in self[NAMED_ENTITIES]]

    def tag_timexes(self):
        """Create ``timexes`` layer.
        Depends on morphological analysis data in ``words`` layer
        and tags it automatically, if it is not present."""
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        if not self.is_tagged(TIMEXES):
            if self.__timex_tagger is None:
                self.__timex_tagger = load_default_timex_tagger()
            self.__timex_tagger.tag_document(self, **self.__kwargs)
            self.__tagged.add(TIMEXES)
        return self

    @cached_property
    def timexes(self):
        """The list of elements in ``timexes`` layer."""
        if not self.is_tagged(TIMEXES):
            self.tag_timexes()
        return self[TIMEXES]

    @cached_property
    def timex_texts(self):
        """The list of texts representing ``timexes`` layer elements."""
        return [timex.get(TEXT, '') for timex in self.timexes]

    @cached_property
    def timex_values(self):
        """The list of timex values of ``timexes`` layer elements."""
        return [timex[TMX_VALUE] for timex in self.timexes]

    @cached_property
    def timex_types(self):
        """The list of timex types of ``timexes`` layer elements."""
        return [timex[TMX_TYPE] for timex in self.timexes]

    @cached_property
    def timex_ids(self):
        """The list of timex id-s of ``timexes`` layer elements."""
        return [timex[TMX_ID] for timex in self.timexes]

    @cached_property
    def timex_starts(self):
        """The list of start positions of ``timexes`` layer elements."""
        if not self.is_tagged(TIMEXES):
            self.tag_timexes()
        return self.starts(TIMEXES)

    @cached_property
    def timex_ends(self):
        """The list of end positions of ``timexes`` layer elements."""
        if not self.is_tagged(TIMEXES):
            self.tag_timexes()
        return self.ends(TIMEXES)

    @cached_property
    def timex_spans(self):
        """The list of spans of ``timexes`` layer elements."""
        if not self.is_tagged(TIMEXES):
            self.tag_timexes()
        return self.spans(TIMEXES)

    def tag_clause_annotations(self):
        """Tag clause annotations in ``words`` layer.
        Depends on morphological analysis.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        if self.__clause_segmenter is None:
            self.__clause_segmenter = load_default_clausesegmenter()
        self.__tagged.add(CLAUSE_ANNOTATION)
        return self.__clause_segmenter.tag(self)

    @cached_property
    def clause_annotations(self):
        """The list of clause annotations in ``words`` layer."""
        if not self.is_tagged(CLAUSE_ANNOTATION):
            self.tag_clause_annotations()
        return [word.get(CLAUSE_ANNOTATION, None) for word in self[WORDS]]

    @cached_property
    def clause_indices(self):
        """The list of clause indices in ``words`` layer.
        The indices are unique only in the boundary of a single sentence.
        """
        if not self.is_tagged(CLAUSE_ANNOTATION):
            self.tag_clause_annotations()
        return [word.get(CLAUSE_IDX, None) for word in self[WORDS]]

    def tag_clauses(self):
        """Create ``clauses`` multilayer.

        Depends on clause annotations."""
        if not self.is_tagged(CLAUSE_ANNOTATION):
            self.tag_clause_annotations()

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
        self.__tagged.add(CLAUSES)
        return self

    @cached_property
    def clauses(self):
        """The elements of ``clauses`` multilayer."""
        if not self.is_tagged(CLAUSES):
            self.tag_clauses()
        return self[CLAUSES]

    @cached_property
    def clause_texts(self):
        """The texts of ``clauses`` multilayer elements.
        Non-consequent spans are concatenated with space character by default.
        Use :py:meth:`~estnltk.text.Text.texts` method to supply custom separators.
        """
        if not self.is_tagged(CLAUSES):
            self.tag_clauses()
        return self.texts(CLAUSES)

    def tag_verb_chains(self):
        """Create ``verb_chains`` layer.
        Depends on ``clauses`` layer.
        """
        if not self.is_tagged(CLAUSES):
            self.tag_clauses()
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
        self.__tagged.add(VERB_CHAINS)
        return self

    @cached_property
    def verb_chains(self):
        """The list of elements of ``verb_chains`` layer."""
        if not self.is_tagged(VERB_CHAINS):
            self.tag_verb_chains()
        return self[VERB_CHAINS]

    @cached_property
    def verb_chain_texts(self):
        """The list of texts of ``verb_chains`` layer elements."""
        if not self.is_tagged(VERB_CHAINS):
            self.tag_verb_chains()
        return self.texts(VERB_CHAINS)

    @cached_property
    def verb_chain_patterns(self):
        """The patterns of ``verb_chains`` elements."""
        return [vc[PATTERN] for vc in self.verb_chains]

    @cached_property
    def verb_chain_roots(self):
        """The chain roots of ``verb_chains`` elements."""
        return [vc[ROOTS] for vc in self.verb_chains]

    @cached_property
    def verb_chain_morphs(self):
        """The morph attributes of ``verb_chains`` elements."""
        return [vc[MORPH] for vc in self.verb_chains]

    @cached_property
    def verb_chain_polarities(self):
        """The polarities of ``verb_chains`` elements."""
        return [vc[POLARITY] for vc in self.verb_chains]

    @cached_property
    def verb_chain_tenses(self):
        """The tense attributes of ``verb_chains`` elements."""
        return [vc[TENSE] for vc in self.verb_chains]

    @cached_property
    def verb_chain_moods(self):
        """The mood attributes of ``verb_chains`` elements."""
        return [vc[MOOD] for vc in self.verb_chains]

    @cached_property
    def verb_chain_voices(self):
        """The voice attributes of ``verb_chains`` elements."""
        return [vc[VOICE] for vc in self.verb_chains]

    @cached_property
    def verb_chain_clause_indices(self):
        """The clause indices of ``verb_chains`` elements."""
        return [vc[CLAUSE_IDX] for vc in self.verb_chains]

    @cached_property
    def verb_chain_starts(self):
        """The start positions of ``verb_chains`` elements."""
        if not self.is_tagged(VERB_CHAINS):
            self.tag_verb_chains()
        return self.starts(VERB_CHAINS)

    @cached_property
    def verb_chain_ends(self):
        """The end positions of ``verb_chains`` elements."""
        if not self.is_tagged(VERB_CHAINS):
            self.tag_verb_chains()
        return self.ends(VERB_CHAINS)

    @cached_property
    def verb_chain_other_verbs(self):
        """The other verb attributes of ``verb_chains`` elements."""
        return [vc[OTHER_VERBS] for vc in self.verb_chains]

    def tag_wordnet(self, **kwargs):
        """Create wordnet attribute in ``words`` layer.

        See :py:meth:`~estnltk.text.wordnet_tagger.WordnetTagger.tag_text` method
        for applicable keyword arguments.
        """
        global wordnet_tagger
        if wordnet_tagger is None: # cached wn tagger
            wordnet_tagger = WordnetTagger()
        self.__wordnet_tagger = wordnet_tagger
        self.__tagged.add(WORDNET)
        if len(kwargs) > 0:
            return self.__wordnet_tagger.tag_text(self, **kwargs)
        return self.__wordnet_tagger.tag_text(self, **self.__kwargs)

    @cached_property
    def wordnet_annotations(self):
        """The list of wordnet annotations of ``words`` layer."""
        if not self.is_tagged(WORDNET):
            self.tag_wordnet()
        return [[a[WORDNET] for a in analysis] for analysis in self.analysis]

    @cached_property
    def synsets(self):
        """The list of annotated synsets of ``words`` layer."""
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
        """The list of literals per word in ``words`` layer."""
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
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return [data[SPELLING] for data in vabamorf.spellcheck(self.word_texts, suggestions=False)]

    @cached_property
    def spelling_suggestions(self):
        """The list of spelling suggestions per misspelled word."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return [data[SUGGESTIONS] for data in vabamorf.spellcheck(self.word_texts, suggestions=True)]

    @cached_property
    def spellcheck_results(self):
        """The list of True/False values denoting the correct spelling of words."""
        if not self.is_tagged(WORDS):
            self.tokenize_words()
        return vabamorf.spellcheck(self.word_texts, suggestions=True)

    def fix_spelling(self):
        """Fix spelling of the text.

        Note that this method uses the first suggestion that is given for each misspelled word.
        It does not perform any sophisticated analysis to determine which one of the suggestions
        fits best into the context.

        Returns
        -------
        Text
            A copy of this instance with automatically fixed spelling.
        """
        if not self.is_tagged(WORDS):
            self.tokenize_words()
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
        """Does this text contain allowed/valid characters as defined by
        the :py:class:`~estnltk.textcleaner.TextCleaner` instances supplied
        to this Text."""
        return self.__text_cleaner.is_valid(self[TEXT])

    @cached_property
    def invalid_characters(self):
        """List of invalid characters found in this text."""
        return self.__text_cleaner.invalid_characters(self[TEXT])

    def clean(self):
        """Return a copy of this Text instance with invalid characters removed."""
        return Text(self.__text_cleaner.clean(self[TEXT]), **self.__kwargs)

    # ///////////////////////////////////////////////////////////////////
    # SPLITTING
    # ///////////////////////////////////////////////////////////////////

    def split_given_spans(self, spans, sep=' '):
        """Split the text into several pieces.

        Resulting texts have all the layers that are present in the text instance that is splitted.
        The elements are copied to resulting pieces that are covered by their spans.
        However, this can result in empty layers if no element of a splitted layer fits into
        a span of a particular output piece.

        The positions of layer elements that are copied are translated according to the container span,
        so they are consistent with returned text lengths.

        Parameters
        ----------

        spans: list of spans.
            The positions determining the regions that will end up as individual pieces.
            Spans themselves can be lists of spans, which denote multilayer-style text regions.
        sep: str
            The separator that is used to join together text pieces of multilayer spans.

        Returns
        -------
        list of Text
            One instance of text per span.
        """
        N = len(spans)
        results = [{TEXT: text} for text in self.texts_from_spans(spans, sep=sep)]
        for elem in self:
            if isinstance(self[elem], list):
                splits = divide_by_spans(self[elem], spans, translate=True, sep=sep)
                for idx in range(N):
                    results[idx][elem] = splits[idx]
        return [Text(res) for res in results]

    def split_by(self, layer, sep=' '):
        """Split the text into multiple instances defined by elements of given layer.

        The spans for layer elements are extracted and feed to :py:meth:`~estnltk.text.Text.split_given_spans`
        method.

        Parameters
        ----------
        layer: str
            String determining the layer that is used to define the start and end positions of resulting splits.
        sep: str (default: ' ')
            The separator to use to join texts of multilayer elements.

        Returns
        -------
        list of Text
        """
        if not self.is_tagged(layer):
            self.tag(layer)
        return self.split_given_spans(self.spans(layer), sep=sep)

    def split_by_sentences(self):
        """Split the text into individual sentences."""
        return self.split_by(SENTENCES)

    def split_by_words(self):
        """Split the text into individual words."""
        return self.split_by(WORDS)

    def split_by_regex(self, regex_or_pattern, flags=re.U, gaps=True):
        """Split the text into multiple instances using a regex.

        Parameters
        ----------
        regex_or_pattern: str or compiled pattern
            The regular expression to use for splitting.
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
        if gaps: # tag cap spans
            for mo in regex.finditer(text):
                start, end = mo.start(), mo.end()
                if start > last_end:
                    spans.append((last_end, start))
                last_end = end
            if last_end < len(text):
                spans.append((last_end, len(text)))
        else: # use matched regions
            spans = [(mo.start(), mo.end()) for mo in regex.finditer(text)]
        return self.split_given_spans(spans)

    # ///////////////////////////////////////////////////////////////////
    # DIVIDING
    # ///////////////////////////////////////////////////////////////////

    def divide(self, layer=WORDS, by=SENTENCES):
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
        if not self.is_tagged(layer):
            self.tag(layer)
        if not self.is_tagged(by):
            self.tag(by)
        return divide(self[layer], self[by])

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

