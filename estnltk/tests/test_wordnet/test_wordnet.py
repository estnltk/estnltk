from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset

wn = Wordnet()


def test_getitem_word():
    result = wn['laulma']
    ids = [7157, 63569]
    expected = [Synset(wn, id) for id in ids]

    assert result == expected


def test_getitem_word_and_pos():
    result = wn['laulma', 'v']
    ids = [7157, 63569]
    expected = [Synset(wn, id) for id in ids]

    assert result == expected


def test_getitem_word_and_int():
    assert wn['laulma', 1] == Synset(wn, 7157)
