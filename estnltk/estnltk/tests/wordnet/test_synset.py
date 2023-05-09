from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset

wn = Wordnet()

def test_init():
    ss = Synset(wn, 6299)
    name = "üllatamine.n.01"
    pos = "n"
    sense = 1
    literal = "üllatamine"

    assert ss.name == name and ss.pos == pos and ss.sense == sense and ss.literal == literal


def test_get_related_synset_with_relation():
    ss = Synset(wn, 6299)
    result = ss.get_related_synset("hypernym")
    expected = [Synset(wn, 3203)]
    assert result == expected


def test_get_related_synset_without_relation():
    ss = Synset(wn, 6299)
    result = ss.get_related_synset()
    if wn.version == '2.3.2':
        # [("Synset('ekstsitatsioon.n.01')", 'hypernym')]
        expected = [(Synset(wn, 3203), 'hypernym')]
    elif wn.version == '2.5.0':
        # [("Synset('faktilugu.n.01')", 'domain_topic'), ("Synset('ekstsitatsioon.n.01')", 'hypernym')]
        expected = [(Synset(wn, 58586), 'domain_topic'), (Synset(wn, 3203), 'hypernym')]
    else:
        raise AssertionError('Test not implemented for wordnet version {}'.format(wn.version))
    assert result == expected


def test_closure():
    if wn.version == '2.3.2':
        # wn['koer'] = ["Synset('koer.n.01')", "Synset('kaak.n.01')", "Synset('kutsikas.n.02')"]
        ss_koer = wn['koer'][0]
        expected = [Synset(wn, 55794)]
    elif wn.version == '2.5.0':
        # wn['koer'] = ["Synset('distsiplineerimatu.a.01')", "Synset('kodukoer.n.01')", "Synset('kaak.n.01')", "Synset('koer.n.03')"]
        ss_koer = wn['koer'][1]
        expected = [Synset(wn, 55794)]
    else:
        raise AssertionError('Test not implemented for wordnet version {}'.format(wn.version))
    synset = ss_koer
    result = synset.closure('holonym')
    assert result == expected

def test_lemmas():
    ss = Synset(wn, 6299)
    assert ss.lemmas == ['üllatamine']

def test_path_similarity_with_self():
    if wn.version == '2.3.2':
        # wn['koer'] = ["Synset('koer.n.01')", "Synset('kaak.n.01')", "Synset('kutsikas.n.02')"]
        ss_koer = wn['koer'][0]
    elif wn.version == '2.5.0':
        # wn['koer'] = ["Synset('distsiplineerimatu.a.01')", "Synset('kodukoer.n.01')", "Synset('kaak.n.01')", "Synset('koer.n.03')"]
        ss_koer = wn['koer'][1]
    else:
        raise AssertionError('Test not implemented for wordnet version {}'.format(wn.version))
    assert wn.path_similarity(ss_koer, ss_koer) == 1

def test_path_similarity_with_parent():
    if wn.version == '2.3.2':
        # wn['koer'] = ["Synset('koer.n.01')", "Synset('kaak.n.01')", "Synset('kutsikas.n.02')"]
        ss_koer = wn['koer'][0]
    elif wn.version == '2.5.0':
        # wn['koer'] = ["Synset('distsiplineerimatu.a.01')", "Synset('kodukoer.n.01')", "Synset('kaak.n.01')", "Synset('koer.n.03')"]
        ss_koer = wn['koer'][1]
    else:
        raise AssertionError('Test not implemented for wordnet version {}'.format(wn.version))
    target_synset = wn['koduloom'][0]
    assert wn.path_similarity(ss_koer, target_synset) == 1/2

def test_path_similarity_with_unreachable():
    ss_koer = wn['koer'][0]
    synset = wn['laulma'][0]
    target_synset = ss_koer
    assert wn.path_similarity(synset, target_synset) is None
