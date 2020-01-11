import pytest
from estnltk import ElementaryBaseSpan
from estnltk import EnvelopingBaseSpan


def test_constructors():
    base_span = EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(8, 12)])
    with pytest.raises(ValueError, match="enveloped components must be sorted and must not overlap"):
        base_span = EnvelopingBaseSpan([ElementaryBaseSpan(8, 12), ElementaryBaseSpan(0, 4)])
