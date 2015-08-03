# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from ..common import is_valid_symbol_name
from ..common import re


def split_by_case_sensitive(elems):
    case_sensitive = []
    case_insensitive = []
    for elem, case in elems:
        if case:
            case_sensitive.append(elem)
        else:
            case_insensitive.append(elem)
    return case_sensitive, case_insensitive


def concat_regexes(regexes, name):
    return '(?P<{0}>('.format(name) + ')|('.join(regexes) + '))'


def get_word_patterns(name, words):
    words, iwords = split_by_case_sensitive(words)
    patterns = []
    if len(words) > 0:
        regex = re.compile('(?P<{0}>\L<words>)'.format(name), words=words, flags=re.UNICODE)
        patterns.append(regex)
    if len(iwords) > 0:
        regex = re.compile('(?P<{0}>\L<words>)'.format(name), words=iwords, flags=re.UNICODE | re.IGNORECASE)
        patterns.append(regex)
    return patterns


def get_regex_patterns(name, regexes):
    regexes, iregexes = split_by_case_sensitive(regexes)
    patterns = []
    if len(regexes) > 0:
        regex = re.compile(concat_regexes(regexes, name), re.UNICODE)
        patterns.append(regex)
    if len(iregexes) > 0:
        regex = re.compile(concat_regexes(iregexes, name), re.UNICODE | re.IGNORECASE)
        patterns.append(regex)
    return patterns


def get_patterns(name, words, regexes):
    return get_word_patterns(name, words) + get_regex_patterns(name, regexes)


def get_lemma_regex(name, lemmas):
    if len(lemmas) > 0:
        return re.compile('(?P<{0}>\L<lemmas>)'.format(name), lemmas=lemmas, flags=re.UNICODE | re.IGNORECASE)


def get_postag_regex(name, postags):
    if len(postags) > 0:
        return re.compile('(?P<{0}>\L<postags>)'.format(name), postags=postags, flags=re.UNICODE | re.IGNORECASE)


class Symbol(object):

    def __init__(self, name, **kwargs):
        """Initialize a symbol.

        Parameters
        ----------
        name: str
            The name of the symbol.
        productions: list of ProductionNode
            The productions of this symbol.
        words: list of (str, bool) tuples
            Each tuple has a word and a boolean indicating if the matching should be case sensitive.
        regexes: list of (str, bool) tuples
            Each tuple has a regex and a boolean indicating if the matching should be case sensitive.
        lemmas: list of str
            List of lemmas that can be matched. Lemmas can be matched only at word boundaries.
        postags: list of str
            List of postags that can be matched at this sumbol. Matches can happen only at word boundaries.
        """
        assert is_valid_symbol_name(name)
        self.__name = name
        self.__productions = kwargs.get('productions', [])
        self.__patterns = get_patterns(self.name, kwargs.get('words', []), kwargs.get('regexes', []))
        self.__lemma_regex = get_lemma_regex(self.name, kwargs.get('lemmas', []))
        self.__postag_regex = get_postag_regex(self.name, kwargs.get('postags', []))

    @property
    def name(self):
        return self.__name

    @property
    def productions(self):
        return self.__productions

    @property
    def patterns(self):
        return self.__patterns

    @property
    def lemma_regex(self):
        return self.__lemma_regex

    @property
    def postag_regex(self):
        return self.__postag_regex

