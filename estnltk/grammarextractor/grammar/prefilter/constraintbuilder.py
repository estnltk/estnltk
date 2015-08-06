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
from ..symbol import Symbol
from ..grammar import Grammar


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
    cb = ConstraintsBuilder(grammar.get_symbol(name_node.name))
    return cb.constraints


BUILDERS = {
    type(List): build_list,
    type(Or): build_or,
    type(Optional): build_optional,
    type(Regex): build_regex,
    type(Name): build_name
}


def build_node(node, grammar):
    f = BUILDERS[type(node)]
    return f(node, grammar)


class ConstraintsBuilder(object):

    def __init__(self, symbol, grammar):
        assert isinstance(symbol, Symbol)
        assert isinstance(grammar, Grammar)
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
            word_dict.add(word, CASE_SENSITIVE)
        for word in symbol.iwords:
            word_dict.add(word, CASE_INSENSITIVE)
        return word_dict

    def __lemma_dict(self):
        symbol = self.symbol
        lemma_dict = LemmaDictionary()
        for lemma in symbol.lemmas:
            lemma_dict.add_lemma(lemma)
        return lemma_dict

    def __build(self):
        # in case there are regexes, we need to match all documents
        if self.symbol.regexes.size() > 0:
            return Constraints(all=True)
        # build word and lemma dictionaries
        word_dict = self.__word_dict()
        lemma_dict = self.__lemma_dict()
        # and get the default constraints
        self_constraints = Constraints(word_dict, lemma_dict, False)
        # get the constraints from productions
        constraints = (build_node(production, self.grammar) for production in self.symbol.productions)
        return reduce(unite_constraints, constraints, self_constraints)
