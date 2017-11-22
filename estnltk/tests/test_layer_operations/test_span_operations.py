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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    
    #assert spanlist_1.touching_right(spanlist_2)
    #assert span6.touching_left(spanlist_2)
    #assert spanlist_1.touching_right(span4)


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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.hovering_right(spanlist_3)
    #assert span6.hovering_left(spanlist_1)
    #assert spanlist_2.hovering_right(span7)


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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.right(spanlist_3)
    #assert span6.left(spanlist_1)
    #assert spanlist_1.right(span4)
    #assert not spanlist_2.right(span4)


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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_21 = SpanList()
    #spanlist_21.spans = [span4]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.nested(span3)
    #assert not spanlist_1.nested(span34)
    #assert spanlist_2.nested(span4)
    #assert not spanlist_3.nested(span6)
    
    #assert spanlist_2.nested(spanlist_21)
    #assert not spanlist_1.nested(spanlist_2)


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
    
    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_21 = SpanList()
    #spanlist_21.spans = [span4]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.nested_aligned_right(span3)
    #assert not spanlist_1.nested_aligned_right(span34)
    #assert spanlist_2.nested_aligned_left(span4)
    #assert not spanlist_3.nested_aligned_right(span6)
    
    #assert spanlist_2.nested_aligned_left(spanlist_21)
    #assert not spanlist_1.nested_aligned_right(spanlist_2)


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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_21 = SpanList()
    #spanlist_21.spans = [span3, span4]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.overlapping_right(span34)
    #assert not spanlist_1.overlapping_right(span4)
    #assert spanlist_2.overlapping_left(span34)
    #assert not spanlist_3.overlapping_left(span6)
    
    #assert spanlist_2.overlapping_left(spanlist_21)
    #assert spanlist_1.overlapping_right(spanlist_21)
    #assert not spanlist_1.overlapping_right(spanlist_2)


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
    
    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1, span2, span3]
    #spanlist_2 = SpanList()
    #spanlist_2.spans = [span4, span5]
    #spanlist_21 = SpanList()
    #spanlist_21.spans = [span3, span4]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.conflict(span34)
    #assert not spanlist_1.conflict(span4)
    #assert spanlist_2.conflict(span34)
    #assert not spanlist_3.conflict(span6)
    #assert not spanlist_2.conflict(span3)
    
    #assert spanlist_2.conflict(spanlist_21)
    #assert spanlist_1.conflict(spanlist_21)
    #assert not spanlist_2.conflict(spanlist_1)
    #assert not spanlist_1.conflict(spanlist_2)


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

    # Test on SpanList-s
    #spanlist_1 = SpanList()
    #spanlist_1.spans = [span1]
    #spanlist_20 = SpanList()
    #spanlist_20.spans = [span4, span5]
    #spanlist_21 = SpanList()
    #spanlist_21.spans = [span4, span5]
    #spanlist_3 = SpanList()
    #spanlist_3.spans = [span7]
    
    #assert spanlist_1.equal(span1)
    #assert spanlist_20.equal(spanlist_21)
    #assert not spanlist_21.equal(span4)
    #assert not spanlist_21.equal(span34)
    #assert spanlist_3.equal(span7)
    #assert not spanlist_3.equal(span56)

# --------------------------------------------------------------------------

from estnltk.text import Layer
from estnltk.layer_operations.intersections import iterate_intersecting_pairs


def test_yield_spanlist_intersections():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    # Test Spans
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
    
    spanlist = SpanList()
    spanlist.add_span(span1)
    spanlist.add_span(span2)
    spanlist.add_span(span3)
    spanlist.add_span(span23)
    spanlist.add_span(span4)
    spanlist.add_span(span34)
    spanlist.add_span(span5)
    spanlist.add_span(span6)
    spanlist.add_span(span56)
    spanlist.add_span(span7)
    spanlist.add_span(span67)
    
    intersections = list( iterate_intersecting_pairs(spanlist) )
    intersect_texts = \
        [(text[a.start:a.end],text[b.start:b.end]) for a, b in intersections ]
    #print( intersect_texts )
    assert intersect_texts == \
        [('kaks', 'kaks kolm'), ('kaks kolm', 'kolm'), ('kaks kolm', 'kolmneli'), ('kolm', 'kolmneli'),\
         ('kolmneli', 'neli'), ('viis', 'viiskuus'), ('viiskuus', 'kuus'), ('viiskuus', 'kuus seitse'),\
         ('kuus', 'kuus seitse'), ('kuus seitse', 'seitse')]


def test_yield_no_spanlist_intersections():
    # Example text:
    text = 'üks kaks'
    
    # Test items
    span1  = Span(start=0, end=3)  # üks
    span2  = Span(start=4, end=8)  # kaks 
    spanlist = SpanList()
    spanlist.add_span(span1)
    spanlist.add_span(span2)
    
    intersections = list( iterate_intersecting_pairs(spanlist) )
    intersect_texts = [ (text[a.start:a.end],text[b.start:b.end]) for a, b in intersections ]
    assert intersect_texts == []


def test_yield_layer_intersections():
    # Example text:
    text = Text('üks kaks kolmneli viiskuus seitse')
    text.tag_layer(['words'])
    
    # Test Spans
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

    layer = Layer(name='test_layer')
    layer.add_span(span1)
    layer.add_span(span2)
    layer.add_span(span3)
    layer.add_span(span23)
    layer.add_span(span4)
    layer.add_span(span34)
    layer.add_span(span5)
    layer.add_span(span6)
    layer.add_span(span56)
    layer.add_span(span7)
    layer.add_span(span67)
    text['test_layer'] = layer
    
    intersections   = list( iterate_intersecting_pairs( text['test_layer'] ) )
    intersect_texts = [ (a.text,b.text) for a, b in intersections ]
    #print( intersect_texts )
    assert intersect_texts == \
        [('kaks', 'kaks kolm'), ('kaks kolm', 'kolm'), ('kaks kolm', 'kolmneli'), ('kolm', 'kolmneli'),\
         ('kolmneli', 'neli'), ('viis', 'viiskuus'), ('viiskuus', 'kuus'), ('viiskuus', 'kuus seitse'),\
         ('kuus', 'kuus seitse'), ('kuus seitse', 'seitse')]
