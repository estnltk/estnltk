#
#   Functions for yielding intersecting spans.
#

from typing import Union, List

from estnltk_core import SpanList, Span
from estnltk_core.layer.span_operations import nested


def iterate_intersecting_spans(spanlist: Union[List[Span], SpanList],
                               yield_nested: bool=True,
                               yield_equal: bool=True,
                               yield_overlapped: bool=True):
    """ Given a Layer or a SpanList, yields pairs of Spans that are 
        positionally intersecting.
        
        If the yield_nested = True (default), then pairs of Spans 
        where one span is nested inside other are included.
        If the yield_equal = True (default), then pairs of Spans 
        where one span is positionally equal to another are 
        included.
        If the yield_overlapped = True (default), then pairs of 
        Spans where one span partially overlaps another are 
        included.
        
        Note that if a List of Spans is given as an input argument, it 
        is sorted before detection of the consecutive spans.
    """
    # Check the type of input list, and sort the regular spanlist
    if isinstance(spanlist, list) and spanlist:
        if all( [isinstance(span, Span) for span in spanlist] ):
            spanlist = sorted(spanlist)
        else:
            raise Exception (
                '(!) The input list contains unexpected types of elements: ', str(spanlist))
    # Iterate over the list and detect consecutive spans
    spl_enum = list(enumerate(spanlist))
    for span_id, span in spl_enum:
        # Check the following spans
        for span_id_2 in range(span_id + 1, len(spl_enum)):
            following_span = spl_enum[span_id_2][1]
            if span.start <= following_span.start < span.end:
                # Check for nestings
                following_nested = nested(span, following_span)
                this_nested = nested(following_span, span)
                # Yield nested, equal, overlapped or all of them (default)
                if yield_nested and (following_nested or this_nested) and \
                                not (following_nested and this_nested):
                    yield span, following_span
                if yield_equal and following_nested and this_nested:
                    yield span, following_span
                if yield_overlapped and not (following_nested or this_nested):
                    # If there is no nesting, there must be an overlap
                    yield span, following_span
            elif span.end < following_span.start:
                # Under the assumption that the list is sorted,
                # there is no need to look further
                break


#  -------------  Shortcut functions

def iterate_nested_spans( spanlist:Union[List[Span], SpanList] ):
    """ Given a Layer or a SpanList, yields pairs of Spans 
        where one Span is nested inside other. 
        
        Note that pairs of Spans are yielded in the order of their 
        positions, regardless which Span is nesting and which
        is being nested inside other;
    """
    yield from iterate_intersecting_spans( spanlist, yield_nested=True, yield_equal=False, yield_overlapped=False )


def iterate_overlapping_spans( spanlist:Union[List[Span], SpanList] ):
    """ Given a Layer or a SpanList, yields pairs of Spans 
        where one Span is partially overlapped by other.
    """
    yield from iterate_intersecting_spans( spanlist, yield_nested=False, yield_equal=False, yield_overlapped=True )

