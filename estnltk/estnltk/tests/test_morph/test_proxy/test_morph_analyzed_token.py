from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken


def test_public():
    t0 = MorphAnalyzedToken('lfjdsdq')
    t1 = MorphAnalyzedToken('plekist')
    t2 = MorphAnalyzedToken('ning')
    t3 = MorphAnalyzedToken('temale')

    assert t1.text == 'plekist'

    assert not t0.is_word
    assert t1.is_word
    assert t2.is_word
    assert t3.is_word

    assert not t0.is_conjunction
    assert not t1.is_conjunction
    assert t2.is_conjunction
    assert not t3.is_conjunction
    
    assert not t0.is_pronoun
    assert not t1.is_pronoun
    assert not t2.is_pronoun
    assert t3.is_pronoun
    
    assert t0.normal is t0
    assert t1.normal is t1
    assert t2.normal is t2
    assert t3.normal is t3

def test_magic():
    t1 = MorphAnalyzedToken('plekk')
    t2 = MorphAnalyzedToken('plekk')
    assert t1 == t2
    assert 'ek' in t1
    assert len(t1) == 5
    assert str(t1) == 'plekk'
    assert repr(t1) == "MorphAnalyzedToken('plekk')"


def test_normal():
    t = MorphAnalyzedToken('plekk')
    assert t == 'plekk'
    assert t.normal is t

    assert MorphAnalyzedToken('lil-le-pott').normal == 'lillepott'
    assert MorphAnalyzedToken('lille-pott').normal == 'lille-pott'

    t = MorphAnalyzedToken('maa-alune')
    assert t.normal is t
    assert MorphAnalyzedToken('maa-a-lu-ne').normal == 'maa-alune'
    assert MorphAnalyzedToken('m-m-m-maa-alune').normal == 'maa-alune'

    assert MorphAnalyzedToken('v-v-v-ve-ve-ve-vere-taoline').normal == 'vere-taoline'
    assert MorphAnalyzedToken('v-v-v-ve-ve-ve-vere-tao-li-ne').normal == 'veretaoline'

    assert MorphAnalyzedToken('ma-sina').normal == 'masina'
    t = MorphAnalyzedToken('ma-tegevusnimi')
    assert t.normal is t