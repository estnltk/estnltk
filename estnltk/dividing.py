# -*- coding: utf-8 -*-
"""
Module containing functions for splitting and dividing spans.
These are mainly used in :py:class:`~estnltk.text.Text` class split and divide methods.
"""
from __future__ import unicode_literals, print_function, absolute_import
from .names import START, END
from copy import deepcopy


def span_contains_span(outer, inner):
    return outer[0] <= inner[0] and outer[1] >= inner[1]


def span_contains_list(outer, inner):
    return all(span_contains_span(outer, span) for span in inner)


def list_contains_span(outer, inner):
    return any(span_contains_span(span, inner) for span in outer)


def list_contains_list(outer, inner):
    n, m = len(outer), len(inner)
    i, j = 0, 0
    while i < n and j < m:
        (ostart, oend), (istart, iend) = outer[i], inner[j]
        if ostart > istart:
            return False
        if oend >= iend:
            j += 1
        else:
            i += 1
    return j == m


def contains(outer, inner):
    inner_is_list = isinstance(inner, list)
    outer_is_list = isinstance(outer, list)
    if inner_is_list:
        if outer_is_list:
            return list_contains_list(outer, inner)
        return span_contains_list(outer, inner)
    if outer_is_list:
        return list_contains_span(outer, inner)
    return span_contains_span(outer, inner)


def any_filters_span(outer, inner):
    if contains(outer, inner):
        return inner


def span_filters_list(outer, inner):
    filtered = [span for span in inner if span_contains_span(outer, span)]
    if len(filtered) > 0:
        return filtered


def list_filters_list(outer, inner):
    n, m = len(outer), len(inner)
    i, j = 0, 0
    filtered = []
    while i < n and j < m:
        (ostart, oend), (istart, iend) = outer[i], inner[j]
        if ostart > istart:
            j += 1
            continue
        if oend >= iend:
            filtered.append((istart, iend))
            j += 1
        else:
            i += 1
    if len(filtered) > 0:
        return filtered


def span_translates_span(outer, inner):
    if span_contains_span(outer, inner):
        outer_left = outer[0]
        return inner[0]-outer_left, inner[1]-outer_left


def span_translates_list(outer, inner):
    outer_left = outer[0]
    translated = [(span[0]-outer_left, span[1]-outer_left) for span in inner if span_contains_span(outer, span)]
    if len(translated) > 0:
        return translated


def list_translates_span(outer, inner, sep):
    offset = 0
    seplen = len(sep)
    for span in outer:
        if span_contains_span(span, inner):
            outer_left = first(span)
            return inner[0]-outer_left+offset, inner[1]-outer_left+offset
        offset += span[1]-span[0] + seplen


def list_translates_list(outer, inner, sep):
    n, m = len(outer), len(inner)
    i, j = 0, 0
    translated = []
    offset = 0
    seplen = len(sep)
    while i < n and j < m:
        (ostart, oend), (istart, iend) = outer[i], inner[j]
        if ostart > istart:
            j += 1
            continue
        if oend >= iend:
            outer_left = first(outer[i])
            translated.append((istart-outer_left+offset, iend-outer_left+offset))
            j += 1
        else:
            offset += oend - ostart + seplen
            i += 1
    if len(translated) > 0:
        return translated


def filter_containing(outer, inner, translate=False, sep=' '):
    inner_is_list = isinstance(inner, list)
    outer_is_list = isinstance(outer, list)

    if translate:
        if inner_is_list:
            if outer_is_list:
                return list_translates_list(outer, inner, sep)
            return span_translates_list(outer, inner)
        if outer_is_list:
            return list_translates_span(outer, inner, sep)
        return span_translates_span(outer, inner)
    if inner_is_list:
        if outer_is_list:
            return list_filters_list(outer, inner)
        return span_filters_list(outer, inner)
    return any_filters_span(outer, inner)


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


def spans_collect_spans(outer_spans, inner_spans):
    n, m = len(outer_spans), len(inner_spans)
    i, j = 0, 0
    current_bin = []
    nyielded = 0
    while i < n and j < m:
        (ostart, oend), (istart, iend) = outer_spans[i], inner_spans[j]
        if ostart > istart:
            j += 1
            continue
        if oend >= iend:
            current_bin.append(j)
            j += 1
        else:
            yield current_bin
            nyielded += 1
            current_bin = []
            i += 1
    # yield the last (possibly) half-filled bin
    if nyielded < n:
        yield current_bin
        nyielded += 1
    # yield empty bins
    while nyielded < n:
        yield []
        nyielded += 1


def unique(iterable):
    seen = set()
    for e in iterable:
        if e not in seen:
            yield e
            seen.add(e)


def spans_collect_lists(outer_spans, inner_spans):
    mapping = []
    flattened_spans = []
    for idx, spans in enumerate(inner_spans):
        for s in spans:
            flattened_spans.append(s)
            mapping.append(idx)
    flattened_spans, mapping = zip(*sorted(zip(flattened_spans, mapping)))
    for bin in spans_collect_spans(outer_spans, flattened_spans):
        yield unique(mapping[idx] for idx in bin)


def lists_collect_spans(outer_spans, inner_spans):
    mapping = []
    flattened_spans = []
    for idx, spans in enumerate(outer_spans):
        for s in spans:
            flattened_spans.append(s)
            mapping.append(idx)
    flattened_spans, mapping = zip(*sorted(zip(flattened_spans, mapping)))
    flat_bins = list(spans_collect_spans(flattened_spans, inner_spans))
    bins = [[] for _ in range(len(outer_spans))]
    for flatidx, flatbin in enumerate(flat_bins):
        binidx = mapping[flatidx]
        bins[binidx].extend(flatbin)
    for bin in bins:
        yield unique(bin)


def lists_collect_lists(outer_spans, inner_spans):
    mapping = []
    flattened_spans = []
    for idx, spans in enumerate(outer_spans):
        for s in spans:
            flattened_spans.append(s)
            mapping.append(idx)
    flattened_spans, mapping = zip(*sorted(zip(flattened_spans, mapping)))
    flat_bins = list(spans_collect_lists(flattened_spans, inner_spans))
    bins = [[] for _ in range(len(outer_spans))]
    for flatidx, flatbin in enumerate(flat_bins):
        binidx = mapping[flatidx]
        bins[binidx].extend(flatbin)
    for bin in bins:
        yield unique(bin)


def get_bins(outer_spans, inner_spans):
    outers_are_lists = isinstance(outer_spans[0], list)
    inners_are_lists = isinstance(inner_spans[0], list)
    if outers_are_lists:
        if inners_are_lists:
            return lists_collect_lists(outer_spans, inner_spans)
        return lists_collect_spans(outer_spans, inner_spans)
    else:
        if inners_are_lists:
            return spans_collect_lists(outer_spans, inner_spans)
        return spans_collect_spans(outer_spans, inner_spans)


def get_filterer(outer_spans, inner_spans, translate, sep):
    outers_are_lists = isinstance(outer_spans[0], list)
    inners_are_lists = isinstance(inner_spans[0], list)

    if translate:
        if inners_are_lists:
            if outers_are_lists:
                return lambda outer, inner: list_translates_list(outer, inner, sep)
            return lambda outer, inner: span_translates_list(outer, inner)
        if outers_are_lists:
            return lambda outer, inner: list_translates_span(outer, inner, sep)
        return lambda outer, inner: span_translates_span(outer, inner)
    if inners_are_lists:
        if outers_are_lists:
            return lambda outer, inner: list_filters_list(outer, inner)
        return lambda outer, inner: span_filters_list(outer, inner)
    return lambda outer, inner: any_filters_span(outer, inner)


def divide_by_spans(elements, outer_spans, translate=False, sep=' '):
    outer_spans = [convert_span(s) for s in outer_spans]
    inner_spans = [spans(e) for e in elements]
    if len(inner_spans) == 0:
        return [[] for _ in range(len(outer_spans))]
    if len(outer_spans) == 0:
        return []
    inners_are_lists = isinstance(inner_spans[0], list)
    filterer = get_filterer(outer_spans, inner_spans, translate, sep)
    bins = []
    for binidx, collection in enumerate(get_bins(outer_spans, inner_spans)):
        outer = outer_spans[binidx]
        bin = []
        for elemidx in collection:
            elem = elements[elemidx]
            filtered = filterer(outer, inner_spans[elemidx])
            if filtered is not None:
                if inners_are_lists or translate:
                    elem = deepcopy(elem)
                elem = update_span(elem, filtered)
                bin.append(elem)
        bins.append(bin)
    return bins


def divide_by_spans_old_inefficient(elements, outer_spans, translate=False, sep=' '):
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
        This is required in order to tag correct start, end positions of elements.
    """
    outer_spans = [spans(elem) for elem in by]
    return divide_by_spans(elements, outer_spans, translate=translate, sep=sep)
