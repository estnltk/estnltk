import pytest

from estnltk_core import Tagger

def test_tagger_creation():
    tagger = Tagger()

    with pytest.raises(AssertionError):
        new_tagger = Tagger('Kala')
