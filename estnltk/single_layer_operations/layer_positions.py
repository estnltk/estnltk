"""
Lihtkihi elementidega opereerimise tööriistad.
"""


def touching_right(x, y):
    """
    xxxxxxxx
            yyyyy
    """
    return x['end'] == y['start']


def touching_left(x, y):
    """
         xxxxxxxx
    yyyyy
    """
    return touching_right(y, x)


def hovering_right(x, y):
    """
    xxxxxxxx
              yyyyy
    """
    return x['end'] < y['start']


def hovering_left(x, y):
    """
            xxxxxxxx
    yyyyy
    """
    return hovering_right(y, x)


def right(x, y):
    return touching_right(x, y) or hovering_right(x, y)


def left(x, y):
    return right(y, x)


def nested(x, y):
    """
    xxxxxxxx
      yyyyy
    """
    return x['start'] <= y['start'] <= y['end'] <= x['end']


def equal(x, y):
    """
    xxxxxxxx
    yyyyyyyy
    """
    return nested(x, y) and nested(y, x)


def nested_aligned_right(x, y):
    """
    xxxxxxxx
       yyyyy
    """
    return nested(x, y) and x['end'] == y['end']


def nested_aligned_left(x, y):
    """
    xxxxxxxx
    yyyyy
    """
    return nested(x, y) and x['start'] == y['start']


def overlapping_left(x, y):
    """
      xxxxxxxx
    yyyyy
    """
    return y['start'] < x['start'] < y['end']


def overlapping_right(x, y):
    """
    xxxxxxxx
          yyyyy
    """
    return y['start'] < x['end'] < y['end']


########################################################################################################################
########################################################################################################################
########################################################################################################################


def delete_left(elem1, elem2):
    """
    xxxxx
       yyyyy
    ---------
    xxx
       yyyyy
    """
    assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
    if overlapping_right(elem1, elem2):
        elem1['end'] = elem2['start']
    return elem1, elem2


def delete_right(elem1, elem2):
    """
    xxxxx
       yyyyy
    ---------
    xxxxx
         yyy
    """
    assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
    if overlapping_left(elem1, elem2):
        elem2['start'] = elem1['end']
    return elem1, elem2


def in_by_identity(lst, ob):
    """
    Returns True if ob is in lst by identity
    """
    for i in lst:
        if i is ob:
            return True
    return False


def pop_first_by_identity(lst, ob):
    for i in range(len(lst)):
        if lst[i] is ob:
            break
    else:
        return None
    return lst.pop(i)



def iterate_intersecting_pairs(layer):
    """
    Given a layer of estntltk objects, yields pairwise intersecting elements.
    Breaks when the layer is changed or deleted after initializing the iterator.
    """
    yielded = set()
    ri = layer[:]  # Shallow copy the layer
    for i1, elem1 in enumerate(ri):
        for i2, elem2 in enumerate(ri):
            if i1 != i2 and elem1['start'] <= elem2['start'] < elem1['end']:
                inds = (i1, i2) if i1 < i2 else (i2, i1)
                if inds not in yielded and in_by_identity(layer, elem1) and in_by_identity(layer, elem2):
                    yielded.add(inds)
                    yield elem1, elem2

