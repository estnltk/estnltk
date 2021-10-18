from estnltk_core import Layer
from estnltk_core.layer_operations import flatten

from estnltk_core.common import load_text_class

def test_flatten_no_disambiguation():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Aias sadas saia.')

    layer_1 = Layer('test_1', attributes=['attr_1', 'attr_2'], text_object=text)
    text.add_layer(layer_1)
    result = flatten(layer_1, 'test_out')
    assert isinstance(result, Layer)
    assert result.ambiguous is True
    assert result.name == 'test_out'
    assert result.attributes == ('attr_1', 'attr_2')
    assert len(result) == 0

    layer_1.add_annotation((0, 5), attr_1=0, attr_2=1)
    layer_1.add_annotation((0, 10), attr_1=2, attr_2=3)
    layer_1.add_annotation((11, 15), attr_1=2, attr_2=3)

    result = flatten(layer_1, 'test_out')
    assert isinstance(result, Layer)
    assert result.name == 'test_out'
    assert result.attributes == ('attr_1', 'attr_2')
    assert len(result) == 3

    layer_2 = Layer('test_2', attributes=['attr_3', 'attr_4'], text_object=text, enveloping='test_1', ambiguous=True)
    layer_2.add_annotation([layer_1[0], layer_1[2]], attr_3=1)
    layer_2.add_annotation([layer_1[0], layer_1[2]], attr_3=2)
    layer_2.add_annotation([layer_1[1], layer_1[2]])

    result = flatten(layer_2, 'test_out')
    assert isinstance(result, Layer)
    assert result.name == 'test_out'
    assert result.attributes == ('attr_3', 'attr_4')
    assert len(result) == 1
    assert result.ambiguous is True
    assert result.enveloping is None
    span = result[0]
    assert span.start == 0
    assert span.end == 15
    assert len(span.annotations) == 3



def test_flatten_pick_first_disambiguation():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Aias sadas saia.')

    layer_1 = Layer('test_1', attributes=['lemma', 'pos'], \
                    text_object=text, ambiguous=True)
    layer_1.add_annotation((0, 4), lemma='aed', pos='S')
    layer_1.add_annotation((0, 4), lemma='Aed', pos='H')
    layer_1.add_annotation((5, 10), lemma='sadama', pos='V')
    layer_1.add_annotation((11, 15), lemma='sai', pos='S1')
    layer_1.add_annotation((11, 15), lemma='sai', pos='S2')
    
    result = flatten( layer_1, 'test_disambiguated_out', \
                      disambiguation_strategy='pick_first' )
    assert result.ambiguous is False
    assert len(result) == 3
    assert len(result[0].annotations) == 1
    assert result[0].annotations[0]['pos'] == 'S'
    assert result[0].annotations[0]['lemma'] == 'aed'
    assert len(result[1].annotations) == 1
    assert len(result[2].annotations) == 1

