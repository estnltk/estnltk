import pytest

from estnltk import Text
from estnltk import Layer
from estnltk import ElementaryBaseSpan

from estnltk.tests import inspect_class_members
from estnltk.tests import new_text


def test_object_teardown():
    # One cannot delete text object when layers are referenced!
    # This is a sad truth caused by reference counting memory model
    text = Text('Surematu Kašei')
    layer = Layer(name='empty_layer')
    text.add_layer(layer)
    del text
    assert layer.text_object.text == 'Surematu Kašei'


def test_equal():
    t_1 = Text('Tekst algab. Tekst lõpeb.')
    t_2 = Text('Tekst algab.')
    assert t_1 != t_2
    t_2 = Text('Tekst algab. Tekst lõpeb.')
    assert t_1 == t_2

    t_1.meta['year'] = 2017
    assert t_1 != t_2
    t_2.meta['year'] = 2017
    assert t_1 == t_2

    t_1.tag_layer(['morph_extended', 'paragraphs'])
    assert t_1 != t_2
    t_2.tag_layer(['morph_extended', 'paragraphs'])
    assert t_1 == t_2
    t_1['morph_analysis'][0].annotations[0].form = 'x'
    assert t_1 != t_2

    t_1 = new_text(5)
    t_2 = new_text(5)
    assert t_1 == t_2
    t_1.layer_5[1].annotations[1].attr_5 = 'bla'
    assert t_1 != t_2


def test_delete_layer():
    text = Text('Minu nimi on Uku.')
    assert text.layers == {}

    layer_names = ['words', 'sentences', 'morph_analysis']

    text.tag_layer(layer_names)
    assert set(layer_names) <= set(text.layers)
    assert set(layer_names) <= set(text.__dict__)

    # Test del text.layer_name
    # Deleting a root layer should also delete all its dependants
    del text.tokens

    assert 'tokens' not in text.__dict__
    assert 'compound_tokens' not in text.__dict__

    del text.words

    assert 'words' not in text.__dict__
    assert 'sentences' not in text.__dict__
    assert 'morph_analysis' not in text.__dict__

    assert text.layers == {}

    # Test that deleted layers are indeed missing
    with pytest.raises(AttributeError):
        _ = text.words

    with pytest.raises(AttributeError):
        _ = text.sentences

    with pytest.raises(AttributeError):
        _ = text.morph_analysis

    # Test del text['layer_name']
    # Deleting a root layer should also delete all its dependants
    text.tag_layer(layer_names)

    del text['tokens']

    assert 'tokens' not in text.__dict__
    assert 'compound_tokens' not in text.__dict__

    del text['words']

    assert 'words' not in text.__dict__
    assert 'sentences' not in text.__dict__
    assert 'morph_analysis' not in text.__dict__

    assert text.layers == {}

    # Test that deleted layers are indeed missing
    with pytest.raises(AttributeError):
        _ = text.words

    with pytest.raises(AttributeError):
        _ = text.sentences

    with pytest.raises(AttributeError):
        _ = text.morph_analysis


def test_layer_access():
    text = Text('''Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.''')

    # Accessing non-existent layer
    with pytest.raises(AttributeError):
        _ = text.test
    with pytest.raises(KeyError):
        _ = text['test']

    # Accessing empty layer
    layer = Layer(name='empty_layer', attributes=['attr1'])
    text.add_layer(layer)

    assert text.empty_layer is layer
    assert text['empty_layer'] is layer
    assert text.empty_layer is text['empty_layer']

    with pytest.raises(IndexError):
        _ = text.empty_layer[0]
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    # Accessing non-empty layer
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)

    assert text.nonempty_layer is layer
    assert text['nonempty_layer'] is layer

    assert text.nonempty_layer[0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text.nonempty_layer[0] is text['nonempty_layer'][0]


def test_text_attribute_access():
    text = Text('test')
    assert text.text == 'test'

    # Layer text is not present
    with pytest.raises(KeyError):
        _ = text['text']

    # Attribute text is readonly
    with pytest.raises(AttributeError):
        text.text = 'asd'

    # Layer 'text' is accessible
    layer = Layer(name='text', attributes=['attr1'])
    text.add_layer(layer)

    assert text['text'] is layer
    with pytest.raises(IndexError):
        _ = text['text'][0]

    text = Text('test')
    layer = Layer(name='text', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)

    assert text['text'] is layer
    assert text['text'][0].attr_0 == 'L0-0'
    assert text['text'][0] == layer[0]


def test_access_of_other_shadowed_layers():
    properties = ['attributes', 'layers', 'text']
    public_methods = ['add_layer', 'analyse', 'diff', 'list_layers', 'set_text', 'tag_layer']
    public_variables = ['attribute_mapping_for_elementary_layers', 'attribute_mapping_for_enveloping_layers', 'meta']
    shadowed_layers = properties + public_methods + public_variables

    text = Text('Test text.')
    members = inspect_class_members(text)
    assert properties == members['properties']
    assert public_variables == members['public_variables']
    assert public_methods == members['public_methods']

    # Shadowed layers are not present
    for layer_name in shadowed_layers:
        with pytest.raises(KeyError):
            _ = text[layer_name]

    # Shadowed layers are accessible
    for layer_name in shadowed_layers:
        # Test access for empty layers
        layer = Layer(name=layer_name, attributes=['attr'])
        text.add_layer(layer)

        assert text[layer_name] is layer
        with pytest.raises(IndexError):
            _ = text[layer_name][0]

        # Test access for non-empty layers
        layer = Layer(name=layer_name, attributes=['attr_0', 'attr_1'])
        layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
        text.add_layer(layer)

        assert text[layer_name] is layer
        assert text[layer_name][0].attr_0 == 'L0-0'
        assert text[layer_name][0] == layer[0]


def test_add_layer():
    # Canonical way to add a layer
    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text.add_layer(layer)
    assert text['empty_layer'] is layer
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    text = Text('test')
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)
    assert text['nonempty_layer'] is layer
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0] == layer[0]

    # Safety against recursive references in layers
    text = Text('Rekursioon, rekursioon. Sind vaid loon')
    layer = Layer(name='recursive_layer', attributes=['recursive_ref_1','recursive_ref_2', 'recursive_ref_3'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), recursive_ref_1=text, recursive_ref_2=layer, recursive_ref_3=None)
    annotation = layer[0].annotations[0]
    layer[0].recursive_ref_3 = annotation
    text.add_layer(layer)
    assert text['recursive_layer'] is layer
    assert text['recursive_layer'][0].annotations[0].recursive_ref_1 is text
    assert text['recursive_layer'][0].annotations[0].recursive_ref_2 is layer
    assert text['recursive_layer'][0].annotations[0].recursive_ref_3 is annotation

    # Safety against double invocation
    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text.add_layer(layer)
    with pytest.raises(AssertionError, match="this Text object already has a layer with name 'empty_layer'"):
        text.add_layer(layer)

    # Safety against double linking
    text1 = Text('test1')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text1.add_layer(layer)

    text2 = Text('test2')
    with pytest.raises(AssertionError,
                       match="can't add layer 'empty_layer', this layer is already bound to another Text object"):
        text2.add_layer(layer)

    # Possible alternatives for Text.add_layer()
    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text['empty_layer'] = layer
    assert text['empty_layer'] is layer
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text.empty_layer = layer
    assert text['empty_layer'] is layer
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    text = Text('test')
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text['nonempty_layer'] = layer
    assert text['nonempty_layer'] is layer
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0] == layer[0]

    text = Text('test')
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.nonempty_layer = layer
    assert text['nonempty_layer'] is layer
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0] == layer[0]
