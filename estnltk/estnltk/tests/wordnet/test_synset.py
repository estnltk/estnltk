from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset

wn = Wordnet()
ss = Synset(wn, 6299)
ss_koer = wn['koer'][0]


def test_init():
    name = "üllatamine.n.01"
    pos = "n"
    sense = 1
    literal = "üllatamine"

    assert ss.name == name and ss.pos == pos and ss.sense == sense and ss.literal == literal


def test_get_related_synset_with_relation():
    result = ss.get_related_synset("hypernym")
    expected = [Synset(wn, 3203)]
    assert result == expected


def test_get_related_synset_without_relation():
    result = ss.get_related_synset()
    expected = [(Synset(wn, 3203), 'hypernym')]
    assert result == expected


def test_closure():
    synset = ss_koer
    result = synset.closure('holonym')
    expected = [Synset(wn, 55794)]
    assert result == expected


def test_lemmas():
    assert ss.lemmas == ['üllatamine']


def test_path_similarity_with_self():
    synset = ss_koer
    assert wn.path_similarity(synset, synset) == 1


def test_path_similarity_with_parent():
    synset = ss_koer
    target_synset = wn['koduloom'][0]
    assert wn.path_similarity(synset, target_synset) == 1/2


def test_path_similarity_with_unreachable():
    synset = wn['laulma'][0]
    target_synset = ss_koer
    assert wn.path_similarity(synset, target_synset) is None
