import pytest

from estnltk.rewriting import RegexRewriter
from estnltk.rewriting.rewriting import Rewritable


def test_regex_rewriter():
    r = RegexRewriter(
        [
            ('aa', 'a')
        ]
    )

    assert r.rewrite('aa') == 'a'
    assert r.rewrite('aaa') == 'aa'

    #conditional rewriting
    assert r.if_(True).rewrite('aaa') == 'aa'
    assert r.if_(False).rewrite('aaa') == 'aaa'



def test_regex_rewriter_until_stable():
    r = RegexRewriter(
        [
            ('aa', 'a')
        ]
    )

    assert r.rewrite_until_stable('aaa') == 'a'

    with pytest.raises(AssertionError):
        r.rewrite_until_stable('aaaaaaaaaa', limit=2)

    assert r.rewrite_until_stable('aaaaaaaaaa', limit=2, fail_silently=True) == 'aaa'

    #conditional rewriting
    assert r.if_(True).rewrite_until_stable('aaaaaaaaaa', limit=2, fail_silently=True) == 'aaa'
    assert r.if_(False).rewrite_until_stable('aaaaaaaaaa', limit=2, fail_silently=True) == 'aaaaaaaaaa'


def test_rewriting_attribute():
    class Test(Rewritable):
        def __init__(self):
            self.a = '123'
            self.b = 'abc'

    rewritable_attrs = Test()

    rewritable_attrs.rewrite_attribute('a', RegexRewriter([('\d', 'X')]))
    assert rewritable_attrs.a == 'XXX'


