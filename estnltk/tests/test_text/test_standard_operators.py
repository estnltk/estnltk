import pytest

from estnltk import Text
from estnltk import Layer
from estnltk import ElementaryBaseSpan
from estnltk.tests import new_text


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
    assert text.empty_layer is layer
    assert text['empty_layer'] is layer
    assert text.empty_layer is text['empty_layer']

    with pytest.raises(IndexError):
        text.empty_layer[0]
    with pytest.raises(IndexError):
        text['empty_layer'][0]

    # Accessing non-empty layer
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)

    assert text.nonempty_layer is layer
    assert text['nonempty_layer'] is layer
    assert text.nonempty_layer is layer
    assert text['nonempty_layer'] is layer

    assert text.nonempty_layer[0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text.nonempty_layer[0] is text['nonempty_layer'][0]
