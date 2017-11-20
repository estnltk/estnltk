#
#   Methods for yielding intersecting spans.
#   Ported from:
#    https://github.com/estnltk/estnltk/blob/master/estnltk/single_layer_operations/layer_positions.py
#

from estnltk.text import Layer, SpanList, Span
from typing import MutableMapping, Tuple, Any, Union, List


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

