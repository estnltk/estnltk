# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import regex as re
from functools import reduce
from itertools import chain
from collections import defaultdict
import six
from ..text import Text
from .match import Match, concatenate_matches, copy_rename, intersect
from .conflictresolver import resolve_using_maximal_coverage


class Symbol(object):
    """Base symbol for the grammar."""

    def __init__(self, name=None):
        self.__name = name

    @property
    def name(self):
        """The name of the symbol. If there is no name, this is None"""
        return self.__name

    def annotate(self, text, conflict_resolver=resolve_using_maximal_coverage):
        if isinstance(text, six.string_types):
            text = Text(text)
        matches = self.get_matches(text, conflict_resolver=conflict_resolver)
        layers = defaultdict(list)
        for m in matches:
            md = m.dict
            for k, v in md.items():
                layers[k].append(v)
        for k, v in layers.items():
            v.sort()
            text[k] = v
        return text

    def get_matches(self, text, cache=None, conflict_resolver=resolve_using_maximal_coverage):
        """Get the matches of the symbol on given text."""
        is_root_node = False
        if cache is None:
            cache = {}
            is_root_node = True
        if id(self) in cache:
            return cache[id(self)]
        matches = self.get_matches_without_cache(text, cache=cache)
        cache[id(self)] = matches

        # if this is the root node, resolve the matches
        if is_root_node and conflict_resolver is not None:
            return conflict_resolver(matches)
        return matches

    def get_matches_without_cache(self, text, **env):
        raise NotImplementedError('When this method is called for the case class, it indicates a programming error!')


class Regex(Symbol):
    """Regular expression symbol."""

    def __init__(self, pattern, flags=re.UNICODE | re.MULTILINE, name=None):
        super(Regex, self).__init__(name)
        self.__pattern = re.compile(pattern, flags=flags)

    @property
    def pattern(self):
        return self.__pattern

    def get_matches_without_cache(self, text, **env):
        matches = []
        for mo in self.pattern.finditer(text.text):
            start, end = mo.start(), mo.end()
            matches.append(Match(start, end, text.text[start:end], self.name))
        return matches


class IRegex(Regex):
    """Case insensitive regular expression symbol."""

    def __init__(self, pattern, flags=re.UNICODE | re.MULTILINE | re.IGNORECASE, name=None):
        super(IRegex, self).__init__(pattern, flags, name)


class Lemmas(Symbol):
    """Symbol that matches a list of lemmas."""

    def __init__(self, *lemmas, **kwargs):
        super(Lemmas, self).__init__(kwargs.get('name'))
        self.__lemmas = lemmas
        self.__pattern = re.compile('\L<lemmas>', lemmas=lemmas, flags=re.UNICODE | re.IGNORECASE)

    @property
    def lemmas(self):
        return self.__lemmas

    @property
    def pattern(self):
        return self.__pattern

    def get_matches_without_cache(self, text, **env):
        matches = []
        lemmas = text.lemma_lists
        spans = text.word_spans
        for word_lemmas, (start, end) in zip(lemmas, spans):
            for word_lemma in word_lemmas:
                if self.pattern.match(word_lemma):
                    matches.append(Match(start, end, text.text[start:end], self.name))
        return matches


class Postags(Symbol):
    """Symbol that matches a list of part-of-speech tags."""

    def __init__(self, *postags, **kwargs):
        super(Postags, self).__init__(kwargs.get('name'))
        self.__postags = postags
        self.__pattern = re.compile('\L<postags>', postags=postags, flags=re.UNICODE | re.IGNORECASE)

    @property
    def postags(self):
        return self.__postags

    @property
    def pattern(self):
        return self.__pattern

    def get_matches_without_cache(self, text, **env):
        matches = []
        postags = text.postag_lists
        spans = text.word_spans
        for word_postags, (start, end) in zip(postags, spans):
            for word_postag in word_postags:
                if self.pattern.match(word_postag):
                    matches.append(Match(start, end, text.text[start:end], self.name))
        return matches


class Suffix(Symbol):
    """Symbol that matches word suffixes."""

    def __init__(self, suffix, **kwargs):
        super(Suffix, self).__init__(kwargs.get('name'))
        self.__suffix = suffix.lower()

    @property
    def suffix(self):
        return self.__suffix

    def get_matches_without_cache(self, text, **env):
        matches = []
        word_texts = text.word_texts
        spans = text.word_spans
        suffix = self.suffix
        for word_text, (start, end) in zip(word_texts, spans):
            if word_text.lower().endswith(suffix):
                matches.append(Match(start, end, text.text[start:end], self.name))
        return matches


class Layer(Symbol):
    """Symbol that matches elements of given layer."""

    def __init__(self, layer_name, **kwargs):
        super(Layer, self).__init__(kwargs.get('name'))
        self.__layer_name = layer_name

    @property
    def layer_name(self):
        return self.__layer_name

    def get_matches_without_cache(self, text, **env):
        return [Match(start, end, text.text[start:end], self.name) for start, end in text.spans(self.layer_name)]


class LayerRegex(Symbol):
    """Symbol that matches regular expressions on texts of the given layer."""

    def __init__(self, layer_name, regex, **kwargs):
        super(LayerRegex, self).__init__(kwargs.get('name'))
        flags = kwargs.get('flags', re.IGNORECASE)
        self.__layer_name = layer_name
        self.__regex = re.compile(regex, flags)

    @property
    def layer_name(self):
        return self.__layer_name

    @property
    def regex(self):
        return self.__regex

    def get_matches_without_cache(self, text, **env):
        regex = self.regex
        matches = []
        for start, end in text.spans(self.layer_name):
            elem_text = text.text[start:end]
            if regex.match(elem_text) is not None:
                matches.append(Match(start, end, elem_text, self.name))
        return matches


class Union(Symbol):
    """Symbol that unions two other symbols."""

    def __init__(self, *symbols, **kwargs):
        super(Union, self).__init__(kwargs.get('name'))
        self.__symbols = symbols

    @property
    def symbols(self):
        return self.__symbols

    def get_matches_without_cache(self, text, **env):
        symbols_matches = [e.get_matches(text, **env) for e in self.symbols]
        matches = list(sorted(chain(*symbols_matches)))
        # if the union has a name, then name all the matches after this
        if self.name is not None:
            matches = [copy_rename(m, self.name) for m in matches]
        return matches


class Intersection(Symbol):
    """Symbol that intersects two different symbols."""

    def __init__(self, *symbols, **kwargs):
        super(Intersection, self).__init__(kwargs.get('name'))
        self.__symbols = symbols

    @property
    def symbols(self):
        return self.__symbols

    def get_matches_without_cache(self, text, **env):
        symbols_matches = [list(e.get_matches(text, **env)) for e in self.symbols]
        matches = reduce(intersect, symbols_matches)
        if self.name is not None:
            matches = [copy_rename(m, self.name) for m in matches]
        return matches


def concat(matches_a, matches_b, text, name=None):
    i, j = 0, 0
    n, m = len(matches_a), len(matches_b)
    matches = []
    while i < n and j < m:
        a, b = matches_a[i], matches_b[j]
        if a.end == b.start:
            matches.append(concatenate_matches(a, b, text.text, name))
            j += 1
        elif a.end < b.start:
            i += 1
        else:
            j += 1
    return matches


class Concatenation(Symbol):
    """Concatenate symbols."""

    def __init__(self, *symbols, **kwargs):
        """

        Parameters
        ----------
        symbol.. : list of :py:class:`~estnltk.grammar.Symbol`
            The symbols that are coing to be concatenated.
        sep: :py:class:`~estnltk.grammar.Symbol`
            The optional separator symbol.
        """
        super(Concatenation, self).__init__(kwargs.get('name'))
        sep = kwargs.get('sep', None)
        self.__symbols = []
        for idx, sym in enumerate(symbols):
            if idx > 0 and sep is not None:
                self.__symbols.append(sep)
            self.__symbols.append(sym)

    @property
    def symbols(self):
        return self.__symbols

    def get_matches_without_cache(self, text, **env):
        symbol_matches = [e.get_matches(text, **env) for e in self.symbols]
        matches = list(reduce(lambda a, b: concat(a, b, text), symbol_matches))
        if self.name is not None:
            matches = [copy_rename(m, self.name) for m in matches]
        return matches


def allgaps(matches_a, matches_b, text, name=None):
    matches = []
    for a in matches_a:
        for b in matches_b:
            if a.end <= b.start:
                matches.append(concatenate_matches(a, b, text.text, name))
    return matches


class AllGaps(Symbol):
    """Concatenate symbols, but allow gaps of any size between the symbols."""

    def __init__(self, *symbols, **kwargs):
        super(AllGaps, self).__init__(kwargs.get('name'))
        self.__symbols = symbols

    @property
    def symbols(self):
        return self.__symbols

    def get_matches_without_cache(self, text, **env):
        symbol_matches = [e.get_matches(text, **env) for e in self.symbols]
        matches = list(reduce(lambda a, b: allgaps(a, b, text), symbol_matches))
        if self.name is not None:
            matches = [copy_rename(m, self.name) for m in matches]
        return matches


def gaps(matches_a, matches_b, text, name=None):
    matches = []
    for a in matches_a:
        for b in matches_b:
            if a.end <= b.start:
                matches.append(concatenate_matches(a, b, text.text, name))
                break
    return matches


class Gaps(Symbol):

    def __init__(self, *symbols, **kwargs):
        super(Gaps, self).__init__(kwargs.get('name'))
        self.__symbols = symbols

    @property
    def symbols(self):
        return self.__symbols

    def get_matches_without_cache(self, text, **env):
        symbol_matches = [e.get_matches(text, **env) for e in self.symbols]
        matches = list(reduce(lambda a, b: gaps(a, b, text), symbol_matches))
        if self.name is not None:
            matches = [copy_rename(m, self.name) for m in matches]
        return matches

