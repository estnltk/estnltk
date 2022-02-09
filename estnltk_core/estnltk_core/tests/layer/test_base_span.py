import pytest

from estnltk_core.layer.base_span import BaseSpan
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_span import EnvelopingBaseSpan


def test_base_span():
    span = BaseSpan((1,2), 0, 3, 8)
    with pytest.raises(AttributeError):
        span.illegal_attribute = None

    with pytest.raises(NotImplementedError):
        span.flatten()


def test_elementary_base_span():
    with pytest.raises(TypeError):
        ElementaryBaseSpan('2', 3)

    with pytest.raises(TypeError):
        ElementaryBaseSpan(2, '3')

    with pytest.raises(ValueError):
        ElementaryBaseSpan(-2, 3)

    with pytest.raises(ValueError):
        ElementaryBaseSpan(3, 2)

    span = ElementaryBaseSpan(23, 30)
    assert span.start == 23
    assert span.end == 30
    assert span.level == 0

    with pytest.raises(AttributeError):
        span.illegal_attribute = None

    # Test that BaseSpan's are immutable
    with pytest.raises(Exception):
        span.start = 1
    with pytest.raises(Exception):
        span.level = 5

    assert span.flatten() == ((23, 30),)

    assert span.raw() == (23, 30)

    assert ElementaryBaseSpan(5, 8) < ElementaryBaseSpan(5, 9)
    assert ElementaryBaseSpan(5, 8) < ElementaryBaseSpan(6, 8)
    assert ElementaryBaseSpan(1, 3) < ElementaryBaseSpan(6, 8)
    assert not (ElementaryBaseSpan(1, 3) == ElementaryBaseSpan(6, 8))

    assert span == span
    assert span <= span
    assert span >= span
    assert not span < span

    with pytest.raises(TypeError):
        span <= (23, 30)

    eb_span_2 = ElementaryBaseSpan(23, 30)

    assert span is not eb_span_2
    assert span == eb_span_2
    assert hash(span) == hash(eb_span_2)
    assert not span < eb_span_2
    assert not span > eb_span_2

    assert repr(span) == 'ElementaryBaseSpan(23, 30)'


def test_enveloping_base_span():

    with pytest.raises(TypeError):
        EnvelopingBaseSpan(23)

    with pytest.raises(ValueError):
        EnvelopingBaseSpan([])

    with pytest.raises(TypeError):
        EnvelopingBaseSpan([(1,2)])

    with pytest.raises(ValueError, match="enveloped components must be sorted and must not overlap"):
        EnvelopingBaseSpan([ElementaryBaseSpan(0, 5), ElementaryBaseSpan(4, 8)])

    with pytest.raises(ValueError, match="enveloped components must be sorted and must not overlap"):
        base_span = EnvelopingBaseSpan([ElementaryBaseSpan(8, 12), ElementaryBaseSpan(0, 4)])

    with pytest.raises(ValueError, match="enveloped components must have the same levels"):
        EnvelopingBaseSpan([EnvelopingBaseSpan([ElementaryBaseSpan(0, 3)]), ElementaryBaseSpan(4, 8)])

    el_span = ElementaryBaseSpan(4, 10)
    env_span = EnvelopingBaseSpan([el_span])
    assert el_span is not env_span
    assert el_span != env_span
    assert env_span == env_span
    assert env_span <= env_span
    assert not env_span < env_span
    assert hash(el_span) != (env_span)
    assert el_span in env_span
    assert el_span.start == env_span.start
    assert el_span.end == env_span.end

    span = EnvelopingBaseSpan(
            [EnvelopingBaseSpan(
                    [EnvelopingBaseSpan(
                            [EnvelopingBaseSpan(
                                    [ElementaryBaseSpan(0, 2), ElementaryBaseSpan(2, 5)])]),
                        EnvelopingBaseSpan(
                                [EnvelopingBaseSpan(
                                        [ElementaryBaseSpan(6, 7), ElementaryBaseSpan(8, 9)])])
                     ]
            )])
    assert span.start == 0
    assert span.end == 9
    assert span.flatten() == ((0, 2), (2, 5), (6, 7), (8, 9))
    assert span.raw() == (((((0, 2), (2, 5)),), (((6, 7), (8, 9)),)),)
    assert span.level == 4
    assert span[0].level == 3
    assert span[0][0].level == 2
    assert span[0][0][0].level == 1
    assert span[0][0][0][0].level == 0
    assert len(span) == 1

    with pytest.raises(TypeError):
        span <= (23, 30)

    span = EnvelopingBaseSpan((ElementaryBaseSpan(4, 10), ElementaryBaseSpan(11, 20)))
    assert span.start == 4
    assert span.end == 20
    assert span.level == 1
    assert span == span
    assert span <= span

    with pytest.raises(AttributeError):
        span.illegal_attribute = None

    # Test that BaseSpan's are immutable
    with pytest.raises(Exception):
        span.start = 1
    with pytest.raises(Exception):
        span.level = 5

    assert span.flatten() == ((4, 10), (11, 20))
    assert span.raw() == ((4, 10), (11, 20))

    # order by start
    assert EnvelopingBaseSpan([ElementaryBaseSpan(10, 45)]) < EnvelopingBaseSpan([ElementaryBaseSpan(11, 15),
                                                                                  ElementaryBaseSpan(20, 25),
                                                                                  ElementaryBaseSpan(30, 35)])
    # order by end
    assert EnvelopingBaseSpan([ElementaryBaseSpan(10, 15),
                               ElementaryBaseSpan(20, 25),
                               ElementaryBaseSpan(30, 34)]) < EnvelopingBaseSpan([ElementaryBaseSpan(10, 15),
                                                                                  ElementaryBaseSpan(19, 25), 
                                                                                  ElementaryBaseSpan(30, 35)])
    # order by first base span
    assert EnvelopingBaseSpan([ElementaryBaseSpan(10, 15),
                               ElementaryBaseSpan(20, 25),
                               ElementaryBaseSpan(30, 35)]) < EnvelopingBaseSpan([ElementaryBaseSpan(10, 35)])
    # order by second base span
    assert EnvelopingBaseSpan([ElementaryBaseSpan(10, 15),
                               ElementaryBaseSpan(19, 25),
                               ElementaryBaseSpan(30, 35)]) < EnvelopingBaseSpan([ElementaryBaseSpan(10, 15),
                                                                                  ElementaryBaseSpan(20, 25),
                                                                                  ElementaryBaseSpan(30, 35)])

    assert list(span) == [ElementaryBaseSpan(4, 10), ElementaryBaseSpan(11, 20)]

    span_2 = EnvelopingBaseSpan([ElementaryBaseSpan(4, 10), ElementaryBaseSpan(11, 20)])

    assert span is not span_2
    assert span == span_2
    assert hash(span) == hash(span_2)
    assert not span < span_2
    assert not span > span_2
    assert len(span_2) == 2

    assert repr(span) == 'EnvelopingBaseSpan((ElementaryBaseSpan(4, 10), ElementaryBaseSpan(11, 20)))'

