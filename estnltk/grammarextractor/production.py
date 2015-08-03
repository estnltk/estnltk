# -*- coding: utf-8 -*-
"""
This module contains functions for parsing and working with productions.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .symbols import Name, Or, List, Regex, Optional

from .exceptions import ParseException


def tokenize(line, lineno=0):
    """Tokenize a string describing a production.

    Example
    -------
    a_symbol|(b_symbol 'optional_regex'? c_symbol)

    will be tokenized as

    ['a_symbol', '|', '(', 'b_symbol', "'optional_regex'", '?', 'c_symbol', ')']

    Parameters
    ----------
    line: str
        A single line containing the production.
    lineno: int (default: 0)
        The line number of the production, in case the production is parsed
        from a larger grammar.

    Returns
    -------
    list of str
        List of tokens.
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


def divide_to_buckets(elements):
    buckets = []
    cur_bucket = []
    for elem in elements:
        if elem == '|':
            buckets.append(cur_bucket)
            cur_bucket = []
        else:
            cur_bucket.append(elem)
    if len(cur_bucket) > 0:
        buckets.append(cur_bucket)
    return buckets


def symbol_from_list_stack(stack, lineno):
    """If stack has any | tokens, it will be transformed to a Or,
    otherwise List."""
    buckets = divide_to_buckets(stack)
    if len(buckets) > 1:
        buckets = [List(b) for b in buckets]
        return Or(buckets)
    elif len(buckets) == 1:
        return List(buckets[0])
    raise ParseException('Invalid/empty production on line {0}'.format(lineno))


def parse_tokens(tokens, lineno=0):
    """Parse a production.

    Parameters
    ----------
    tokens: list of str
        The tokens of the production.
    lineno: int
        The line number the production is in source code.

    Returns
    -------
    list of Symbol
    """
    stack = []
    for token in tokens:
        if token == '(':
            stack.append(token)
        elif token == ')':
            found = False
            for pos, stackelem in reversed(list(enumerate(stack))):
                if stackelem == '(':
                    elem = symbol_from_list_stack(stack[pos+1:], lineno)
                    stack = stack[:pos]
                    stack.append(elem)
                    found = True
                    break
            if not found:
                raise ParseException('Could not match parenthesis on line {0}'.format(lineno))
        elif token == '?':
            if len(stack) > 0 and isinstance(stack[-1], Optional):
                raise ParseException('Double ?? in production on line {0}'.format(lineno))
            stack.append(Optional(stack.pop()))
        elif token == '|':
            stack.append('|')
        elif token.startswith("'"):
            stack.append(Regex(token[1:-1]))
        else:
            stack.append(Name(token))
    if '(' in stack:
        raise ParseException('Unbalanced parenthesis on line {0}'.format(lineno))
    root = symbol_from_list_stack(stack, lineno)
    return root.optimize()


def parse(production, lineno=0):
    return parse_tokens(tokenize(production), lineno)
