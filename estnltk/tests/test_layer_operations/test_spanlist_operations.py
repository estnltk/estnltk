from estnltk import Text
from estnltk.text import Span, SpanList, Layer

from estnltk.layer_operations.consecutive import iterate_consecutive_spans
from estnltk.layer_operations.consecutive import iterate_touching_spans
from estnltk.layer_operations.consecutive import iterate_hovering_spans
from estnltk.layer_operations.consecutive import iterate_starting_spans
from estnltk.layer_operations.consecutive import iterate_ending_spans

from estnltk.layer_operations.intersections import iterate_intersecting_spans
from estnltk.layer_operations.intersections import iterate_nested_spans
from estnltk.layer_operations.intersections import iterate_equal_spans
from estnltk.layer_operations.intersections import iterate_overlapping_spans

# --------------------- Iterate over hovering Spans in SpanList 

def test_iterate_hovering_spans_in_spanlist_1():
    # Example text:
    text = 'A B C D'
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))   # A
    spanlist.add_span(Span(start=2, end=3))   # B
    spanlist.add_span(Span(start=4, end=5))   # C
    spanlist.add_span(Span(start=6, end=7))   # D
    hovering = list( iterate_hovering_spans(spanlist) )
    expected_hovering_span_texts = \
        [('A', 'B'), ('B', 'C'), ('C', 'D')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


def test_iterate_hovering_spans_in_spanlist_2():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=3))   # üks
    spanlist.add_span(Span(start=4, end=8))   # kaks 
    spanlist.add_span(Span(start=9, end=13))  # kolm
    spanlist.add_span(Span(start=13, end=17)) # neli
    spanlist.add_span(Span(start=22, end=26)) # kuus
    spanlist.add_span(Span(start=18, end=22)) # viis 
    spanlist.add_span(Span(start=27, end=33)) # seitse
    hovering = list( iterate_hovering_spans(spanlist) )
    expected_hovering_span_texts = \
        [('üks', 'kaks'), ('kaks', 'kolm'), ('neli', 'viis'), ('kuus', 'seitse')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


def test_iterate_hovering_spans_in_spanlist_with_min_gap():
    # Example text:
    text = 'A  B C  D E'
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))     # A
    spanlist.add_span(Span(start=3, end=4))     # B
    spanlist.add_span(Span(start=5, end=6))     # C
    spanlist.add_span(Span(start=8, end=9))     # D
    spanlist.add_span(Span(start=10, end=11))   # E
    hovering = list( iterate_hovering_spans(spanlist, min_gap = 2) )
    expected_hovering_span_texts = \
        [('A', 'B'), ('C', 'D')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


# --------------------- Iterate over consecutive Spans in SpanList 

def test_iterate_consecutive_spans_in_spanlist():
    # Example text:
    text = 'üks kaks kolmneli viis'
    
    # Test on SpanList
    spanlist = SpanList(ambiguous = True)
    spanlist.add_span(Span(start=0, end=3))   # üks
    spanlist.add_span(Span(start=4, end=8))   # kaks 
    spanlist.add_span(Span(start=9, end=13))  # kolm
    spanlist.add_span(Span(start=4, end=13))  # 'kaks kolm'
    spanlist.add_span(Span(start=13, end=17)) # neli
    spanlist.add_span(Span(start=9, end=17))  # kolmneli
    spanlist.add_span(Span(start=18, end=22)) # viis 
    consecutive = list( iterate_consecutive_spans(spanlist) )
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'), \
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print( consecutive_span_texts )
    assert consecutive_span_texts == expected_consecutive_span_texts
    
    # Test on list of Spans
    spanlist = []
    spanlist.append(Span(start=9, end=13))  # kolm
    spanlist.append(Span(start=0, end=3))   # üks
    spanlist.append(Span(start=4, end=8))   # kaks 
    spanlist.append(Span(start=13, end=17)) # neli
    spanlist.append(Span(start=9, end=17))  # kolmneli
    spanlist.append(Span(start=18, end=22)) # viis 
    spanlist.append(Span(start=4, end=13))  # 'kaks kolm'
    consecutive = list( iterate_consecutive_spans(spanlist) )
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print( consecutive_span_texts )
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'), \
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    assert consecutive_span_texts == expected_consecutive_span_texts


def test_iterate_consecutive_spans_in_spanlist_with_max_gap():
    # Example text:
    text = 'A  B    CD  E    F'
    
    # Test on SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))   # A
    spanlist.add_span(Span(start=3, end=4))   # B
    spanlist.add_span(Span(start=8, end=9))   # C
    spanlist.add_span(Span(start=8, end=10))  # CD
    spanlist.add_span(Span(start=9, end=10))  # D
    spanlist.add_span(Span(start=12, end=13)) # E
    spanlist.add_span(Span(start=17, end=18)) # F
    
    consecutive = list( iterate_consecutive_spans(spanlist, max_gap=2) )
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print( consecutive_span_texts )
    expected_consecutive_span_texts = \
        [('A', 'B'), ('C', 'D'), ('CD', 'E'), ('D', 'E')]
    assert consecutive_span_texts == expected_consecutive_span_texts


# --------------------- Iterate over touching Spans in SpanList 

def test_iterate_touching_spans_in_spanlist_1():
    # Example text:
    text = 'AB'
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span( Span(start=0, end=1) )  # A
    spanlist.add_span( Span(start=1, end=2) )  # B
    spanlist.add_span( Span(start=0, end=2) )  # AB
    
    touching = list( iterate_touching_spans(spanlist) )
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('A', 'B')]
    assert touching_span_texts == expected_touching_span_texts


def test_iterate_touching_spans_in_spanlist_2():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=3))   # üks
    spanlist.add_span(Span(start=4, end=8))   # kaks 
    spanlist.add_span(Span(start=9, end=13))  # kolm
    spanlist.add_span(Span(start=13, end=17)) # neli
    spanlist.add_span(Span(start=22, end=26)) # kuus
    spanlist.add_span(Span(start=18, end=22)) # viis 
    spanlist.add_span(Span(start=27, end=33)) # seitse
    
    touching = list( iterate_touching_spans(spanlist) )
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('kolm', 'neli'), ('viis', 'kuus')]
    assert touching_span_texts == expected_touching_span_texts


def test_iterate_touching_spans_in_spanlist_3():
    # Example text:
    text = 'üks kaks kolmneli viis'
    
    # Create a SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=3))   # üks
    spanlist.add_span(Span(start=4, end=8))   # kaks 
    spanlist.add_span(Span(start=9, end=13))  # kolm
    spanlist.add_span(Span(start=4, end=13))  # 'kaks kolm'
    spanlist.add_span(Span(start=13, end=17)) # neli
    spanlist.add_span(Span(start=9, end=17))  # kolmneli
    spanlist.add_span(Span(start=18, end=22)) # viis 
    touching = list( iterate_touching_spans(spanlist) )
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('kaks kolm', 'neli'), ('kolm', 'neli')]
    assert touching_span_texts == expected_touching_span_texts

# --------------------- Iterate over starting and ending spans


def test_iterate_terminal_spans():
    s1 = Span(0,  3)
    s2 = Span(1, 10)
    s3 = Span(5,  7)
    s4 = Span(5,  7)
    s5 = Span(8,  9)

    span_list = SpanList()
    assert tuple(iterate_starting_spans(span_list)) == ()
    assert tuple(iterate_ending_spans(span_list)) == ()

    span_list.add_span(s3)
    assert tuple(iterate_starting_spans(span_list)) == (s3,)
    assert tuple(iterate_ending_spans(span_list)) == (s3,)

    span_list.add_span(s4)
    assert tuple(iterate_starting_spans(span_list)) == (s3, s4)
    assert tuple(iterate_ending_spans(span_list)) == (s3, s4)

    span_list.add_span(s1)
    span_list.add_span(s5)
    assert tuple(iterate_starting_spans(span_list)) == (s1,)
    assert tuple(iterate_ending_spans(span_list)) == (s5,)

    span_list.add_span(s2)
    assert tuple(iterate_starting_spans(span_list)) == (s1,s2)
    assert tuple(iterate_ending_spans(span_list)) == (s2, s5)


# --------------------- Iterate over intersecting Spans in SpanList 

def test_yield_spanlist_intersections():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    # Test on SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=3))   # üks
    spanlist.add_span(Span(start=4, end=8))   # kaks 
    spanlist.add_span(Span(start=9, end=13))  # kolm
    spanlist.add_span(Span(start=4, end=13))  # 'kaks kolm'
    spanlist.add_span(Span(start=13, end=17)) # neli
    spanlist.add_span(Span(start=9, end=17))  # kolmneli
    spanlist.add_span(Span(start=18, end=22)) # viis 
    spanlist.add_span(Span(start=22, end=26)) # kuus
    spanlist.add_span(Span(start=18, end=26)) # viiskuus
    spanlist.add_span(Span(start=27, end=33)) # seitse
    spanlist.add_span(Span(start=22, end=33)) # 'kuus seitse'
    
    intersections = list( iterate_intersecting_spans(spanlist) )
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
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=3))  # üks
    spanlist.add_span(Span(start=4, end=8))  # kaks 
    
    intersections = list( iterate_intersecting_spans(spanlist) )
    intersect_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in intersections ]
    assert intersect_texts == []


def test_yield_layer_intersections():
    # Example text:
    text = Text('üks kaks kolmneli viiskuus seitse')
    text.tag_layer(['words'])
    
    # Test Spans
    layer = Layer(name='test_layer')
    layer.add_span(Span(start=0, end=3))   # üks
    layer.add_span(Span(start=4, end=8))   # kaks 
    layer.add_span(Span(start=9, end=13))  # kolm
    layer.add_span(Span(start=4, end=13))  # 'kaks kolm'
    layer.add_span(Span(start=13, end=17)) # neli
    layer.add_span(Span(start=9, end=17))  # kolmneli
    layer.add_span(Span(start=18, end=22)) # viis 
    layer.add_span(Span(start=22, end=26)) # kuus
    layer.add_span(Span(start=18, end=26)) # viiskuus
    layer.add_span(Span(start=27, end=33)) # seitse
    layer.add_span(Span(start=22, end=33)) # 'kuus seitse'
    text['test_layer'] = layer
    
    intersections   = list( iterate_intersecting_spans( text['test_layer'].spans ) )
    intersect_texts = [ (a.text,b.text) for a, b in intersections ]
    #print( intersect_texts )
    assert intersect_texts == \
        [('kaks', 'kaks kolm'), ('kaks kolm', 'kolm'), ('kaks kolm', 'kolmneli'), ('kolm', 'kolmneli'),\
         ('kolmneli', 'neli'), ('viis', 'viiskuus'), ('viiskuus', 'kuus'), ('viiskuus', 'kuus seitse'),\
         ('kuus', 'kuus seitse'), ('kuus seitse', 'seitse')]


# --------------------- Iterate over nested Spans in SpanList 

def test_yield_spanlist_nested_positions():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))    # A
    spanlist.add_span(Span(start=2, end=3))    # B
    spanlist.add_span(Span(start=4, end=5))    # C
    spanlist.add_span(Span(start=5, end=6))    # D
    spanlist.add_span(Span(start=4, end=6))    # CD
    spanlist.add_span(Span(start=7, end=8))    # E
    spanlist.add_span(Span(start=8, end=9))    # F
    spanlist.add_span(Span(start=7, end=9))    # EF
    spanlist.add_span(Span(start=10, end=11))  # G

    nested = list( iterate_nested_spans( spanlist ) )
    nested_spans_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in nested ]
    #print( nested_spans_texts )
    assert nested_spans_texts == \
        [('C', 'CD'), ('CD', 'D'), ('E', 'EF'), ('EF', 'F')]


# --------------------- Iterate over overlapped Spans in SpanList

def test_yield_spanlist_overlapping_positions():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))    # A
    spanlist.add_span(Span(start=2, end=3))    # B
    spanlist.add_span(Span(start=4, end=5))    # C
    spanlist.add_span(Span(start=2, end=5))    # 'B C'
    spanlist.add_span(Span(start=5, end=6))    # D
    spanlist.add_span(Span(start=4, end=6))    # CD
    spanlist.add_span(Span(start=7, end=8))    # E
    spanlist.add_span(Span(start=8, end=9))    # F
    spanlist.add_span(Span(start=7, end=9))    # EF
    spanlist.add_span(Span(start=10, end=11))  # G
    spanlist.add_span(Span(start=8, end=11))   # 'F G'
    
    overlapping = list( iterate_overlapping_spans( spanlist ) )
    overlapping_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in overlapping ]
    #print( overlapping_texts )
    assert overlapping_texts == \
        [('B C', 'CD'), ('EF', 'F G')]


# --------------------- Iterate over equal Spans in SpanList

def test_equal_positions():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create SpanList
    spanlist = SpanList()
    spanlist.add_span(Span(start=0, end=1))    # A
    spanlist.add_span(Span(start=2, end=3))    # B
    spanlist.add_span(Span(start=4, end=5))    # C
    spanlist.add_span(Span(start=2, end=5))    # 'B C'
    spanlist.add_span(Span(start=5, end=6))    # D
    spanlist.add_span(Span(start=4, end=6))    # CD
    spanlist.add_span(Span(start=7, end=8))    # E
    spanlist.add_span(Span(end=6, start=4))    # CD
    spanlist.add_span(Span(start=8, end=9))    # F
    spanlist.add_span(Span(start=7, end=9))    # EF
    spanlist.add_span(Span(start=10, end=11))  # G
    spanlist.add_span(Span(start=8, end=11))   # 'F G'
    spanlist.add_span(Span(end=11, start=10))  # G
    
    equal_pos = list( iterate_equal_spans( spanlist ) )
    equal_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in equal_pos ]
    #print( equal_texts )
    assert equal_texts == \
        [('CD', 'CD'), ('G', 'G')]


# --------------------------------------------------------------------------
