#
#   Functions for yielding consecutive spans.
#

from estnltk.text import Layer, SpanList, Span
from typing import MutableMapping, Tuple, Any, Union, List


def iterate_consecutive_spans(spanlist:Union[List[Span], SpanList], max_gap:int=float('inf')):
    """  Given a SpanList or a List of Spans, yields pairs of Spans that are 
        positionally consecutive. Consecutive means that there can be a gap (in 
        size of max_gap) between the two spans, but none of the other spans may 
        fall entirely between the two consecutive spans.

        Argument max_gap can be additionally used for defining the maximal allowed 
        gap between end and start of two yielded spans. By default, the max_gap 
        is equal to the value defined by constant sys.maxsize;
        
         Note that if a List of Spans is given as an input argument, it is sorted 
        before detection of the consecutive spans.
    """
    if max_gap < 0:
        raise Exception('(!) Value of max_gap should be positive int or zero!')
    # Check the type of input list, and sort the regular spanlist
    if isinstance(spanlist, list) and spanlist:
        if all( [isinstance(span, Span) for span in spanlist]):
            spanlist = sorted(spanlist)
        else:
            raise Exception(
                '(!) The input list contains unexpected types of elements: ', str(spanlist))
    # Assume that:
    #    1) spans in the list are sorted;
    #    2) if overlapping spans have equal start positions, then 
    #       shorter spans come first
    # Iterate over the list and detect consecutive spans
    for span_id, span in enumerate(spanlist):
        # Check the following spans
        spans_checked = []
        for span_id_2 in range(span_id + 1, len(spanlist)):
            following_span = spanlist[span_id_2]
            if 0 <= following_span.start - span.end <= max_gap:
                if not spans_checked:
                    # No span between the two spans
                    yield (span, following_span)
                else:
                    # Check for spans falling inside the gap 
                    falls_in_gap = False
                    for checked_span in spans_checked:
                        if span.end <= checked_span.start and \
                           checked_span.end <= following_span.start:
                            falls_in_gap = True
                            break
                    if falls_in_gap:
                        # If any of the checked spans falls entirely 
                        # between this span and the following span, 
                        # then we have already exhausted the consecutive
                        # spans -- break the cycle
                        break
                    else:
                        # Checked spans do not fall entirely between
                        # this span and the following span: yield the
                        # following span
                        yield (span, following_span)
                spans_checked.append(following_span)


def iterate_touching_spans(spanlist:Union[List[Span], SpanList]):
    """ Given a SpanList or a List of Spans, yields pairs of Spans that are 
        positionally touching (i.e. gap between the consecutive spans is 0).
    """
    yield from iterate_consecutive_spans(spanlist, max_gap=0)


def iterate_hovering_spans(spanlist:Union[List[Span], SpanList],
                           min_gap:int=1,
                           max_gap:int=float('inf')):
    """ Given a SpanList or a List of Spans, yields pairs of Spans that are 
        positionally hovering, i.e. gap between the consecutive spans is at 
        least 1. 
        
        Arguments min_gap and max_gap can be additionally used for 
        constraining the minimal and maximal allowed gap between the yielded 
        spans. Note that it is required that 0 < min_gap <= max_gap;
    """
    if min_gap < 1:
        raise Exception('(!) Value of min_gap should be an integer > 0!')
    if max_gap < 1:
        raise Exception('(!) Value of max_gap should be an integer > 0!')
    if not (min_gap <= max_gap):
        raise Exception('(!) Value of min_gap should be <= max_gap!')
    for (span, following_span) in iterate_consecutive_spans(spanlist, max_gap=max_gap):
        if min_gap <= (following_span.start - span.end) <= max_gap:
            yield (span, following_span)


def iterate_starting_spans(spanlist):
    """
    yield all spans that have no strictly preceding spans
    """
    min_end = float('inf')
    for span in spanlist:
        min_end = min(span.end, min_end)
        if span.start < min_end:
            yield span
        else:
            return


def iterate_ending_spans(spanlist):
    """
    yield all spans that have no strictly succeeding spans
    """
    if isinstance(spanlist, list) and spanlist:
        if all([isinstance(span, Span) for span in spanlist]):
            spanlist = sorted(spanlist)
        else:
            raise Exception(
                'the input list contains unexpected types of elements: ', str(spanlist))
    if spanlist:
        max_start = spanlist[-1].start
        yield from (span for span in spanlist if span.end > max_start)

