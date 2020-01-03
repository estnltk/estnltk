import pytest
from copy import copy, deepcopy

from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import EnvelopingSpan
from estnltk import Annotation
from estnltk import ElementaryBaseSpan
from estnltk import EnvelopingBaseSpan
from estnltk.tests import inspect_class_members


def test_len():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Empty annotation
    annotation = Annotation(span=span)
    assert len(annotation) == 0

    # Annotation without shadowed attributes
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    assert len(annotation) == 3

    # Annotation with shadowed attributes
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __deepcopy__='its gonna fail without arrangements')
    assert len(annotation) == 5


def test_methods_list():
    # Test that the list of prohibited attribute names is complete
    members = inspect_class_members(Annotation(None))
    assert set(members['properties']) <= Annotation.methods
    print(set(members['private_methods'])-set(Annotation.methods))
    assert set(members['private_methods']) <= Annotation.methods
    assert set(members['protected_methods']) <= Annotation.methods
    assert set(members['public_methods']) <= Annotation.methods
    assert set(members['private_variables']) <= Annotation.methods
    assert set(members['protected_variables']) <= Annotation.methods
    assert set(members['public_variables']) <= Annotation.methods
    # additional slots are assignable
    assert isinstance(Annotation.methods, frozenset)


def test_copy_constructors():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Copying of empty annotation
    annotation = Annotation(span=span)

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 0
    d_copy = deepcopy(annotation)
    assert d_copy is not annotation
    assert d_copy.span is None
    assert len(d_copy) == 0

    # Copying of a simple annotation without shadowed attributes
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})

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
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __deepcopy__='its gonna fail without arrangements')
    annotation['span'] = [55, 66]

    s_copy = copy(annotation)
    assert s_copy is not annotation
    assert s_copy.span is None
    assert len(s_copy) == 6
    assert s_copy.number is annotation.number
    assert s_copy.string is annotation.string
    assert s_copy.dict is annotation.dict
    assert s_copy['end'] is annotation['end']
    assert s_copy['__deepcopy__'] is annotation['__deepcopy__']
    assert s_copy['span'] is annotation['span']
    d_copy = deepcopy(annotation)
    assert d_copy is not annotation
    assert d_copy.span is None
    assert len(d_copy) == 6
    assert d_copy.number is annotation.number                     # Immutable
    assert d_copy.string is annotation.string                     # Immutable
    assert d_copy.dict is not annotation.dict                     # Mutable
    assert d_copy.dict == annotation.dict
    assert d_copy['end'] is not annotation['end']                 # Mutable
    assert d_copy['end'] == annotation['end']
    assert d_copy['__deepcopy__'] is annotation['__deepcopy__']   # Immutable
    assert d_copy['span'] is not annotation['span']               # Mutable
    assert d_copy['span'] == annotation['span']

    # Copying of recursive annotations
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
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
    assert list(d_copy.dict.keys()) == ['a', 'b', 'rec']
    assert d_copy.dict['a'] == annotation.dict['a']
    assert d_copy.dict['b'] == annotation.dict['b']
    assert d_copy.dict['rec'] is d_copy.dict['rec']
    assert d_copy.rec_attr is d_copy.rec_attr


def test_attribute_assignment_and_access():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Normal annotation without an attached span
    annotation = Annotation(span=None)
    annotation.attr_1 = 'üks'
    annotation.attr_2 = 1
    annotation.attr_3 = dict(a=1, b=2)
    assert len(annotation) == 3
    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 1
    assert annotation.attr_3 == dict(a=1, b=2)
    assert annotation['attr_1'] == 'üks'
    assert annotation['attr_2'] == 1
    assert annotation['attr_3'] == dict(a=1, b=2)

    # Normal annotation with an attached span
    annotation = Annotation(span=span, attr_1='kaks', attr_2=4, attr_3={})
    assert len(annotation) == 3
    assert annotation.attr_1 == 'kaks'
    assert annotation.attr_2 == 4
    assert annotation.attr_3 == {}
    annotation.attr_1 = 'üks'
    annotation.attr_2 = 1
    annotation.attr_3 = dict(a=1, b=2)
    annotation.attr_4 = 'uus'
    assert len(annotation) == 4
    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 1
    assert annotation.attr_3 == dict(a=1, b=2)
    assert annotation.attr_4 == 'uus'
    assert annotation['attr_1'] == 'üks'
    assert annotation['attr_2'] == 1
    assert annotation['attr_3'] == dict(a=1, b=2)
    assert annotation['attr_4'] == 'uus'

    # Tests that AttrDict methods cannot be assigned
    for attr in annotation.methods:
        with pytest.raises(AttributeError, match='attempt to set an attribute that shadows a method'):
            setattr(annotation, attr, 42)


def test_attribute_deletion():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Normal annotation without an attached span
    annotation = Annotation(span=None, attr_1='üks', attr_2=1, attr_3=dict(a=1, b=2))
    assert len(annotation) == 3
    assert annotation.mapping == dict(attr_1='üks', attr_2=1, attr_3=dict(a=1, b=2))
    del annotation.attr_1
    assert len(annotation) == 2
    assert annotation.mapping == dict(attr_2=1, attr_3=dict(a=1, b=2))
    del annotation.attr_2
    assert len(annotation) == 1
    assert annotation.mapping == dict(attr_3=dict(a=1, b=2))
    del annotation.attr_3
    assert len(annotation) == 0
    assert annotation.mapping == dict()

    # Normal annotation with an attached span
    annotation = Annotation(span=span, attr_1='kaks', attr_2=4, attr_3={})
    assert len(annotation) == 3
    assert annotation.mapping == dict(attr_1='kaks', attr_2=4, attr_3={})
    del annotation.attr_1
    assert len(annotation) == 2
    assert annotation.mapping == dict(attr_2=4, attr_3={})
    del annotation.attr_2
    assert len(annotation) == 1
    assert annotation.mapping == dict(attr_3={})
    del annotation.attr_3
    assert len(annotation) == 0
    assert annotation.mapping == dict()

    # Tests that Annotation methods cannot be deleted
    attrdict = Annotation(span=None)
    for attr in Annotation.methods:
        with pytest.raises(AttributeError, match="'Annotation' object has no attribute"):
            delattr(attrdict, attr)

    # Tests for missing attributes
    with pytest.raises(AttributeError, match="'Annotation' object has no attribute"):
        _ = attrdict.missing_attribute
    with pytest.raises(AttributeError, match="'Annotation' object has no attribute"):
        del attrdict.missing_attribute


def test_item_assignment_and_access():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)

    # Normal annotation without an attached span
    annotation = Annotation(span=None)
    annotation['attr_1'] = 'üks'
    annotation['attr_2'] = 1
    annotation['attr_3'] = dict(a=1, b=2)
    assert len(annotation) == 3
    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 1
    assert annotation.attr_3 == dict(a=1, b=2)
    assert annotation['attr_1'] == 'üks'
    assert annotation['attr_2'] == 1
    assert annotation['attr_3'] == dict(a=1, b=2)

    # Normal annotation with an attached span
    annotation = Annotation(span=span)
    annotation['attr_1'] = 'üks'
    annotation['attr_2'] = 1
    annotation['attr_3'] = dict(a=1, b=2)
    assert len(annotation) == 3
    assert annotation.attr_1 == 'üks'
    assert annotation.attr_2 == 1
    assert annotation.attr_3 == dict(a=1, b=2)
    assert annotation['attr_1'] == 'üks'
    assert annotation['attr_2'] == 1
    assert annotation['attr_3'] == dict(a=1, b=2)

    # Tests that Annotation methods can be keys
    annotation = Annotation(None)
    for attr in Annotation.methods:
        annotation[attr] = 42
        assert annotation[attr] == 42
        assert attr not in annotation.__dict__

    # Check that item assignment and deletion correctly updates __dict__
    annotation = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            methods=5, keys=['a', 'b'], __len__='its gonna fail without arrangements')
    assert annotation.__dict__ == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'})

    annotation['new'] = 56
    assert annotation.__dict__ == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'}, new=56)

    del annotation['new']
    assert annotation.__dict__ == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'})

    del annotation['__len__']
    assert annotation.__dict__ == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'})


def test_multi_indexing():
    annotation = Annotation(span=None, attr_1='üks', attr_2=1, attr_3=dict(a=1, b=2))
    assert annotation[()] == ()
    assert annotation['attr_1'] == 'üks'
    assert annotation[('attr_1',)] == ('üks',)
    assert annotation['attr_1', 'attr_2'] == ('üks', 1)
    assert annotation[('attr_1', 'attr_2')] == ('üks', 1)
    assert annotation['attr_1', 'attr_2', 'attr_3'] == ('üks', 1, dict(a=1, b=2))
    assert annotation[('attr_1', 'attr_2', 'attr_3')] == ('üks', 1, dict(a=1, b=2))

    # Tuple elements must be strings
    with pytest.raises(TypeError, match='index must be a string or a tuple of strings'):
        _ = annotation[(5,)]
    with pytest.raises(TypeError, match='index must be a string or a tuple of strings'):
        _ = annotation[(5,6)]

    # No multi-key deletion
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation[()]
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation[('attr_1',)]
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation['attr_1', 'attr_2']
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation[('attr_1', 'attr_2')]
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation['attr_1', 'attr_2', 'attr_3']
    with pytest.raises(KeyError, match="'Annotation' object does not have a key"):
        del annotation[('attr_1', 'attr_2', 'attr_3')]

    # No multi-key assignment
    print(isinstance((), str))
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation[()] = ()
    annotation['attr_1'] = 'üks'
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation[('attr_1',)] = ('üks',)
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation['attr_1', 'attr_2'] = ('üks', 1)
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation[('attr_1', 'attr_2')] = ('üks', 1)
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation['attr_1', 'attr_2', 'attr_3'] = ('üks', 1, dict(a=1, b=2))
    with pytest.raises(TypeError, match='index must be a string. Multi-indexing is not supported'):
        annotation[('attr_1', 'attr_2', 'attr_3')] = ('üks', 1, dict(a=1, b=2))


def test_span_slot_access_rules():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    other_span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)
    env_layer= Layer('env_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    env_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(spans=[span.base_span]), layer=env_layer)

    # Annotation can be attached to a random type
    annotation = Annotation(span=None)
    with pytest.raises(TypeError, match="span must be an instance of 'Span'"):
        annotation.span = 42

    # Annotation can be attached to a span
    annotation = Annotation(span=None)
    annotation.span = span
    assert annotation.span is span
    with pytest.raises(KeyError):
        _ = annotation['span']

    # Annotation can be attached to an enveloping span
    annotation = Annotation(span=None)
    annotation.span = env_span
    assert annotation.span is env_span
    with pytest.raises(KeyError):
        _ = annotation['span']

    # Annotation cannot be detached form its span
    with pytest.raises(AttributeError, match='an attempt to detach Annotation form its span'):
        annotation.span = None

    # Annotation cannot be re-attached to another span
    with pytest.raises(AttributeError, match='an attempt to re-attach Annotation to a different span'):
        annotation.span = other_span

    # Annotation cannot be re-attached to same span
    with pytest.raises(AttributeError, match='an attempt to re-attach Annotation to a different span'):
        annotation.span = span

    annotation = Annotation(span=span)

    # Annotation cannot be detached form its span
    with pytest.raises(AttributeError, match='an attempt to detach Annotation form its span'):
        annotation.span = None

    # Annotation cannot be re-attached to another span
    with pytest.raises(AttributeError, match='an attempt to re-attach Annotation to a different span'):
        annotation.span = other_span

    # Annotation cannot be re-attached to same span
    with pytest.raises(AttributeError, match='an attempt to re-attach Annotation to a different span'):
        annotation.span = span


def test_equality():
    text = Text('Tere!')
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=text)
    span = Span(base_span=ElementaryBaseSpan(0, 1), layer=layer)
    other_span = Span(base_span=ElementaryBaseSpan(0, 2), layer=layer)

    annotation_1 = Annotation(span=None)
    annotation_2 = Annotation(span=span)
    assert annotation_1 == annotation_1
    assert annotation_2 == annotation_2
    assert annotation_1 == annotation_2

    annotation_3 = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    annotation_4 = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    annotation_5 = Annotation(span=other_span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    assert annotation_3 == annotation_3
    assert annotation_3 == annotation_4
    assert annotation_3 == annotation_5
    assert annotation_4 == annotation_3
    assert annotation_4 == annotation_4
    assert annotation_4 == annotation_5
    assert annotation_5 == annotation_3
    assert annotation_5 == annotation_4
    assert annotation_5 == annotation_5

    assert annotation_1 != annotation_3
    assert annotation_1 != annotation_4
    assert annotation_1 != annotation_5
    assert annotation_2 != annotation_3
    assert annotation_2 != annotation_4
    assert annotation_2 != annotation_5

    annotation_6 = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                              methods=5, keys=['a', 'b'], __len__='its gonna fail without arrangements')
    annotation_7 = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                              methods=5, keys=['a', 'b'], __len__='its gonna fail without arrangements')
    assert annotation_6 == annotation_6
    assert annotation_6 == annotation_7
    assert annotation_7 == annotation_6
    assert annotation_7 == annotation_7

    assert annotation_3 != annotation_6
    assert annotation_3 != annotation_7
    assert annotation_4 != annotation_6
    assert annotation_4 != annotation_7
    assert annotation_5 != annotation_6
    assert annotation_5 != annotation_7


def test_repr_and_str():
    # Non-recursive annotations without the span
    annotation = Annotation(span=None)
    assert str(annotation) == 'Annotation(None, {})'
    assert repr(annotation) == 'Annotation(None, {})'
    annotation = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    assert str(annotation) == "Annotation(None, {'dict': {'a': 15, 'b': 'one'}, 'number': 42, 'string': 'twelve'})"
    assert repr(annotation) == "Annotation(None, {'dict': {'a': 15, 'b': 'one'}, 'number': 42, 'string': 'twelve'})"
    annotation = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __deepcopy__='its gonna fail without arrangements')
    assert str(annotation) == "Annotation(None, {'__deepcopy__': 'its gonna fail without arrangements'," + \
                              " 'dict': {'a': 15, 'b': 'one'}, 'end': ['a', 'b'], 'number': 42, 'string': 'twelve'})"
    assert repr(annotation) == "Annotation(None, {'__deepcopy__': 'its gonna fail without arrangements'," + \
                               " 'dict': {'a': 15, 'b': 'one'}, 'end': ['a', 'b'], 'number': 42, 'string': 'twelve'})"

    # Span in a layer must have all attributes required by the layer
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=Text('Tere!'))
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span)
    with pytest.raises(KeyError):
        assert str(annotation) == 'Annotation(Tere, {})'
    with pytest.raises(KeyError):
        assert repr(annotation) == 'Annotation(Tere, {})'
    # The order of attributes is determined by the order of attributes in the layer
    layer = Layer('test_layer', attributes=['number', 'string', 'dict'], text_object=Text('Tere!'))
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    assert str(annotation) == "Annotation('Tere', {'number': 42, 'string': 'twelve', 'dict': {'a': 15, 'b': 'one'}})"
    assert repr(annotation) == "Annotation('Tere', {'number': 42, 'string': 'twelve', 'dict': {'a': 15, 'b': 'one'}})"
    # There are no restrictions what attribute names are for the layer
    layer = Layer('test_layer', attributes=['number', 'string', 'dict', 'end', '__deepcopy__'], text_object=Text('Jah'))
    span = Span(base_span=ElementaryBaseSpan(0, 3), layer=layer)
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __deepcopy__='its gonna fail without arrangements')
    assert str(annotation) == "Annotation('Jah', {'number': 42, 'string': 'twelve', 'dict': {'a': 15, 'b': 'one'}," + \
                              " 'end': ['a', 'b'], '__deepcopy__': 'its gonna fail without arrangements'})"
    assert repr(annotation) == "Annotation('Jah', {'number': 42, 'string': 'twelve', 'dict': {'a': 15, 'b': 'one'}," +\
                               " 'end': ['a', 'b'], '__deepcopy__': 'its gonna fail without arrangements'})"

    # Simple test that repr and str are recursion safe
    annotation = Annotation(span=None)
    annotation.update(dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'}, rec=annotation))
    assert str(annotation) == "Annotation(None, {'dict': {'a': 15, 'b': 'one'}, 'number': 42," + \
                              " 'rec': ..., 'string': 'twelve'})"
    assert repr(annotation) == "Annotation(None, {'dict': {'a': 15, 'b': 'one'}, 'number': 42," + \
                               " 'rec': ..., 'string': 'twelve'})"
