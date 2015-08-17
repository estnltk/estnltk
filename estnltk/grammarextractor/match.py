# -*- coding: utf-8 -*-
"""This module defines Match objects."""
from __future__ import unicode_literals, print_function, absolute_import

from copy import copy

NAME = 'name'
START = 'start'
END = 'end'
MATCHES = 'groups'
TEXT = 'text'


class Match(dict):

    def __init__(self, start, end, name=None):
        super(Match, self).__init__()
        self[START] = int(start)
        self[END] = int(end)
        self[MATCHES] = {}
        assert self[START] < self[END]
        if name is not None:
            self[NAME] = name

    @property
    def name(self):
        return self.get(NAME, None)

    @property
    def start(self):
        return self[START]

    @property
    def end(self):
        return self[END]

    @property
    def matches(self):
        return self[MATCHES]

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __repr__(self):
        return repr((self.start, self.end, self.name, self.matches))


def concatenate_matches(a, b, name):
    match = Match(a.start, b.end, name)
    for k, v in a.matches:
        match.matches[k] = v
    for k, v in b.matches:
        match.matches[k] = v
    if a.name is not None:
        match.matches[a.name] = a
    if b.name is not None:
        match.matces[b.name] = b
    return match


def copy_rename(match, name):
    m = copy(match)
    m[NAME] = name
    return m
