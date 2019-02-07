import pytest
from estnltk.tests import new_text
from estnltk import EnvelopingSpan


def test_getitem():
    layer_4 = new_text(5).layer_4

    assert isinstance(layer_4[0], EnvelopingSpan)

    assert layer_4[0]['attr_4'] == '123'

    with pytest.raises(AttributeError):
        layer_4[0]['bla']
