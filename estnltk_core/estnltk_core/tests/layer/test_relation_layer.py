import pytest

import re
from copy import copy, deepcopy

from estnltk_core import ElementaryBaseSpan
from estnltk_core import RelationLayer, Relation

from estnltk_core.common import load_text_class


def test_relation_layer_basic():
    # Test basic API of the relations layer (w/o Text object)
    
    # Test creating layer:
    layer = RelationLayer('test', span_names=['arg0', 'arg1'], 
                                  attributes=['attr1', 'attr2'])
    assert layer.span_names == ('arg0', 'arg1')
    assert layer.attributes == ('attr1', 'attr2')
    assert layer.ambiguous == False
    assert len(layer) == 0
    assert layer.span_level is None
    
    with pytest.raises(AssertionError):
        # error: layer name cannot consist of whitespace
        layer2 = RelationLayer('  ', span_names=['arg0', 'arg1'], 
                                     attributes=['attr1', 'attr2'])
    
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer2 = RelationLayer('test2', span_names=['arg0', 'arg1'], 
                                        attributes=['arg1', 'attr1', 'attr2'])
    
    # Test that span names and attributes cannot be mingled later
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer.attributes = ('arg0', 'arg1')
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer.span_names = ('attr1', 'attr2')

    # Test adding annotations:
    # add relation annotation via dict 
    layer.add_annotation( {'arg0': (0, 4), 'arg1': (6, 12), 'attr1': 1})
    # add relation annotation via kwargs
    layer.add_annotation( arg0=(20, 24), arg1=(26, 32), attr1=2, attr2=2 )
    # combine dict and keywords, skip one arg
    layer.add_annotation( {'arg0': (14, 18), 'attr1': 3}, attr2=3 )
    # leave annotations empty
    layer.add_annotation( arg0=(40, 44), arg1=(46, 52) )

    assert len(layer) == 4
    assert layer.span_level == 0
    assert [sp.as_tuple for sp in layer[0].spans] == \
            [('arg0', ElementaryBaseSpan(0, 4)),   ('arg1', ElementaryBaseSpan(6, 12))]
    assert [sp.as_tuple for sp in layer[1].spans] == \
            [('arg0', ElementaryBaseSpan(20, 24)), ('arg1', ElementaryBaseSpan(26, 32))]
    assert [sp.as_tuple for sp in layer[2].spans] == \
            [('arg0', ElementaryBaseSpan(14, 18))]
    assert [sp.as_tuple for sp in layer[3].spans] == \
            [('arg0', ElementaryBaseSpan(40, 44)), ('arg1', ElementaryBaseSpan(46, 52))]
    assert [dict(a) for a in layer[0].annotations] == [{'attr1': 1, 'attr2': None}]
    assert [dict(a) for a in layer[1].annotations] == [{'attr1': 2, 'attr2': 2}]
    assert [dict(a) for a in layer[2].annotations] == [{'attr1': 3, 'attr2': 3}]
    assert [dict(a) for a in layer[3].annotations] == [{'attr1': None, 'attr2': None}]

    with pytest.raises(ValueError):
        # error: named span(s) cannot be missing
        layer.add_annotation( {'attr1': 4, 'attr2': 4} )
    with pytest.raises(ValueError):
        # error: layer has different span level than newly addable spans
        layer.add_annotation( {'arg0': [(50, 54), (56, 64)], 'attr1': 4} )
    with pytest.raises(TypeError):
        # error: wrong type for named span
        layer.add_annotation( {'arg0': 1, 'attr1': 4} )
    with pytest.raises(ValueError):
        # error: wrong type for named span
        layer.add_annotation( {'arg1': None, 'attr1': 4} )
    with pytest.raises(Exception):
        # error: cannot add more than one annotation to unambiguous layer
        layer.add_annotation( arg0=(20, 24), arg1=(26, 32), attr1=4, attr2=4 )


def test_relation_layer_basic_with_text_obj():
    # Test basic API of the relations layer (with Text object)
    
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('0123456789')
    layer = RelationLayer('test', span_names=['arg0', 'arg1'], 
                                   attributes=['summa'],
                                   text_object=text)
    layer.add_annotation( {'arg0': (0, 1), 'arg1': (1, 2), 'summa': 1} )
    layer.add_annotation( {'arg0': (2, 3), 'arg1': (3, 4), 'summa': 5} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (2, 3), 'summa': 7} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (4, 5), 'summa': 9} )
    relations = []
    for rel in layer:
        relation_dict = {**{sp: rel[sp].text for sp in layer.span_names},
                         **{a: rel[a] for a in layer.attributes} }
        relations.append(relation_dict)
    assert relations == \
        [{'arg0': '0', 'arg1': '1', 'summa': 1}, \
         {'arg0': '2', 'arg1': '3', 'summa': 5}, \
         {'arg0': '5', 'arg1': '2', 'summa': 7}, \
         {'arg0': '5', 'arg1': '4', 'summa': 9}]


def test_relation_layer_deep_copy():
    # Simple empty layer
    layer = RelationLayer('test', span_names=['my_span'])
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Simple relations layer with some relations
    layer = RelationLayer('test', span_names=['my_span'], 
                                   attributes=['attribute1', 'attribute2'],
                                   ambiguous=True)
    layer.add_annotation(my_span=(0, 2), attribute1='test1')
    layer.add_annotation(my_span=(2, 4), attribute2='test2')
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer.span_names == layer_deepcopy.span_names
    assert layer.attributes == layer_deepcopy.attributes
    assert layer.ambiguous  == layer_deepcopy.ambiguous
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Modify attributes
    # Initially, both layers' attributes point to the same tuple
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy.attributes is layer.attributes
    layer_deepcopy.attributes = [*layer_deepcopy.attributes, 'new_attribute']
    assert layer_deepcopy.attributes != layer.attributes
    assert layer_deepcopy != layer
    layer_deepcopy.attributes = layer_deepcopy.attributes[:-1]
    # After modification of one layer, tuples won't be same anymore ...
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy == layer
    assert layer_deepcopy.attributes is not layer.attributes

    # Modify relations
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] == layer[0]
    # Relation references are different
    assert layer_deepcopy[0] is not layer[0]
    # Deleting relation from one layer does not affect the other layer
    del layer_deepcopy[0]
    del layer_deepcopy[0]
    assert layer_deepcopy != layer
    layer_deepcopy.add_annotation(my_span=(0, 2), attribute1='test1')
    layer_deepcopy.add_annotation(my_span=(2, 4), attribute2='test2')
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] is not layer[0]

    # Modify annotations
    assert layer_deepcopy[0].annotations == layer[0].annotations
    # We can modify annotations without affecting the other layer
    layer_deepcopy.add_annotation( {**{sp.name: sp.base_span for sp in layer_deepcopy[1].spans}, \
                                    **{'attribute2': 'test3'}} )
    assert layer_deepcopy[0].annotations == layer[0].annotations
    assert layer_deepcopy[1].annotations != layer[1].annotations
    assert layer_deepcopy != layer
    del layer_deepcopy[1].annotations[-1]
    assert layer_deepcopy[1].annotations == layer[1].annotations
    assert layer_deepcopy == layer
    assert layer_deepcopy[1].annotations is not layer[1].annotations
    layer[0].annotations[-1].attribute1 = '???'
    assert layer_deepcopy[0].annotations[-1].attribute1 == 'test1'
    assert layer_deepcopy[0].annotations != layer[0].annotations
    layer_deepcopy[0].annotations[-1].attribute1 = '???'
    assert layer_deepcopy[0].annotations == layer[0].annotations
    assert layer_deepcopy[0] == layer[0]
    assert layer_deepcopy == layer