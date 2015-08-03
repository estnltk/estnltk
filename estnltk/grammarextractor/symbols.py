# -*- coding: utf-8 -*-
"""
This module defines symbols in the grammarextractor.

The symbols do not fall into 'terminal' and 'non-terminal' categories, but
rather combine the properties of both.
"""
from __future__ import unicode_literals, print_function, absolute_import

import regex as re

from .common import is_valid_symbol_name, is_valid_regex


class Symbol(object):

    def optimize(self):
        """Optimize redundant nodes: zero to one element lists and one elements Or."""
        return self


class Name(Symbol):

    def __init__(self, name):
        assert is_valid_symbol_name(name)
        self.__name = name

    @property
    def name(self):
        return self.__name

    @property
    def children(self):
        return []

    def __eq__(self, other):
        return isinstance(other, Name) and self.__dict__ == other.__dict__

    def __str__(self):
        return self.name


class Optional(Symbol):

    def __init__(self, symbol):
        self.__symbol = symbol

    @property
    def symbol(self):
        return self.__symbol

    @property
    def children(self):
        return [self.symbol]

    def optimize(self):
        symbol = self.symbol.optimize()
        if symbol is None:
            return None
        return Optional(symbol)

    def __eq__(self, other):
        return isinstance(other, Optional) and self.__dict__ == other.__dict__

    def __str__(self):
        return '(optional, {0})'.format(self.symbol)


class List(Symbol):

    def __init__(self, symbols):
        self.__symbols = symbols

    @property
    def symbols(self):
        return self.__symbols

    @property
    def children(self):
        return self.symbols

    def optimize(self):
        symbols = [s.optimize() for s in self.symbols]
        symbols = [s for s in symbols if s is not None]
        if len(symbols) == 0:
            return None
        if len(symbols) == 1:
            return symbols[0]
        return List(symbols)

    def __eq__(self, other):
        return isinstance(other, List) and self.__dict__ == other.__dict__

    def __str__(self):
        symbols = ' '.join(str(s) for s in self.symbols)
        return '(list {0})'.format(symbols)


class Regex(Symbol):

    def __init__(self, regex):
        assert is_valid_regex(regex)
        self.__regex = regex

    @property
    def regex(self):
        return self.__regex

    @property
    def children(self):
        return []

    def optimize(self):
        return self

    def __eq__(self, other):
        return isinstance(other, Regex) and self.__dict__ == other.__dict__

    def __str__(self):
        return 'regex {0})'.format(self.__regex)


class Or(Symbol):

    def __init__(self, clauses):
        self.__clauses = clauses

    @property
    def clauses(self):
        return self.__clauses

    @property
    def children(self):
        return self.clauses

    def optimize(self):
        clauses = [s.optimize() for s in self.clauses]
        clauses = [s for s in clauses if s is not None]
        if len(clauses) == 0:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return Or(clauses)

    def __eq__(self, other):
        return isinstance(other, Or) and self.__dict__ == other.__dict__

    def __str__(self):
        clauses = ' '.join(str(s) for s in self.clauses)
        return '(or {0})'.format(clauses)

