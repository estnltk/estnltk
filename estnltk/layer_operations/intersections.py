#
#   Methods for yielding intersecting spans.
#   Ported from:
#    https://github.com/estnltk/estnltk/blob/master/estnltk/single_layer_operations/layer_positions.py
#

from estnltk.text import Layer, SpanList, Span
from typing import MutableMapping, Tuple, Any, Union, List

from sys import maxsize as MAX_INT

def iterate_intersecting_pairs( spanlist:Union[Layer, SpanList] ):
    """ Given a Layer or a SpanList, yields pairwise Spans from its 
        contents that are positionally intersecting.
    """
    yielded = set()
    if isinstance(spanlist, SpanList):
        spl_copy = spanlist.spans[:]       # Shallow copy of the spanlist
    elif isinstance(spanlist, Layer):
        spl_copy = spanlist.spans.spans[:] # Shallow copy of the spanlist
    for i1, elem1 in enumerate(spl_copy):
        for i2, elem2 in enumerate(spl_copy):
            indexes = (i1, i2) if i1 < i2 else (i2, i1)
            if i1 != i2 and elem1.start <= elem2.start < elem1.end:
                if indexes not in yielded:
                    yielded.add(indexes)
                    yield elem1, elem2


def iterate_consecutive_spans(spanlist:Union[List[Span], SpanList], max_gap:int=MAX_INT): 
    '''  Given a SpanList or a List of Spans, yields pairs of Spans that are 
        positionally consecutive. Argument max_gap can be additionally used for 
        defining the maximal allowed gap between end and start of two yielded 
        spans. By default, the max_gap is equal to largest possible value defined 
        by sys.maxsize;
        
         Note that if a List of Spans is given as an input argument, it is sorted 
        before detection of the consecutive spans.
    '''
    if max_gap < 0:
        raise Exception ('(!) Value of max_gap should be positive or zero!')
    # Check the type of input list, and sort the regular spanlist
    if isinstance(spanlist, list) and spanlist:
        if all( [isinstance(span, Span) for span in spanlist] ):
            spanlist = sorted(spanlist)
        else:
            raise Exception (
                '(!) The input list contains unexpected types of elements: ', str(spanlist))
    # Assume that:
    #    1) spans in the list are sorted;
    #    2) if overlapping spans have equal start positions, then 
    #       shorter spans come first
    # Iterate over the list and detect consecutive spans
    spl_enum = list(enumerate(spanlist))
    for span_id, span in spl_enum:
        # Check the following spans
        spans_checked = []
        for span_id_2 in range(span_id + 1, len(spl_enum)):
            following_span = spl_enum[span_id_2][1]
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
    '''  Given a SpanList or a List of Spans, yields pairs of Spans that are 
        positionally touching (i.e. gap between the consecutive spans is 0).
    '''
    yield from iterate_consecutive_spans(spanlist, max_gap=0)
