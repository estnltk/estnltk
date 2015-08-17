# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .symbol import Symbol
from .prefilter import PreFilter


class Grammar(object):

    def __init__(self, symbols, exports, words, regexes, lemmas, postags, productions, examples):
        self.__exports = exports
        self.__examples = examples
        # set up symbolnodes
        self.__symbols = {}
        for name in symbols:
            kwargs = {
                'words': words.get(name, []),
                'regexes': regexes.get(name, []),
                'lemmas': lemmas.get(name, []),
                'postags': postags.get(name, []),
                'productions': productions.get(name, [])
            }
            self.__symbols[name] = Symbol(name, **kwargs)

    def get_symbol(self, name):
        return self.__symbols[name]

    @property
    def exports(self):
        return self.__exports

    @property
    def examples(self):
        return self.__examples

    @property
    def constraints(self):
        prefilter = PreFilter(self)
        return prefilter.constraints

