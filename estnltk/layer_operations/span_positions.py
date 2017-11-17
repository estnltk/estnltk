#
#   Predicates for testing Span's positions with respect to each other
#   ( work in progress )
#

from typing import MutableMapping, Tuple, Any, Union, List

from estnltk.text import SpanList, Span

#
#  Note: following layer operations are ported from:
#     https://github.com/estnltk/estnltk/blob/master/estnltk/single_layer_operations/layer_positions.py
# 

def touching_right(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    """ 
    Tests if Span y is touching Span x from the right.
    Pictorial example:
    xxxxxxxx
            yyyyy
    """
    return x.end == y.start

def touching_left(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    """ 
    Tests if Span y is touching Span x from the left.
    Pictorial example:
         xxxxxxxx
    yyyyy
    """
    return touching_right(y, x)

def hovering_right(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    """
    Tests if Span y is hovering right from the Span x.
    Pictorial example:
    xxxxxxxx
              yyyyy
    """
    return x.end < y.start

def hovering_left(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    """
    Tests if Span y is hovering left from the Span x.
    Pictorial example:
            xxxxxxxx
    yyyyy
    """
    return hovering_right(y, x)

def right(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    '''
    Tests if Span y is either touching or hovering right with respect to span x.
    '''
    return touching_right(x, y) or hovering_right(x, y)

def left(x:Union[Span,SpanList],y:Union[Span,SpanList]) -> bool:
    '''
    Tests if Span y is either touching or hovering left with respect to span x.
    '''
    return right(y, x)

def nested(x:Span, y:Span) -> bool:
    """
    Tests if Span y is nested inside Span x.
    Pictorial example:
    xxxxxxxx
      yyyyy
    """
    return x.start <= y.start <= y.end <= x.end

def equal(x:Span, y:Span) -> bool:
    """
    Tests if Span y is equal to Span x. (Both are nested within each other).
    Pictorial example:
    xxxxxxxx
    yyyyyyyy
    """
    return nested(x, y) and nested(y, x)

def nested_aligned_right(x:Span, y:Span) -> bool:
    """
    Tests if Span y is nested inside Span x, and is aligned with right 
    ending of x.
    Pictorial example:
    xxxxxxxx
       yyyyy
    """
    return nested(x, y) and x.end == y.end

def nested_aligned_left(x:Span, y:Span) -> bool:
    """
    Tests if Span y is nested inside Span x, and is aligned with left 
    ending of x.
    Pictorial example:
    xxxxxxxx
    yyyyy
    """
    return nested(x, y) and x.start == y.start

def overlapping_left(x:Span, y:Span) -> bool:
    """
    Tests if left side of Span x overlaps with Span y, but 
    y is not nested within x.
    Pictorial example:
      xxxxxxxx
    yyyyy
    """
    return y.start < x.start < y.end

def overlapping_right(x:Span, y:Span) -> bool:
    """
    Tests if right side of Span x overlaps with Span y, but 
    y is not nested within x.
    Pictorial example:
    xxxxxxxx
          yyyyy
    """
    return y.start < x.end < y.end

def conflict(x:Span, y:Span) -> bool:
    """
    Tests if there is a conflict between Spans x an y: one
    of the Spans is either nested within other, or there 
    is an overlapping from right or left side.
    """
    return nested(x, y) or nested(y, x) or overlapping_left(x, y) or overlapping_right(x, y)
