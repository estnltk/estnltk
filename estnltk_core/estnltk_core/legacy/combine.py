from typing import List, Callable, Dict, Generator


def combine_layers(a: List[Dict], b: List[Dict], fun: Callable[[Dict, Dict], Dict]) -> Generator:
    """
    Generator of merged layers.
    
    Remark: this function could be useful, but needs to be re-implemented to properly support v1.6.
    Can be added to layer_operations.aggregators.

    Parameters
    ----------
    a and b: iterable of dict
        Iterable of Estnltk layer elements. Must be ordered by *(start, end)*.

    fun: merge function
        Function that merges two layer elements. Must accept one None value.
        Example::

            def fun(x, y):
                if x is None:
                    return y
                return x

    Yields
    ------
    dict
        Merged layer elements.
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
        if x.start < y.start or x.start == y.start and x.end < y.end:
            yield fun(x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.start == y.start and x.end == y.end:
            yield fun(x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield fun(None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True

    if a_end and b_end:
        return

    if a_end:
        while True:
            yield fun(None, y)
            y = next(b)

    if b_end:
        while True:
            yield fun(x, None)
            x = next(a)
