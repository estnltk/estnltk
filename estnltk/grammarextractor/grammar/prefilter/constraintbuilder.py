# -*- coding: utf-8 -*-
"""
This module defines functions to build Constraint
objects from grammar symbols.
"""
from __future__ import unicode_literals, print_function, absolute_import

from functools import reduce

from .constraints import Constraints
from .dictionaries import CASE_INSENSITIVE, CASE_SENSITIVE, WordDictionary, LemmaDictionary
from ..production_nodes import Name, Optional, Or, List, Regex


def unite_constraints(c1, c2):
    return c1 | c2


def intersect_constraints(c1, c2):
    return c1 & c2


def build_list(list_node, grammar):
    constraints = (build_node(child, grammar) for child in list_node.children)
    return reduce(intersect_constraints, constraints)


def build_or(or_node, grammar):
    constraints = (build_node(child, grammar) for child in or_node.children)
    return reduce(unite_constraints, constraints)


def build_optional(optional_node, grammar):
    return Constraints(all=True)


def build_regex(regex_node, grammar):
    return Constraints(all=True)


def build_name(name_node, grammar):
    cb = ConstraintsBuilder(grammar.get_symbol(name_node.name), grammar)
    return cb.constraints


BUILDERS = {
    type(List): build_list,
    type(Or): build_or,
    type(Optional): build_optional,
    type(Regex): build_regex,
    type(Name): build_name
}


def build_node(node, grammar):
    if isinstance(node, List):
        return build_list(node, grammar)
    if isinstance(node, Or):
        return build_or(node, grammar)
    if isinstance(node, Optional):
        return build_optional(node, grammar)
    if isinstance(node, Regex):
        return build_regex(node, grammar)
    if isinstance(node, Name):
        return build_name(node, grammar)
    assert False, 'Code should not reach here!'


class ConstraintsBuilder(object):

    def __init__(self, symbol, grammar):
        self.__symbol = symbol
        self.__grammar = grammar
        self.__constraints = self.__build()

    @property
    def symbol(self):
        return self.__symbol

    @property
    def grammar(self):
        return self.__grammar

    @property
    def constraints(self):
        return self.__constraints

    def __word_dict(self):
        symbol = self.symbol
        word_dict = WordDictionary()
        for word in symbol.words:
            word_dict.add_word(word, CASE_SENSITIVE)
        for word in symbol.iwords:
            word_dict.add_word(word, CASE_INSENSITIVE)
        return word_dict

    def __lemma_dict(self):
        symbol = self.symbol
        lemma_dict = LemmaDictionary()
        for lemma in symbol.lemmas:
            lemma_dict.add_lemma(lemma)
        return lemma_dict

    def __build(self):
        # in case there are regexes, we need to match all documents
        if len(self.symbol.regexes) > 0 or len(self.symbol.iregexes) > 0:
            return Constraints(all=True)
        # build word and lemma dictionaries
        word_dict = self.__word_dict()
        lemma_dict = self.__lemma_dict()
        # and get the default constraints
        self_constraints = Constraints(word_dict, lemma_dict, False)
        # get the constraints from productions
        constraints = (build_node(production, self.grammar) for production in self.symbol.productions)
        return reduce(unite_constraints, constraints, self_constraints)
