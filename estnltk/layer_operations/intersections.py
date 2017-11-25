#
#   Methods for yielding intersecting spans.
#

from estnltk.text import Layer, SpanList, Span
from typing import MutableMapping, Tuple, Any, Union, List

def iterate_intersecting_pairs( spanlist:Union[List[Span], SpanList] ):
    """ Given a Layer or a SpanList, yields pairwise Spans from its 
        contents that are positionally intersecting.
        
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
                yield span, following_span
            elif span.end < following_span.start:
                # Under the assumption that the list is sorted,
                # there is no need to look further
                break
