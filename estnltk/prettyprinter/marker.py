# -*- coding: utf-8 -*-
"""This module defines functions to tag plain texts with <mark> annotations."""
from __future__ import unicode_literals, print_function, absolute_import

from ..core import as_unicode
from ..names import START, END
from .templates import htmlescape, get_opening_mark, CLOSING_MARK


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
            if self.is_opening_tag > other.start_tag:
                return True
            # otherwise, tags should be sorted by css_class name
            if self.is_opening_tag == other.start_tag:
                return self.css_class < other.css_class
        return False


def create_tags(start, end, css_class):
    start_tag = Tag(start, True, css_class)
    end_tag = Tag(end, False, css_class)
    return start_tag, end_tag


def create_tags_for_simple_layer(elems, css_class):
    tags = []
    for elem in elems:
        start_tag, end_tag = create_tags(elem[START], elem[END], css_class)
        tags.append(start_tag)
        tags.append(end_tag)
    return tags


def create_tags_for_multi_layer(elems, css_class):
    tags = []
    for elem in elems:
        for start, end in zip(elem[START], elem[END]):
            start_tag, end_tag = create_tags(start, end, css_class)
            tags.append(start_tag)
            tags.append(end_tag)
    return tags


def create_tags_for_layer(text, layer, css_class):
    if text.is_simple(layer):
        return create_tags_for_simple_layer(text[layer], css_class)
    return create_tags_for_multi_layer(text[layer], css_class)


def group_tags_at_same_position(tags):
    last_pos = 0
    group = []
    for tag in tags:
        if tag.pos == last_pos:
            group.append(tag)
        else:
            yield group
            group = [tag]
    if len(group) > 0:
        yield group


def create_tags_with_concatenated_css_classes(tags):
    """Function that creates <mark> tags such that they are not overlapping.
    In order to do this, it concatenates the css classes and stores the concatenated
    result in new tags.
    """
    current_classes = set()
    result = []
    for group in group_tags_at_same_position(tags):
        opening, closing = [], []
        for tag in group:
            if tag.is_opening_tag:
                opening.append(tag)
            else:
                closing.append(tag)
        if len(closing) > 0:
            # ' '.join is not really needed here, but we use it for consistency of Tag information.
            closing_tag = Tag(tag.pos, False, ' '.join(sorted(current_classes)))
            for tag in closing:
                current_classes.remove(tag.css_class)
            result.append(closing_tag)
        if len(opening) > 0:
            for tag in opening:
                current_classes.add(tag.css_class)
            opening_tag = Tag(tag.pos, True, ' '.join(sorted(current_classes)))
            result.append(opening_tag)
    return result


def create_tags_for_text(text, aesthetics):
    tags = []
    for aes, layer in aesthetics.items():
        tags.extend(create_tags_for_layer(text, layer, aes))
    return create_tags_with_concatenated_css_classes(sorted(tags))


def mark_text(text, aesthetics):
    tags = create_tags_for_text(text, aesthetics)
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
