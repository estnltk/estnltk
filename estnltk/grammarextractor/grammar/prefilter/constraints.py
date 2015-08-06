# -*- coding: utf-8 -*-
"""
Module defining dictionaries for building the prefilter constraint list.
They can be used to create database queries that filter out documents
that cannot be matched by grammar.

As a result, the matcher has to look through fewer documents and hence is faster.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .dictionaries import WordDictionary, LemmaDictionary


class Constraints(object):

    def __init__(self, word_dict=None, lemma_dict=None, all=False):
        self.__word_dict = WordDictionary() if word_dict is None else word_dict
        self.__lemma_dict = LemmaDictionary() if lemma_dict is None else lemma_dict
        self.__all = all

    @property
    def word_dict(self):
        return self.__word_dict

    def __or__(self, other):
        all = self.__all or other.__all
        if all:
            return Constraints(all=True)
        word_dict = self.__word_dict | other.__word_dict
        lemma_dict = self.__lemma_dict | other.__lemma_dict
        return Constraints(word_dict, lemma_dict, False)

    def __and__(self, other):
        all = self._all and other.__all
        if all:
            return Constraints(all=True)
        word_dict = self.__word_dict & other.__word_dict
        lemma_dict = self.__lemma_dict & other.__lemma_dict
        return Constraints(word_dict, lemma_dict, False)
