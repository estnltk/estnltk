import pytest
from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset, SynsetException

wn = Wordnet()
ss = Synset(wn, 12346)


def test_init():
    name = "üllatamine.n.1"
    pos = "n"
    sense = 1
    literal = "üllatamine"

    assert ss.name == name and ss.pos == pos and ss.sense == sense and ss.literal == literal


def test_init_incorrect_id_type():
    with pytest.raises(SynsetException):
        Synset(wn, "vale id tüüp")


def test_get_related_synset_with_relation():
    result = ss.get_related_synset("hypernym")
    expected = [Synset(wn, 9997)]
    assert result == expected


def test_get_related_synset_without_relation():
    result = ss.get_related_synset()
    expected = [(Synset(wn, 9997), 'hypernym')]
    assert result == expected


def test_closure():
    synset = wn['koer'][0]
    result = synset.closure('hypernym')
    expected = Synset(wn, 8252)
    assert result == expected


def test_lemmas():
    assert ss.lemmas() == ['üllatamine']


def test_shortest_path_distance_with_self():
    synset = wn['koer'][0]
    assert synset._shortest_path_distance(synset) == 0


def test_path_similarity():
    aprill = wn['aprill'][0]
    diplomaat = wn['diplomaat'][0]
    assert aprill.path_similarity(diplomaat) == 0.05


def test_path_similarity_with_self():
    synset = wn['koer'][0]
    assert synset.path_similarity(synset) == 1


def test_path_similarity_with_parent():
    synset = wn['koer'][0]
    target_synset = wn['koduloom'][0]
    assert synset.path_similarity(target_synset) == 1/2


def test_path_similarity_with_unreachable():
    synset = wn['laulma'][0]
    target_synset = wn['koer'][0]
    assert synset.path_similarity(target_synset) is None
