from estnltk.rewriting.premorph.morph_analyzed_token import MorphAnalyzedToken

def test_MorphAnalyzedToken():
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