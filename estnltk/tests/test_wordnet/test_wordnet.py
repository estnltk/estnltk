from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset

wn = Wordnet()


def test_getitem_word():
    result = wn['king']
    king1 = [66332, 'king', 'estwn-et-61958-n', 'n', 2, 'king']
    king2 = [16159, 'king', 'estwn-et-9954-n', 'n', 1, 'king']
    expected = [Synset(wn, info) for info in [king1, king2]]

    assert result == expected


def test_getitem_word_and_pos():
    result = wn['king', 'n']
    king1 = [66332, 'king', 'estwn-et-61958-n', 'n', 2, 'king']
    king2 = [16159, 'king', 'estwn-et-9954-n', 'n', 1, 'king']
    expected = [Synset(wn, info) for info in [king1, king2]]

    assert result == expected


def test_getitem_word_and_int():
    assert wn['king', 1] == Synset(wn, [66332, 'king', 'estwn-et-61958-n', 'n', 2, 'king'])
