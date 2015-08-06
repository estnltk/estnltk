# -*- coding: utf-8 -*-
"""
This module defines functionality that can be used to
filter documents before matching.

It helps to minimize the number of documents that have to be searched.
Of course, the efficiency of this depends on the defined symbols,
especially the words and lemmas that are defined.

Rules are simple:

Nodes that have terminal property can be used.
Terminal property means that node has defined matching words, lemmas or postags.


"""
from __future__ import unicode_literals, print_function, absolute_import

import weakref
from functools import reduce

from .constraintbuilder import ConstraintsBuilder, unite_constraints


class PreFilter(object):

    def __init__(self, grammar):
        self.__grammar = weakref.proxy(grammar)

    @property
    def grammar(self):
        return self.__grammar

    @property
    def constraints(self):
        symbols = list(self.__grammar.exports.keys())
        constraints = (ConstraintsBuilder(symbol, self.grammar).constraints for symbol in symbols)
        return reduce(unite_constraints, constraints)
