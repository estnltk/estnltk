from estnltk import Text
from estnltk.text import Span, SpanList

def test_touching_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1 = Span(start=0, end=3)    # üks
    span2 = Span(start=4, end=8)    # kaks 
    span3 = Span(start=9, end=13)   # kolm
    span4 = Span(start=13, end=17)  # neli
    span5 = Span(start=18, end=22)  # viis 
    span6 = Span(start=22, end=26)  # kuus
    span7 = Span(start=27, end=33)  # seitse
    
    assert span3.touching_right(span4)
    assert span5.touching_right(span6)
    
    assert span4.touching_left(span3)
    assert span6.touching_left(span5)
    
    assert not span1.touching_left(span2)
    assert not span3.touching_left(span4)


def test_hovering_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1 = Span(start=0, end=3)    # üks
    span2 = Span(start=4, end=8)    # kaks 
    span3 = Span(start=9, end=13)   # kolm
    span4 = Span(start=13, end=17)  # neli
    span5 = Span(start=18, end=22)  # viis 
    span6 = Span(start=22, end=26)  # kuus
    span7 = Span(start=27, end=33)  # seitse
    
    assert span1.hovering_right(span2)
    assert not span3.hovering_right(span4) 
    
    assert span7.hovering_left(span6)
    assert span5.hovering_left(span4)
    
    assert not span6.hovering_left(span5)


def test_left_and_right_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1 = Span(start=0, end=3)    # üks
    span2 = Span(start=4, end=8)    # kaks 
    span3 = Span(start=9, end=13)   # kolm
    span4 = Span(start=13, end=17)  # neli
    span5 = Span(start=18, end=22)  # viis 
    span6 = Span(start=22, end=26)  # kuus
    span7 = Span(start=27, end=33)  # seitse
    
    assert span1.right(span2)
    assert not span3.right(span1) 
    
    assert span7.left(span6)
    assert span4.left(span3)
    
    assert not span6.left(span7)


def test_nested_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1  = Span(start=0, end=3)    # üks
    span2  = Span(start=4, end=8)    # kaks 
    span3  = Span(start=9, end=13)   # kolm
    span4  = Span(start=13, end=17)  # neli
    span34 = Span(start=9, end=17)   # kolmneli
    span5  = Span(start=18, end=22)  # viis 
    span6  = Span(start=22, end=26)  # kuus
    span56 = Span(start=18, end=26)  # viiskuus
    span7  = Span(start=27, end=33)  # seitse
    
    assert span56.nested(span6)
    assert not span34.nested(span5) 
    
    assert span34.nested(span3)
    assert span34.nested(span4)
    
    assert not span34.nested(span5)


def test_nested_aligned_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1  = Span(start=0, end=3)    # üks
    span2  = Span(start=4, end=8)    # kaks 
    span3  = Span(start=9, end=13)   # kolm
    span4  = Span(start=13, end=17)  # neli
    span34 = Span(start=9, end=17)   # kolmneli
    span5  = Span(start=18, end=22)  # viis 
    span6  = Span(start=22, end=26)  # kuus
    span56 = Span(start=18, end=26)  # viiskuus
    span7  = Span(start=27, end=33)  # seitse
    
    assert span56.nested_aligned_right(span6)
    assert span34.nested_aligned_right(span4)
    assert not span34.nested_aligned_right(span5)
    assert not span34.nested_aligned_right(span7)
    
    assert span34.nested_aligned_left(span3)
    assert not span34.nested_aligned_left(span4)


def test_overlapping_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1  = Span(start=0, end=3)    # üks
    span2  = Span(start=4, end=8)    # kaks 
    span3  = Span(start=9, end=13)   # kolm
    span23 = Span(start=4, end=13)   # 'kaks kolm'
    span4  = Span(start=13, end=17)  # neli
    span34 = Span(start=9, end=17)   # kolmneli
    span5  = Span(start=18, end=22)  # viis 
    span6  = Span(start=22, end=26)  # kuus
    span56 = Span(start=18, end=26)  # viiskuus
    span7  = Span(start=27, end=33)  # seitse
    span67 = Span(start=22, end=33)  # 'kuus seitse'

    assert span34.overlapping_left(span23)
    assert not span34.overlapping_left(span3)

    assert span56.overlapping_right(span67)
    assert not span56.overlapping_right(span6)


def test_conflict_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1  = Span(start=0, end=3)    # üks
    span2  = Span(start=4, end=8)    # kaks 
    span3  = Span(start=9, end=13)   # kolm
    span23 = Span(start=4, end=13)   # 'kaks kolm'
    span4  = Span(start=13, end=17)  # neli
    span34 = Span(start=9, end=17)   # kolmneli
    span5  = Span(start=18, end=22)  # viis 
    span6  = Span(start=22, end=26)  # kuus
    span56 = Span(start=18, end=26)  # viiskuus
    span7  = Span(start=27, end=33)  # seitse
    span67 = Span(start=22, end=33)  # 'kuus seitse'
    
    assert span23.conflict(span34)
    assert span56.conflict(span67)
    assert span34.conflict(span3)
    assert span56.conflict(span6)
    assert not span3.conflict(span4)
    assert not span6.conflict(span5)
    assert not span34.conflict(span2)
    assert not span34.conflict(span56)
    assert not span7.conflict(span56)


def test_equal_positions():
    # Example text: 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Test on Spans
    span1  = Span(start=0, end=3)    # üks
    span2  = Span(start=4, end=8)    # kaks 
    span3  = Span(start=9, end=13)   # kolm
    span23 = Span(start=4, end=13)   # 'kaks kolm'
    span4  = Span(start=13, end=17)  # neli
    span34 = Span(start=9, end=17)   # kolmneli
    span43 = Span(end=17, start=9)   # kolmneli
    span5  = Span(start=18, end=22)  # viis 
    span6  = Span(start=22, end=26)  # kuus
    span56 = Span(start=18, end=26)  # viiskuus
    span7  = Span(start=27, end=33)  # seitse
    span67 = Span(start=22, end=33)  # 'kuus seitse'
    
    assert span34.equal(span43)
    assert not span34.equal(span56)
    assert not span34.equal(span3)

