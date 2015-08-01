# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .common import htmlescape


class Match(object):
    """
    Match object describes text spans matched by symbols in the grammar.

    Attributes
    ----------
    name: str
        The name of the matched element.
    start: int
        The starting position of the match of this element.
    end: int
        The ending position of the match of this element.
    chain_end: int
        The ending position of this match and following matches.
    content: str
        The matched string.
    sub_match: Match
        First submatch within this match. Usually the first matched child in the production.
    next_match: Match
        Match following this match and is out of this match.
    """

    def __init__(self, name, start, end, content, sub_match=None, next_match=None):
        self.name = name
        self.start = start
        self.end = end
        self.chain_end = end
        self.content = content
        self.chain_content = content
        self.sub_match = sub_match
        self.next_match = next_match

    @staticmethod
    def encapsulate(name, match):
        """Encapsulate a submatch."""
        return Match(name, match.start, match.chain_end, match.chain_content, match)

    def link(self, match):
        """Link this match with a next match.
        Note that this method assumes that the chain_end attribute of the linked
        match is already updated correctly.
        """
        self.next_match = match
        self.chain_end = match.chain_end
        self.chain_content += match.chain_content
        return self

    def to_list(self):
        sub_match = None
        if self.sub_match is not None:
            sub_match = self.sub_match.to_list()
        next_match = []
        if self.next_match is not None:
            next_match = self.next_match.to_list()
        return [(self.name, self.start, self.end, self.content, sub_match)] + next_match

    def groups(self, grps=None):
        """Return a dictionary of matched groups."""
        if grps is None:
            grps = {}
        if not self.name.startswith('__'):
            grps[self.name] = {'start': self.start,
                               'end': self.end,
                               'name': self.name,
                               'content': self.content}
        if self.sub_match is not None:
            self.sub_match.groups(grps)
        if self.next_match is not None:
            self.next_match.groups(grps)
        return grps

    def grouptree(self, clear_offsets=False, offset=0):
        """Return a hierarchial tree of matched groups.

        Parameters
        ----------
        clear_offsets: boolean
            If True, then return the offsets as if the match starts from position given by offset parameter.
        offset: int
            If clear_offsets is True, then use this value to correct the offset (NB! used internally by the efunction)
        """
        if clear_offsets:
            offset = -self.start
        grp = None
        if self.sub_match is not None:
            grp = []
            for elem in self.sub_match.grouptree(offset=offset):
                if isinstance(elem, list) and len(elem) == 1:
                    grp.append(elem[0])
                else:
                    grp.append(elem)
        if not self.name.startswith('__'):
            grp = {'name': self.name,
                   'start': self.start+offset,
                   'end': self.end+offset,
                   'content': self.content,
                   'submatch': grp}
            if grp['submatch'] is None:
                del grp['submatch']
        next_match = []
        if self.next_match is not None:
            next_match = self.next_match.grouptree(offset=offset)
        if grp is not None:
            return [grp] + next_match
        return next_match

    def canonical_form(self):
        """Return the hierarchy of matched symbols.
        This is useful to estimate the precision of the matches."""
        def filter_tree(tree):
            if isinstance(tree, list):
                return ' + '.join([filter_tree(subtree) for subtree in tree])
            if 'submatch' in tree:
                return '{0} ({1})'.format(tree['name'], ' + '.join([filter_tree(subtree) for subtree in tree['submatch']]))
            else:
                return tree['name']
        return filter_tree(self.grouptree()[0])

    def is_before(self, match):
        return self.end <= match.start

    @property
    def length(self):
        return self.end - self.start

    def __repr__(self):
        return repr((self.name, self.start, self.end, self.content))

    def groups_html(self):
        groups = self.groups()
        offset = groups[self.name]['start']
        groups = groups.values()
        groups.sort(key=lambda grp: (grp['start'], -grp['end']))

        rows = []
        for group in groups:
            left = '&nbsp;'*(group['start']-offset) + htmlescape(group['content'])
            middle = '&nbsp;&#x2015;&nbsp;'
            right = htmlescape(group['name'])
            row = '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(left, middle, right)
            rows.append(row)
        return '<div><table class="grouptable">{0}</table></div>'.format(''.join(rows))