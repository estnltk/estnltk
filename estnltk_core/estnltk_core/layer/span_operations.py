from typing import Sequence
from estnltk_core import Span


#  Span operations were adapted from:
#    https://github.com/estnltk/estnltk/blob/93163829bff223e2840b53c0480d00a5e817d406/estnltk/single_layer_operations/layer_positions.py


def touching_right(x: Span, y: Span) -> bool:
    """
    Tests if Span y is touching this Span (x) from the right.
    Pictorial example:
    xxxxxxxx
            yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return x.end == y.start


def touching_left(x: Span, y: Span) -> bool:
    """
    Tests if Span y is touching this Span (x) from the left.
    Pictorial example:
         xxxxxxxx
    yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return touching_right(y, x)


def hovering_right(x: Span, y: Span) -> bool:
    """
    Tests if Span y is hovering right from x.
    Pictorial example:
    xxxxxxxx
              yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return x.end < y.start


def hovering_left(x: Span, y: Span) -> bool:
    """
    Tests if Span y is hovering left from x.
    Pictorial example:
            xxxxxxxx
    yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return hovering_right(y, x)


def right(x: Span, y: Span) -> bool:
    """
    Tests if Span y is either touching or hovering right with respect to this Span.
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return touching_right(x, y) or hovering_right(x, y)


def left(x: Span, y: Span) -> bool:
    """
    Tests if Span y is either touching or hovering left with respect to this Span.
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return right(y, x)


def nested(x: Span, y: Span) -> bool:
    """
    Tests if Span y is nested inside x.
    Pictorial example:
    xxxxxxxx
      yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return x.start <= y.start <= y.end <= x.end


def equal(x: Span, y: Span) -> bool:
    """
    Tests if Span y is positionally equal to x.
    (Both are nested within each other).
    Pictorial example:
    xxxxxxxx
    yyyyyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return nested(x, y) and nested(y, x)


def symm_diff_ambiguous_spans(x: Span, y: Span, attributes: Sequence[str] = None):
    # assert isinstance(x, AmbiguousSpan)
    # assert isinstance(y, AmbiguousSpan)
    if attributes is None:
        annot_x = [a for a in x.annotations if a not in y.annotations]
        annot_y = [a for a in y.annotations if a not in x.annotations]
    else:
        values_x = [[getattr(annot, attr) for attr in attributes] for annot in x.annotations]
        values_y = [[getattr(annot, attr) for attr in attributes] for annot in y.annotations]
        annot_x = [a for a, values in zip(x, values_x) if values not in values_y]
        annot_y = [a for a, values in zip(y, values_y) if values not in values_x]

    return annot_x, annot_y


def nested_aligned_right(x: Span, y: Span) -> bool:
    """
    Tests if Span y is nested inside x, and
    Span y is aligned with the right ending of this Span.
    Pictorial example:
    xxxxxxxx
       yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return nested(x, y) and x.end == y.end


def nested_aligned_left(x: Span, y: Span) -> bool:
    """
    Tests if Span y is nested inside x, and
    Span y is aligned with the left ending of this Span.
    Pictorial example:
    xxxxxxxx
    yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return nested(x, y) and x.start == y.start


def overlapping_left(x: Span, y: Span) -> bool:
    """
    Tests if left side of x overlaps with
    the Span y, but y is not nested within this Span.
    Pictorial example:
      xxxxxxxx
    yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return y.start < x.start < y.end


def overlapping_right(x: Span, y: Span) -> bool:
    """
    Tests if right side of x overlaps with
    the Span y, but y is not nested within this Span.
    Pictorial example:
    xxxxxxxx
          yyyyy
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return y.start < x.end < y.end


def conflict(x: Span, y: Span) -> bool:
    """
    Tests if there is a conflict between the Span x and the
    Span y: one of the Spans is either nested within other,
    or there is an overlapping from right or left side.
    """
    assert isinstance(x, Span), x
    assert isinstance(y, Span), y
    return nested(x, y) or nested(y, x) or \
           overlapping_left(x, y) or overlapping_right(x, y)
