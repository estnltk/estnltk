# -*- coding: utf-8 -*-
"""
Text module contains central functionality of Estnltk.
It sets up standard functionality for tokenziation and tagging and hooks it up with
:py:class:`~estnltk.text.Text` class.

"""
from __future__ import unicode_literals, print_function, absolute_import

import nltk.data
import pandas
import regex as re
import six
from cached_property import cached_property
from nltk.tokenize.regexp import RegexpTokenizer

from estnltk.legacy.core import as_unicode, POSTAG_DESCRIPTIONS
from estnltk.legacy.dividing import divide, divide_by_spans
from estnltk.legacy.names import *
from estnltk.taggers.legacy_tokenizers import EstWordTokenizer
from estnltk.vabamorf import morf as vabamorf


# default functionality
paragraph_tokenizer = RegexpTokenizer('\n\n', gaps=True, discard_empty=True)

# use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
sentence_tokenizer = None
try:
    sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
except LookupError:
    import nltk.downloader
    nltk.downloader.download('punkt')
finally:
    if sentence_tokenizer is None:
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')

word_tokenizer = EstWordTokenizer()

class Asd:
    pass

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
        syntax_tagger: estnltk.syntax.tagger.SyntaxTagger
            Kaili's and Tiina's syntax tagger wrapper.
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

    def get_kwargs(self):
        """Get the keyword arguments that were passed to the :py:class:`~estnltk.text.Text` when it was constructed."""
        return self.__kwargs

    def is_tagged(self, layer):
        """Is the given element tokenized/tagged?"""
        # we have a number of special names that are not layers but instead
        # attributes of "words" layer
        if layer == ANALYSIS:
            if WORDS in self and len(self[WORDS]) > 0:
                return ANALYSIS in self[WORDS][0]
        elif layer == SYNTAX:
            if WORDS in self and len(self[WORDS]) > 0:
                return SYNTAX in self[WORDS][0]
        elif layer == LABEL:
            if WORDS in self and len(self[WORDS]) > 0:
                return LABEL in self[WORDS][0]
        elif layer == CLAUSE_ANNOTATION:
            if WORDS in self and len(self[WORDS]) > 0:
                return CLAUSE_ANNOTATION in self[WORDS][0]
        elif layer == WORDNET:
            if WORDS in self and len(self[WORDS]) > 0:
                if ANALYSIS in self[WORDS][0] and len(self[WORDS][0][ANALYSIS]) > 0:
                    return WORDNET in self[WORDS][0][ANALYSIS][0]
        else:
            return layer in self
        return False  # do not remove False

    def tag_all(self):
        """Tag all layers."""
        return self.tag_timexes().tag_named_entities().tag_verb_chains()

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
           Automatically tokenizes paragraphs, if they are not already tokenized.
           Also, if word tokenization has already been performed, tries to fit 
           the sentence tokenization into the existing word tokenization;
        """
        if not self.is_tagged(PARAGRAPHS):
            self.tokenize_paragraphs()
        tok  = self.__sentence_tokenizer
        text = self.text
        dicts = []
        for paragraph in self[PARAGRAPHS]:
            para_start, para_end = paragraph[START], paragraph[END]
            para_text = text[para_start:para_end]
            if not self.is_tagged(WORDS):
                # Non-hack variant: word tokenization has not been applied yet,
                # so we proceed in natural order (first sentences, then words)
                spans = tok.span_tokenize(para_text)
                for start, end in spans:
                    dicts.append({'start': start+para_start, 'end': end+para_start})
            else:
                # A hack variant: word tokenization has already been made, so
                # we try to use existing word tokenization (first words, then sentences)
                para_words = \
                    [ w for w in self[WORDS] if w[START]>=para_start and w[END]<=para_end ]
                para_word_texts = \
                    [ w[TEXT] for w in para_words ]
                try:
                    # Apply sentences_from_tokens method (if available)
                    sents = tok.sentences_from_tokens( para_word_texts )
                except AttributeError as e:
                    raise
                # Align result of the sentence tokenization with the initial word tokenization
                # in order to determine the sentence boundaries
                i = 0
                for sentence in sents:
                    j = 0
                    firstToken = None
                    lastToken  = None
                    while i < len(para_words):
                        if para_words[i][TEXT] != sentence[j]:
                            raise Exception('Error on aligning: ', para_word_texts,' and ',sentence,' at positions ',i,j)
                        if j == 0:
                            firstToken = para_words[i]
                        if j == len(sentence) - 1:
                            lastToken = para_words[i]
                            i+=1
                            break
                        j+=1
                        i+=1
                    sentenceDict = \
                        {'start': firstToken[START], 'end': lastToken[END]}
                    dicts.append( sentenceDict )
                # Note: We also need to invalidate the cached properties providing the
                #       sentence information, as otherwise, if the properties have been
                #       called already, new calls would return the old state of sentence 
                #       tokenization;
                for sentence_attrib in ['sentences', 'sentence_texts', 'sentence_spans', \
                                        'sentence_starts', 'sentence_ends']:
                    try:
                        # invalidate the cache
                        delattr(self, sentence_attrib)
                    except AttributeError:
                        # it's ok, if the cached property has not been called yet
                        pass
        self[SENTENCES] = dicts
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
    def lemma_lists(self):
        """Lemma lists.

        Ambiguous cases are separate list elements.
        """
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return [[an[LEMMA] for an in word[ANALYSIS]] for word in self[WORDS]]

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
    def postag_lists(self):
        if not self.is_tagged(ANALYSIS):
            self.tag_analysis()
        return [[an[POSTAG] for an in word[ANALYSIS]] for word in self[WORDS]]

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





    def is_simple(self, layer):
        elems = self[layer]
        if len(elems) > 0:
            return isinstance(elems[0][START], int)
        return False

    def is_multi(self, layer):
        elems = self[layer]
        if len(elems) > 0:
            return isinstance(elems[0][START], list)
        return False

    def tag_with_regex(self, name, pattern, flags=0):
        if name in self:
            raise ValueError('Layer or attribute with name <{0}> already exists!'.format(name))
        if isinstance(pattern, six.string_types):
            pattern = re.compile(pattern, flags)
        self[name] = [{START: mo.start(), END: mo.end()} for mo in pattern.finditer(self[TEXT])]
        return self

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

