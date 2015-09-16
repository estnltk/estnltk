# -*- coding: utf-8 -*-
"""This module defines Match objects."""
from __future__ import unicode_literals, print_function, absolute_import

from copy import copy

NAME = 'name'
START = 'start'
END = 'end'
MATCHES = 'matches'
TEXT = 'text'


class Match(dict):
    """Match of a grammar symbol."""

    def __init__(self, start, end, text, name=None):
        super(Match, self).__init__()
        self[START] = int(start)
        self[END] = int(end)
        self[TEXT] = text
        self[MATCHES] = {}
        assert self[START] <= self[END]
        assert len(text) == end - start
        if name is not None:
            self[NAME] = name

    @property
    def name(self):
        """The name of the match."""
        return self.get(NAME, None)

    @property
    def start(self):
        """The start position of the match."""
        return self[START]

    @property
    def end(self):
        """The end position of the match."""
        return self[END]

    @property
    def text(self):
        """Matched text."""
        return self[TEXT]

    @property
    def matches(self):
        """Matches of child symbols."""
        return self[MATCHES]

    @property
    def dict(self):
        """Dictionary representing this match and all child symbol matches."""
        res = copy(self)
        if MATCHES in res:
            del res[MATCHES]
        if NAME in res:
            del res[NAME]
        res = {self.name: res}
        for k, v in self.matches.items():
            res[k] = v
            if NAME in res[k]:
                del res[k][NAME]
        return res

    def is_before(self, other):
        return self.end <= other.start

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __len__(self):
        return self.end - self.start

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def concatenate_matches(a, b, text, name):
    """Concatenate matches a and b.
    All submatches will be copied to result."""
    match = Match(a.start, b.end, text[a.start:b.end], name)
    for k, v in a.matches.items():
        match.matches[k] = v
    for k, v in b.matches.items():
        match.matches[k] = v
    if a.name is not None:
        aa = copy(a)
        del aa[MATCHES]
        match.matches[a.name] = aa
    if b.name is not None:
        bb = copy(b)
        del bb[MATCHES]
        match.matches[b.name] = bb
    return match


def copy_rename(match, name):
    m = copy(match)
    m[NAME] = name
    return m


def intersect(lefts, rights):
    n, m = len(lefts), len(rights)
    i, j = 0, 0
    result = []
    while i < n and j < m:
        left = lefts[i]
        right = rights[j]
        if left.start == right.start and left.end == right.end:
            i += 1
            j += 1
            result.append(left)
        elif left < right:
            i += 1
        else:
            j += 1
    return result
