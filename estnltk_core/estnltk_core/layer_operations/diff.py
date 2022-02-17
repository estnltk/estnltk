from typing import Union
from operator import eq

from estnltk_core.layer.base_layer import BaseLayer


def diff_layer(a: Union[BaseLayer, 'Layer'], b: Union[BaseLayer, 'Layer'], comp=eq):
    """Generator of layer differences.

    In detail: iterates over spans of two layers and yields spans that are:
    1) missing from the second layer, 2) missing from the first layer, or
    3) present in both layers, but different according to the comparator
    function (e.g. contain different annotations).
    Spans of two layers are considered as matching (by their positions) only
    if their base spans are matching. If there is a partial overlap between
    the base spans, then the comparator function is not applied and the
    corresponding spans are yielded as missing spans (cases 1 and 2).

    Parameters
    ----------
    a: Union[BaseLayer, 'Layer']
        First layer to be compared
    b: Union[BaseLayer, 'Layer']
        Second layer to be compared
    comp: compare function, default: operator.eq
        Function that returns True if layer elements are equal and False otherwise.
        Only layer elements with equal spans are compared.

    Yields
    -------
    Tuple[Optional[Span], Optional[Span]]
        Pairs of different spans. In place of missing layer element, None is returned.
    """
    a = iter(a)
    b = iter(b)
    a_end = False
    b_end = False
    try:
        x = next(a)
    except StopIteration:
        a_end = True
    try:
        y = next(b)
    except StopIteration:
        b_end = True

    while not a_end and not b_end:
        if x < y:
            yield (x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.base_span == y.base_span:
            if not comp(x, y):
                yield (x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield (None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True

    if a_end and b_end:
        return

    if a_end:
        yield (None, y)
        yield from ((None, y) for y in b)

    if b_end:
        yield (x, None)
        yield from ((x, None) for x in a)

