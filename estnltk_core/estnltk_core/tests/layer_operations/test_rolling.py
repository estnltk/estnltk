import pytest
from estnltk_core import Layer
from estnltk_core.tests import new_text


def test_init():
    layer = Layer('test')

    with pytest.raises(TypeError):
        layer.rolling(window='3')

    with pytest.raises(ValueError):
        layer.rolling(window=0)

    with pytest.raises(TypeError):
        layer.rolling(window=3, min_periods='2')

    with pytest.raises(ValueError):
        layer.rolling(window=3, min_periods=0)

    with pytest.raises(ValueError):
        layer.rolling(window=3, min_periods=4)


def test_repr():
    layer = Layer('test')
    assert repr(layer.rolling(3, min_periods=2, inside='bla')) ==\
           "Rolling(layer=<test>, window=3, min_periods=2, inside='bla')"


def test_default():
    layer = new_text(5)['layer_0']

    result = [spans for spans in layer.rolling(window=3, min_periods=None, inside=None)]

    assert [r.text for r in result] == [
        ['Sada', 'kaks', 'kakskümmend'],
        ['kaks', 'kakskümmend', 'kümme'],
        ['kakskümmend', 'kümme', 'kolm'],
        ['kümme', 'kolm', ' Neli'],
        ['kolm', ' Neli', 'tuhat'],
        [' Neli', 'tuhat', 'viis'],
        ['tuhat', 'viis', 'viissada'],
        ['viis', 'viissada', 'sada'],
        ['viissada', 'sada', 'kuus'],
        ['sada', 'kuus', 'kuuskümmend'],
        ['kuus', 'kuuskümmend', 'kümme'],
        ['kuuskümmend', 'kümme', 'seitse'],
        ['kümme', 'seitse', 'koma'],
        ['seitse', 'koma', 'kaheksa'],
        ['koma', 'kaheksa', 'Üheksa'],
        ['kaheksa', 'Üheksa', 'Üheksakümmend'],
        ['Üheksa', 'Üheksakümmend', 'kümme'],
        ['Üheksakümmend', 'kümme', 'tuhat']]

    assert [] == [spans for spans in layer.rolling(window=21, min_periods=None, inside=None)]


def test_inside():
    layer = new_text(5)['layer_0']
    result = [spans for spans in layer.rolling(window=3, min_periods=2, inside='layer_4')]
    assert [r.text for r in result] == [
        ['Sada', 'kakskümmend'],
        ['Sada', 'kakskümmend', 'kolm'],
        ['kakskümmend', 'kolm'],
        [' Neli', 'tuhat'],
        [' Neli', 'tuhat', 'viissada'],
        ['tuhat', 'viissada', 'kuuskümmend'],
        ['viissada', 'kuuskümmend', 'seitse'],
        ['kuuskümmend', 'seitse'],
        ['Üheksakümmend', 'tuhat'],
        ['Üheksakümmend', 'tuhat']]

    with pytest.raises(ValueError):
        list(layer.rolling(window=3, min_periods=2, inside='non_existent'))
