# -*- coding: utf-8 -*-
"""
Module containing functions for splitting and dividing spans.
These are mainly used in :py:class:`~estnltk.text.Text` class split and divide methods.
"""
from __future__ import unicode_literals, print_function, absolute_import
from .names import START, END
from copy import deepcopy


def contains(outer, inner):
    """Check if outer span contains the inner span."""
    outer_is_list = isinstance(outer, list)
    inner_is_list = isinstance(inner, list)

    if outer_is_list:
        if inner_is_list:
            return all(contains(outer, span) for span in inner)
        else:
            return any(contains(span, inner) for span in outer)
    else:
        ostart, oend = outer
        if inner_is_list:
            return all(contains(outer, span) for span in inner)
        else:
            istart, iend = inner
            return ostart <= istart and iend <= oend


def filter_containing(outer, inner, translate=False, sep=' '):
    inner_is_list = isinstance(inner, list)
    outer_is_list = isinstance(outer, list)
    seplen = len(sep)

    if not inner_is_list:
        if translate:
            # if we need to translate positions, find the outer span that matches the inner span
            if outer_is_list:
                offset = 0
                for span in outer:
                    if contains(span, inner):
                        outer_left = first(span)
                        return inner[0]-outer_left+offset, inner[1]-outer_left+offset
                    offset += span[1]-span[0] + seplen
            else:
                if contains(outer, inner):
                    outer_left = first(outer)
                    return inner[0]-outer_left, inner[1]-outer_left
        else:
            if contains(outer, inner):
                return inner
    else:
        if translate:
            if outer_is_list:
                result = []
                for ispan in inner:
                    offset = 0
                    for ospan in outer:
                        if contains(ospan, ispan):
                            outer_left = first(ospan)
                            result.append((ispan[0]-outer_left+offset, ispan[1]-outer_left+offset))
                            break
                        offset += ospan[1]-ospan[0] + seplen
            else:
                outer_left = first(outer)
                result = [(span[0]-outer_left, span[1]-outer_left) for span in inner if contains(outer, span)]
        else:
            result = [span for span in inner if contains(outer, span)]
        if len(result) > 0:
            return result


def spans(element):
    start = element[START]
    end = element[END]
    return convert_span((start, end))


def convert_span(span):
    # should be already in correct format
    if isinstance(span, list):
        return span
    # otherwise detect, if it is a simple span or multispan
    start, end = span
    if isinstance(start, int):
        return int(start), int(end)
    else:
        return list(zip(start, end))


def first(span):
    if isinstance(span, list):
        return span[0][0]
    return span[0]


def last(span):
    if isinstance(span, list):
        return span[-1][1]
    return span[1]


def update_span(element, spans):
    if isinstance(spans, list):
        starts, ends = zip(*spans)
        element[START] = list(starts)
        element[END] = list(ends)
    else:
        element[START] = spans[0]
        element[END] = spans[1]
    return element


def divide_by_spans(elements, outer_spans, translate=False, sep=' '):
    inner_elems = elements
    outer_spans = [(i, convert_span(e)) for i, e in enumerate(outer_spans)]
    inner_spans = [(i, spans(e)) for i, e in enumerate(inner_elems)]
    bins = [[] for _ in range(len(outer_spans))]
    for iidx, ispan in inner_spans:
        for oidx, ospan in outer_spans:
            filtered = filter_containing(ospan, ispan, translate, sep)
            if filtered is not None:
                elem = inner_elems[iidx]
                if isinstance(ispan, list) or translate:
                    elem = deepcopy(elem)
                elem = update_span(elem, filtered)
                bins[oidx].append(elem)
    return bins


def divide(elements, by, translate=False, sep=' '):
    """Divide lists `elements` and `by`.
    All elements are grouped into N bins, where N denotes the elements in `by` list.

    Parameters
    ----------
    elements: list of dict
        Elements to be grouped into bins.
    by: list of dict
        Elements defining the bins.
    translate: bool (default: False)
        When dividing, also translate start and end positions of elements.
    sep: str (default ' ')
        In case of multispans, what is the default text separator.
        This is required in order to compute correct start, end positions of elements.
    """
    outer_spans = [spans(elem) for elem in by]
    return divide_by_spans(elements, outer_spans, translate=translate, sep=sep)
