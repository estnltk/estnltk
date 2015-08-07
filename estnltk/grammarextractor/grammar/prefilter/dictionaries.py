# -*- coding: utf-8 -*-
"""
Module defining dictionaries for building the prefilter constraint list.
They can be used to create database queries that filter out documents
that cannot be matched by grammar.

As a result, the matcher has to look through fewer documents and hence is faster.
"""
from __future__ import unicode_literals, print_function, absolute_import


CASE_SENSITIVE = True
CASE_INSENSITIVE = False


class WordDictionary(object):

    def __init__(self):
        self.__case_sensitive_words = set()
        self.__case_insensitive_words = set()

    @property
    def case_sensitive_words(self):
        return self.__case_sensitive_words

    @property
    def case_insensitive_words(self):
        return self.__case_insensitive_words

    def add_word(self, word, case_sensitive):
        if case_sensitive:
            self.__case_sensitive_words.add(word)
        self.__case_insensitive_words.add(word)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __or__(self, other):
        case_sensitive_words = self.case_sensitive_words | other.case_sensitive_words
        case_insensitive_words = self.case_insensitive_words | other.case_insensitive_words
        wd = WordDictionary()
        wd.__case_sensitive_Words = case_sensitive_words
        wd.__case_insensitive_words = case_insensitive_words
        return wd

    def __and__(self, other):
        case_sensitive_words = self.case_sensitive_words & other.case_sensitive_words
        case_insensitive_words = self.case_insensitive_words & other.case_insensitive_words
        wd = WordDictionary()
        wd.__case_sensitive_Words = case_sensitive_words
        wd.__case_insensitive_words = case_insensitive_words
        return wd


class LemmaDictionary(object):

    def __init__(self):
        self.__lemmas = set()

    @property
    def lemmas(self):
        return self.__lemmas

    def add_lemma(self, lemma):
        self.__lemmas.add(lemma)

    def __eq__(self, other):
        return self.__lemmas == other.__lemmas

    def __or__(self, other):
        lemmas = self.__lemmas | other.__lemmas
        ld = LemmaDictionary()
        ld.__lemmas = lemmas
        return ld

    def __and__(self, other):
        lemmas = self.__lemmas & other.__lemmas
        ld = LemmaDictionary()
        ld.__lemmas = lemmas
        return ld
