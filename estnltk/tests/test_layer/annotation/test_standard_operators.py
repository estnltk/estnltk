import pytest
from copy import copy, deepcopy

from estnltk import Annotation
from estnltk import ElementaryBaseSpan

def test_len():
    # Empty annotation
    base_span = ElementaryBaseSpan(0, 1)
    annotation = Annotation(base_span)
    assert len(annotation) == 0

    # Annotation without shadowed attributes
    annotation = Annotation(base_span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    assert len(annotation) == 3

    # Annotation with shadowed attributes


def test_copy_constructors():
    # Copying of empty annotation
    base_span = ElementaryBaseSpan(0, 1)
    annotation = Annotation(base_span)

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 0
    d_copy = deepcopy(annotation)
    assert d_copy is not annotation
    assert d_copy.span is None
    assert len(d_copy) == 0

    # Copying of a simple annotation without shadowed attributes
    annotation = Annotation(base_span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 3
    assert s_copy.number is annotation.number
    assert s_copy.string is annotation.string
    assert s_copy.dict is annotation.dict
    d_copy = deepcopy(annotation)
    assert d_copy is not annotation
    assert d_copy.span is None
    assert len(d_copy) == 3
    assert d_copy.number is annotation.number  # Immutable
    assert d_copy.string is annotation.string  # Immutable
    assert d_copy.dict is not annotation.dict  # Mutable
    assert d_copy.dict == annotation.dict

    # Copying of simple annotations with shadowed attributes
    annotation = Annotation(base_span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __deepcopy__='its gonna fail without arrangements')

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 5
    assert s_copy.number is annotation.number
    assert s_copy.string is annotation.string
    assert s_copy.dict is annotation.dict
    assert s_copy['end'] is annotation['end']
    assert s_copy['__deepcopy__'] is annotation['__deepcopy__']
    # d_copy = deepcopy(annotation)
    # assert d_copy is not annotation
    # assert d_copy.span is None
    # assert d_copy.number is annotation.number                     # Immutable
    # assert d_copy.string is annotation.string                     # Immutable
    # assert d_copy.dict is not annotation.dict                     # Mutable
    # assert d_copy.dict == annotation.dict
    # assert d_copy['end'] is not annotation['end']                 # Mutable
    # assert d_copy['end'] == annotation['end']
    # assert d_copy['__deepcopy__'] is annotation['__deepcopy__']   # Immutable

    # Copying of recursive annotations
    annotation = Annotation(base_span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    annotation.rec_attr = annotation
    annotation.dict['rec'] = annotation

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 4
    assert s_copy.number is annotation.number
    assert s_copy.string is annotation.string
    assert s_copy.dict is annotation.dict
    assert s_copy.rec_attr is annotation.rec_attr
    d_copy = deepcopy(annotation)
    assert d_copy is not annotation
    assert d_copy.span is None
    assert d_copy.number is annotation.number  # Immutable
    assert d_copy.string is annotation.string  # Immutable
    assert d_copy.dict is not annotation.dict  # Mutable
    assert list(d_copy.dict.keys()) == ['a', 'b','rec']
    assert d_copy.dict['a'] == annotation.dict['a']
    assert d_copy.dict['b'] == annotation.dict['b']
    assert d_copy.dict['rec'] is d_copy.dict['rec']
    assert d_copy.rec_attr is d_copy.rec_attr
