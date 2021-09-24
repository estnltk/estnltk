from estnltk_core import ElementaryBaseSpan, Span
from estnltk_core.layer.span_operations import touching_right
from estnltk_core.layer.span_operations import touching_left
from estnltk_core.layer.span_operations import hovering_right
from estnltk_core.layer.span_operations import hovering_left
from estnltk_core.layer.span_operations import right
from estnltk_core.layer.span_operations import left
from estnltk_core.layer.span_operations import nested
from estnltk_core.layer.span_operations import equal
from estnltk_core.layer.span_operations import nested_aligned_right
from estnltk_core.layer.span_operations import nested_aligned_left
from estnltk_core.layer.span_operations import overlapping_left
from estnltk_core.layer.span_operations import overlapping_right
from estnltk_core.layer.span_operations import conflict


def test_touching_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    # Test on Spans
    span1 = Span(base_span=ElementaryBaseSpan(start= 0, end= 3), layer=None)  # üks
    span2 = Span(base_span=ElementaryBaseSpan(start= 4, end= 8), layer=None)  # kaks
    span3 = Span(base_span=ElementaryBaseSpan(start= 9, end=13), layer=None)  # kolm
    span4 = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span5 = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6 = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span7 = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    
    assert touching_right(span3, span4)
    assert touching_right(span5, span6)
    
    assert touching_left(span4, span3)
    assert touching_left(span6, span5)
    
    assert not touching_left(span1, span2)
    assert not touching_left(span3, span4)


def test_hovering_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'

    # Test on Spans
    span1 = Span(base_span=ElementaryBaseSpan(start= 0, end= 3), layer=None)  # üks
    span2 = Span(base_span=ElementaryBaseSpan(start= 4, end= 8), layer=None)  # kaks
    span3 = Span(base_span=ElementaryBaseSpan(start= 9, end=13), layer=None)  # kolm
    span4 = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span5 = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6 = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span7 = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    
    assert hovering_right(span1, span2)
    assert not hovering_right(span3, span4)
    
    assert hovering_left(span7, span6)
    assert hovering_left(span5, span4)
    
    assert not hovering_left(span6, span5)


def test_left_and_right_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    # Test on Spans
    span1 = Span(base_span=ElementaryBaseSpan(start=0,  end= 3), layer=None)  # üks
    span2 = Span(base_span=ElementaryBaseSpan(start=4,  end= 8), layer=None)  # kaks
    span3 = Span(base_span=ElementaryBaseSpan(start=9,  end=13), layer=None)  # kolm
    span4 = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span5 = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6 = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span7 = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    
    assert right(span1, span2)
    assert not right(span3, span1)
    
    assert left(span7, span6)
    assert left(span4, span3)
    
    assert not left(span6, span7)


def test_nested_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'

    # Test on Spans
    span1  = Span(base_span=ElementaryBaseSpan(start= 0, end= 3), layer=None)  # üks
    span2  = Span(base_span=ElementaryBaseSpan(start= 4, end= 8), layer=None)  # kaks
    span3  = Span(base_span=ElementaryBaseSpan(start= 9, end=13), layer=None)  # kolm
    span4  = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span34 = Span(base_span=ElementaryBaseSpan(start= 9, end=17), layer=None)  # kolmneli
    span5  = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6  = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span56 = Span(base_span=ElementaryBaseSpan(start=18, end=26), layer=None)  # viiskuus
    span7  = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    
    assert nested(span56, span6)
    assert not nested(span34, span5)
    
    assert nested(span34, span3)
    assert nested(span34, span4)
    
    assert not nested(span34, span5)


def test_nested_aligned_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])

    # Test on Spans
    span1  = Span(base_span=ElementaryBaseSpan(start= 0, end= 3), layer=None)  # üks
    span2  = Span(base_span=ElementaryBaseSpan(start= 4, end= 8), layer=None)  # kaks
    span3  = Span(base_span=ElementaryBaseSpan(start= 9, end=13), layer=None)  # kolm
    span4  = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span34 = Span(base_span=ElementaryBaseSpan(start=9,  end=17), layer=None)  # kolmneli
    span5  = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6  = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span56 = Span(base_span=ElementaryBaseSpan(start=18, end=26), layer=None)  # viiskuus
    span7  = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse

    assert nested_aligned_right(span56, span6)
    assert nested_aligned_right(span34, span4)
    assert not nested_aligned_right(span34, span5)
    assert not nested_aligned_right(span34, span7)
    
    assert nested_aligned_left(span34, span3)
    assert not nested_aligned_left(span34, span4)


def test_overlapping_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'

    # Test on Spans
    span1  = Span(base_span=ElementaryBaseSpan(start=0,  end= 3), layer=None)  # üks
    span2  = Span(base_span=ElementaryBaseSpan(start=4,  end= 8), layer=None)  # kaks
    span3  = Span(base_span=ElementaryBaseSpan(start=9,  end=13), layer=None)  # kolm
    span23 = Span(base_span=ElementaryBaseSpan(start=4,  end=13), layer=None)  # 'kaks kolm'
    span4  = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span34 = Span(base_span=ElementaryBaseSpan(start=9,  end=17), layer=None)  # kolmneli
    span5  = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6  = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span56 = Span(base_span=ElementaryBaseSpan(start=18, end=26), layer=None)  # viiskuus
    span7  = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    span67 = Span(base_span=ElementaryBaseSpan(start=22, end=33), layer=None)  # 'kuus seitse'

    assert overlapping_left(span34, span23)
    assert not overlapping_left(span34, span3)

    assert overlapping_right(span56, span67)
    assert not overlapping_right(span56, span6)


def test_conflict_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'

    # Test on Spans
    span1  = Span(base_span=ElementaryBaseSpan(start=0,  end= 3), layer=None)  # üks
    span2  = Span(base_span=ElementaryBaseSpan(start=4,  end= 8), layer=None)  # kaks
    span3  = Span(base_span=ElementaryBaseSpan(start=9,  end=13), layer=None)  # kolm
    span23 = Span(base_span=ElementaryBaseSpan(start=4,  end=13), layer=None)  # 'kaks kolm'
    span4  = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span34 = Span(base_span=ElementaryBaseSpan(start=9,  end=17), layer=None)  # kolmneli
    span5  = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6  = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span56 = Span(base_span=ElementaryBaseSpan(start=18, end=26), layer=None)  # viiskuus
    span7  = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    span67 = Span(base_span=ElementaryBaseSpan(start=22, end=33), layer=None)  # 'kuus seitse'
    
    assert conflict(span23, span34)
    assert conflict(span56, span67)
    assert conflict(span34, span3)
    assert conflict(span56, span6)
    assert not conflict(span3, span4)
    assert not conflict(span6, span5)
    assert not conflict(span34, span2)
    assert not conflict(span34, span56)
    assert not conflict(span7, span56)


def test_equal_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    # Test on Spans
    span1  = Span(base_span=ElementaryBaseSpan(start=0,  end= 3), layer=None)  # üks
    span2  = Span(base_span=ElementaryBaseSpan(start=4,  end= 8), layer=None)  # kaks
    span3  = Span(base_span=ElementaryBaseSpan(start=9,  end=13), layer=None)  # kolm
    span23 = Span(base_span=ElementaryBaseSpan(start=4,  end=13), layer=None)  # 'kaks kolm'
    span4  = Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None)  # neli
    span34 = Span(base_span=ElementaryBaseSpan(start=9,  end=17), layer=None)  # kolmneli
    span43 = Span(base_span=ElementaryBaseSpan(start=9,  end=17), layer=None)  # kolmneli
    span5  = Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None)  # viis
    span6  = Span(base_span=ElementaryBaseSpan(start=22, end=26), layer=None)  # kuus
    span56 = Span(base_span=ElementaryBaseSpan(start=18, end=26), layer=None)  # viiskuus
    span7  = Span(base_span=ElementaryBaseSpan(start=27, end=33), layer=None)  # seitse
    span67 = Span(base_span=ElementaryBaseSpan(start=22, end=33), layer=None)  # 'kuus seitse'
    
    assert equal(span34, span43)
    assert not equal(span34, span56)
    assert not equal(span34, span3)
