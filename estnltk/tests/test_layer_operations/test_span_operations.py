from estnltk import Text
from estnltk.text import Span, SpanList
from estnltk.layer_operations.span_positions import *

def test_touching_operations():
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
    
    assert touching_right(span3, span4)
    assert touching_right(span5, span6) 
    
    assert touching_left(span4, span3)
    assert touching_left(span6, span5)
    
    assert not touching_left(span1, span2)
    assert not touching_left(span3, span4)

    # Test on SpanList-s
    
    spanlist_1 = SpanList()
    spanlist_1.spans = [span1, span2, span3]
    spanlist_2 = SpanList()
    spanlist_2.spans = [span4, span5]
    
    assert touching_right(spanlist_1, spanlist_2)
    assert touching_left(span6, spanlist_2)
    assert touching_right(spanlist_1, span4)


def test_hovering_operations():
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
    
    assert hovering_right(span1, span2)
    assert not hovering_right(span3, span4) 
    
    assert hovering_left(span7, span6)
    assert hovering_left(span5, span4)
    
    assert not hovering_left(span6, span5)

    # Test on SpanList-s
    
    spanlist_1 = SpanList()
    spanlist_1.spans = [span1, span2, span3]
    spanlist_2 = SpanList()
    spanlist_2.spans = [span4, span5]
    spanlist_3 = SpanList()
    spanlist_3.spans = [span7]
    
    assert hovering_right(spanlist_1, spanlist_3)
    assert hovering_left(span6, spanlist_1)
    assert hovering_right(spanlist_2, span7)


def test_left_and_right_operations():
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
    
    assert right(span1, span2)
    assert not right(span3, span1) 
    
    assert left(span7, span6)
    assert left(span4, span3)
    
    assert not left(span6, span7)

    # Test on SpanList-s
    
    spanlist_1 = SpanList()
    spanlist_1.spans = [span1, span2, span3]
    spanlist_2 = SpanList()
    spanlist_2.spans = [span4, span5]
    spanlist_3 = SpanList()
    spanlist_3.spans = [span7]
    
    assert right(spanlist_1, spanlist_3)
    assert left(span6, spanlist_1)
    assert right(spanlist_1, span4)
    assert not right(spanlist_2, span4)
