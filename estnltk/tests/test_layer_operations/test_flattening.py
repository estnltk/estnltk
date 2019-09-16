from estnltk import Text, Layer
from estnltk.layer_operations import flatten


def test_flatten():
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
