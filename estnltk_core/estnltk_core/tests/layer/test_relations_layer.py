import pytest

import re
from copy import copy, deepcopy

from estnltk_core import RelationsLayer, Relation

from estnltk_core.common import load_text_class


def test_relations_layer_deep_copy():
    # Simple empty layer
    layer = RelationsLayer('test', span_names=['my_span'])
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Simple relations layer with some relations
    layer = RelationsLayer('test', span_names=['my_span'], 
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