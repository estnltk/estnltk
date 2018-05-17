from typing import Any

from estnltk import Span

#  Layer operations are ported from:
#    https://github.com/estnltk/estnltk/blob/master/estnltk/single_layer_operations/layer_positions.py


def touching_right(self, y: Any) -> bool:
    """
    Tests if Span y is touching this Span (x) from the right.
    Pictorial example:
    xxxxxxxx
            yyyyy
    """
    assert isinstance(y, Span)
    return self.end == y.start


def touching_left(self, y: Any) -> bool:
    """
    Tests if Span y is touching this Span (x) from the left.
    Pictorial example:
         xxxxxxxx
    yyyyy
    """
    assert isinstance(y, Span)
    return touching_right(y, self)


def hovering_right(self, y: Any) -> bool:
    """
    Tests if Span y is hovering right from this Span (x).
    Pictorial example:
    xxxxxxxx
              yyyyy
    """
    assert isinstance(y, Span)
    return self.end < y.start


def hovering_left(self, y: Any) -> bool:
    """
    Tests if Span y is hovering left from this Span (x).
    Pictorial example:
            xxxxxxxx
    yyyyy
    """
    assert isinstance(y, Span)
    return hovering_right(y, self)


def right(self, y: Any) -> bool:
    """
    Tests if Span y is either touching or hovering right with respect to this Span.
    """
    assert isinstance(y, Span)
    return touching_right(self, y) or hovering_right(self, y)


def left(self, y: Any) -> bool:
    """
    Tests if Span y is either touching or hovering left with respect to this Span.
    """
    assert isinstance(y, Span)
    return right(y, self)


def nested(self, y: Any) -> bool:
    """
    Tests if Span y is nested inside this Span (x).
    Pictorial example:
    xxxxxxxx
      yyyyy
    """
    assert isinstance(y, Span)
    return self.start <= y.start <= y.end <= self.end


def equal(self, y: Any) -> bool:
    """
    Tests if Span y is positionally equal to this Span (x).
    (Both are nested within each other).
    Pictorial example:
    xxxxxxxx
    yyyyyyyy
    """
    assert isinstance(y, Span)
    return nested(self, y) and nested(y, self)


def nested_aligned_right(self, y: Any) -> bool:
    """
    Tests if Span y is nested inside this Span (x), and
    Span y is aligned with the right ending of this Span.
    Pictorial example:
    xxxxxxxx
       yyyyy
    """
    assert isinstance(y, Span)
    return nested(self, y) and self.end == y.end


def nested_aligned_left(self, y: Any) -> bool:
    """
    Tests if Span y is nested inside this Span (x), and
    Span y is aligned with the left ending of this Span.
    Pictorial example:
    xxxxxxxx
    yyyyy
    """
    assert isinstance(y, Span)
    return nested(self, y) and self.start == y.start


def overlapping_left(self, y: Any) -> bool:
    """
    Tests if left side of this Span (x) overlaps with
    the Span y, but y is not nested within this Span.
    Pictorial example:
      xxxxxxxx
    yyyyy
    """
    assert isinstance(y, Span)
    return y.start < self.start < y.end


def overlapping_right(self, y: Any) -> bool:
    """
    Tests if right side of this Span (x) overlaps with
    the Span y, but y is not nested within this Span.
    Pictorial example:
    xxxxxxxx
          yyyyy
    """
    assert isinstance(y, Span)
    return y.start < self.end < y.end


def conflict(self, y: Any) -> bool:
    """
    Tests if there is a conflict between this Span and the
    Span y: one of the Spans is either nested within other,
    or there is an overlapping from right or left side.
    """
    assert isinstance(y, Span)
    return nested(self, y) or nested(y, self) or \
           overlapping_left(self, y) or overlapping_right(self, y)
