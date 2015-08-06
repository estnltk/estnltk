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
        self.__words = set()
        self.__case_sensitivity = dict()

    def add_word(self, word, case_sensitive):
        self.__words.add(word)
        self.__case_sensitivity[word] = case_sensitive

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __or__(self, other):
        words = self.__words | other.__words
        case_sensitivity = self.__case_sensitivity | other.__case_sensitivity
        wd = WordDictionary()
        wd.__words = words
        wd.__case_sensitivity = case_sensitivity
        return wd

    def __and__(self, other):
        words = self.__words & other.__words
        case_sensitivity = self.__case_sensitivity & other.__case_sensitivity
        wd = WordDictionary()
        wd.__words = words
        wd.__case_sensitivity = case_sensitivity
        return wd


class LemmaDictionary(object):

    def __init__(self):
        self.__lemmas = set()

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
