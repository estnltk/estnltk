# -*- coding: utf-8 -*-
"""
This module contains functions for parsing and working with productions.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .exceptions import ParseException


def tokenize(line, lineno=0):
    """Tokenize a string describing a production.

    Parameters
    ----------
    line: str
        A single line containing the production.
    lineno: int (default: 0)
        The line number of the production, in case the production is parsed
        from a larger grammar.

    Returns
    -------
    list
    """
    tokens = []
    token = ''
    i = 0
    while i < len(line):
        c = line[i]
        if c in ' ()?|':
            if len(token) > 0:
                tokens.append(token)
                token = ''
            if c != ' ':
                tokens.append(c)
            i += 1
        elif c == "'":
            j = i+1
            found = False
            while j < len(line):
                if line[j] == "'":
                    found = True
                    tokens.append(line[i:j+1])
                    i = j+1
                    break
                j += 1
            if not found:
                raise ParseException('Could not find regex end on line {0}'.format(lineno))
        else:
            token += c
            i += 1
    if len(token) > 0:
        tokens.append(token)
    return tokens

