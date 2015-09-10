# -*- coding: utf-8 -*-
"""This module defines functions to tag plain texts with <mark> annotations."""
from __future__ import unicode_literals, print_function, absolute_import

from ..core import as_unicode
from ..names import TEXT, START, END
from .templates import htmlescape, get_opening_mark, CLOSING_MARK
from .extractors import texts_simple, texts_multi


class Tag(object):

    def __init__(self, pos, is_opening_tag, css_class):
        """Create a Tag object.

        Parameters
        ----------
        pos: int
            The position of the tag relative to text.
        is_opening_tag: bool
            Defines whether this tag is an opening or closing tag (<mark> or </mark>).
        css_class: str
            The css class associated with the tag. Although closing tags are not needed in the result,
            we need this during computations.
        """
        self.pos = int(pos)
        self.is_opening_tag = bool(is_opening_tag)
        self.css_class = as_unicode(css_class)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        # tags that appear before relative to text come first
        if self.pos < other.pos:
            return True
        if self.pos == other.pos:
            # end tags should come before opening tags
            if self.is_opening_tag > other.is_opening_tag:
                return True
            # otherwise, tags should be sorted by css_class name
            if self.is_opening_tag == other.is_opening_tag:
                return self.css_class < other.css_class
        return False

    def __repr__(self):
        return '({0}, {1}, {2})'.format(self.pos, self.is_opening_tag, self.css_class)


def create_tags(start, end, css_class):
    start_tag = Tag(start, True, css_class)
    end_tag = Tag(end, False, css_class)
    return start_tag, end_tag


def create_tags_for_layer(text, layer, rules):
    # decide which extractor to use
    # first just assume we need to use a multi layer text extractor
    extractor = lambda t: texts_multi(t, layer)
    # if user has specified his/her own callable, use it
    if hasattr(layer, '__call__'):
        extractor = layer
    elif text.is_simple(layer):
        # the given layer is simple, so use simple text extractor
        extractor = lambda t: texts_simple(t, layer)
    tags = []
    for elem in extractor(text):
        css_class = rules.get_css_class(elem[TEXT])
        if css_class is not None:
            start_tag, end_tag = create_tags(elem[START], elem[END], css_class)
            tags.append(start_tag)
            tags.append(end_tag)
    return tags


def group_tags_at_same_position(tags):
    last_pos = 0
    group = []
    for tag in tags:
        if tag.pos == last_pos:
            group.append(tag)
        else:
            yield last_pos, group
            group = [tag]
            last_pos = tag.pos
    if len(group) > 0:
        yield last_pos, group


def get_opening_closing_tags(group):
    opening, closing = [], []
    for tag in group:
        if tag.is_opening_tag:
            opening.append(tag)
        else:
            closing.append(tag)
    return opening, closing


def create_tags_with_concatenated_css_classes(tags):
    """Function that creates <mark> tags such that they are not overlapping.
    In order to do this, it concatenates the css classes and stores the concatenated
    result in new tags.
    """
    current_classes = set()
    result = []
    for pos, group in group_tags_at_same_position(tags):
        opening, closing = get_opening_closing_tags(group)
        # handle closing tags at current position
        closing_added = False
        if len(closing) > 0:
            closing_tag = Tag(pos, False, '')
            for tag in closing:
                current_classes.remove(tag.css_class)
            result.append(closing_tag)
            closing_added = True
        # handle opening tags at current position
        opening_added = False
        if len(opening) > 0:
            # handle the begin of an overlap
            if not closing_added and len(current_classes) > 0:
                result.append(Tag(pos, False, ''))
            for tag in opening:
                current_classes.add(tag.css_class)
            opening_tag = Tag(pos, True, ' '.join(sorted(current_classes)))
            result.append(opening_tag)
            opening_added = True
        # handle the end of an overlap
        if closing_added and not opening_added and len(current_classes) > 0:
            opening_tag = Tag(pos, True, ' '.join(sorted(current_classes)))
            result.append(opening_tag)
    return result


def create_tags_for_text(text, aesthetics, rules):
    tags = []
    for aes, layer in aesthetics.items():
        tags.extend(create_tags_for_layer(text, layer, rules[aes]))
    return create_tags_with_concatenated_css_classes(sorted(tags))


def mark_text(text, aesthetics, rules):
    tags = create_tags_for_text(text, aesthetics, rules)
    spans = []
    last_pos = 0
    for tag in tags:
        spans.append(htmlescape(text.text[last_pos:tag.pos]))
        last_pos = tag.pos
        if tag.is_opening_tag:
            spans.append(get_opening_mark(tag.css_class))
        else:
            spans.append(CLOSING_MARK)
    if last_pos < len(text.text):
        spans.append(htmlescape(text.text[last_pos:]))
    return ''.join(spans)
