# -*- coding: utf-8 -*-
"""
Module containing functions for splitting and dividing spans.
"""
from __future__ import unicode_literals, print_function, absolute_import
from .names import START, END
from copy import copy

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


def filter_containing(outer, inner):
    inner_is_list = isinstance(inner, list)

    if not inner_is_list:
        if contains(outer, inner):
            return inner
    else:
        result = [span for span in inner if contains(outer, span)]
        if len(result) > 0:
            return result


def spans(element):
    start = element[START]
    end = element[END]
    if isinstance(start, int):
        return int(start), int(end)
    else:
        return list(zip(start, end))


def first(span):
    start = span[1][0]
    if isinstance(start, list):
        return start[0][0]
    return start


def last(span):
    end = span[1][1]
    if isinstance(end, list):
        return end[-1][1]
    return end


def update_span(element, spans):
    if isinstance(spans, list):
        starts, ends = zip(*spans)
        element = copy(element)
        element[START] = list(starts)
        element[END] = list(ends)
    else:
        element[START] = spans[0]
        element[END] = spans[1]
    return element


def divide_by_spans(elements, outer_spans):
    inner_elems = elements
    outer_spans = [(i, e) for i, e in enumerate(outer_spans)]
    inner_spans = [(i, spans(e)) for i, e in enumerate(inner_elems)]
    bins = [[] for _ in range(len(outer_spans))]
    for iidx, ispan in inner_spans:
        for oidx, ospan in outer_spans:
            filtered = filter_containing(ospan, ispan)
            if filtered is not None:
                elem = update_span(inner_elems[iidx], filtered)
                bins[oidx].append(elem)
    return bins

def divide(elements, by):
    outer_spans = [spans(elem) for elem in by]
    return divide_by_spans(elements, outer_spans)
