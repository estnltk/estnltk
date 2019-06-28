from estnltk import Text, ElementaryBaseSpan
from estnltk.text import Span, Layer

from estnltk.layer_operations.consecutive import iterate_consecutive_spans
from estnltk.layer_operations.consecutive import iterate_touching_spans
from estnltk.layer_operations.consecutive import iterate_hovering_spans
from estnltk.layer_operations.consecutive import iterate_starting_spans
from estnltk.layer_operations.consecutive import iterate_ending_spans

from estnltk.layer_operations.intersections import iterate_intersecting_spans
from estnltk.layer_operations.intersections import iterate_nested_spans
from estnltk.layer_operations.intersections import iterate_overlapping_spans

# --------------------- Iterate over hovering Spans in SpanList


def test_iterate_hovering_spans_in_spanlist_1():
    # Example text:
    text = 'A B C D'
    
    # Create a SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0, 1))   # A
    spanlist.add_annotation((2, 3))   # B
    spanlist.add_annotation((4, 5))   # C
    spanlist.add_annotation((6, 7))   # D
    hovering = list(iterate_hovering_spans(spanlist, text))
    expected_hovering_span_texts = \
        [('A', 'B'), ('B', 'C'), ('C', 'D')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


def test_iterate_hovering_spans_in_spanlist_2():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'

    # Create a SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0,  3))    # üks
    spanlist.add_annotation((4,  8))    # kaks
    spanlist.add_annotation((9,  13))   # kolm
    spanlist.add_annotation((13, 17))  # neli
    spanlist.add_annotation((22, 26))  # kuus
    spanlist.add_annotation((18, 22))  # viis
    spanlist.add_annotation((27, 33))  # seitse
    hovering = list(iterate_hovering_spans(spanlist, text))
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
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0,  1))     # A
    spanlist.add_annotation((3,  4))     # B
    spanlist.add_annotation((5,  6))     # C
    spanlist.add_annotation((8,  9))     # D
    spanlist.add_annotation((10, 11))   # E
    hovering = list(iterate_hovering_spans(spanlist, text, min_gap=2))
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
    spanlist = Layer('layer_1', ambiguous=True)
    spanlist.add_annotation((0,  3))    # üks
    spanlist.add_annotation((4,  8))    # kaks
    spanlist.add_annotation((9,  13))   # kolm
    spanlist.add_annotation((4,  13))   # 'kaks kolm'
    spanlist.add_annotation((13, 17))   # neli
    spanlist.add_annotation((9,  17))   # kolmneli
    spanlist.add_annotation((18, 22))   # viis
    consecutive = list(iterate_consecutive_spans(spanlist, text))
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'),
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    consecutive_span_texts = \
        [(text[s1.start:s1.end], text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print(consecutive_span_texts)
    assert consecutive_span_texts == expected_consecutive_span_texts
    
    # Test on list of Spans
    spanlist = []
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 9, end=13)))  # kolm
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 0, end= 3)))   # üks
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end= 8)))   # kaks
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=13, end=17))) # neli
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 9, end=17)))  # kolmneli
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=18, end=22))) # viis
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end=13)))  # 'kaks kolm'
    consecutive = list(iterate_consecutive_spans(spanlist, text))
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print(consecutive_span_texts)
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'),
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    assert consecutive_span_texts == expected_consecutive_span_texts


def test_iterate_consecutive_spans_in_spanlist_with_max_gap():
    # Example text:
    text = 'A  B    CD  E    F'

    # Test on SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation(( 0,  1))    # A
    spanlist.add_annotation(( 3,  4))    # B
    spanlist.add_annotation(( 8,  9))    # C
    spanlist.add_annotation(( 8, 10))    # CD
    spanlist.add_annotation(( 9, 10))    # D
    spanlist.add_annotation((12, 13))    # E
    spanlist.add_annotation((17, 18))    # F

    consecutive = list( iterate_consecutive_spans(spanlist, text, max_gap=2) )
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print( consecutive_span_texts )
    expected_consecutive_span_texts = \
        [('A', 'B'), ('C', 'D'), ('CD', 'E'), ('D', 'E')]
    assert consecutive_span_texts == expected_consecutive_span_texts


def test_iterate_consecutive_spans_in_spanlist_with_gap_validator():
    def gap_validator(s):
        return False

    # Example text:
    text = 'A  B    CD  E    F'

    # Test on SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation(( 0, 1))    # A
    spanlist.add_annotation(( 3, 4))    # B
    spanlist.add_annotation(( 8, 9))    # C
    spanlist.add_annotation(( 8, 10))   # CD
    spanlist.add_annotation(( 9, 10))   # D
    spanlist.add_annotation((12, 13))   # E
    spanlist.add_annotation((17, 18))   # F

    consecutive = tuple(iterate_consecutive_spans(spanlist, text, max_gap=2, gap_validator=gap_validator))
    assert consecutive == ()

    #########################################

    def gap_validator(s):
        return s.strip() == ''

    # Example text:
    text = 'A  B    CD  E    F'

    spanlist = [
        Span(base_span=ElementaryBaseSpan(start=0,  end=1)),   # A
        Span(base_span=ElementaryBaseSpan(start=3,  end=4)),   # B
        Span(base_span=ElementaryBaseSpan(start=12, end=13)),  # E
        Span(base_span=ElementaryBaseSpan(start=17, end=18))   # F
        ]

    consecutive = tuple(iterate_consecutive_spans(spanlist, text, gap_validator=gap_validator))
    consecutive_span_texts = \
        [(text[s1.start:s1.end], text[s2.start:s2.end]) for s1, s2 in consecutive]
    expected_consecutive_span_texts = [('A', 'B'), ('E', 'F')]
    assert consecutive_span_texts == expected_consecutive_span_texts


# --------------------- Iterate over touching Spans in SpanList 

def test_iterate_touching_spans_in_spanlist_1():
    # Example text:
    text = 'AB'
    
    # Create a SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0, 1))  # A
    spanlist.add_annotation((1, 2))  # B
    spanlist.add_annotation((0, 2))  # AB
    
    touching = list(iterate_touching_spans(spanlist, text))
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
    spanlist = Layer('layer_1')
    spanlist.add_annotation(( 0,  3)) # üks
    spanlist.add_annotation(( 4,  8)) # kaks
    spanlist.add_annotation(( 9, 13)) # kolm
    spanlist.add_annotation((13, 17)) # neli
    spanlist.add_annotation((22, 26)) # kuus
    spanlist.add_annotation((18, 22)) # viis
    spanlist.add_annotation((27, 33)) # seitse
    
    touching = list(iterate_touching_spans(spanlist, text))
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
    spanlist = Layer('layer_1')
    spanlist.add_annotation(( 0,  3))  # üks
    spanlist.add_annotation(( 4,  8))  # kaks
    spanlist.add_annotation(( 9, 13))  # kolm
    spanlist.add_annotation(( 4, 13))  # 'kaks kolm'
    spanlist.add_annotation((13, 17))  # neli
    spanlist.add_annotation(( 9, 17))  # kolmneli
    spanlist.add_annotation((18, 22))  # viis
    touching = list(iterate_touching_spans(spanlist, text))
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('kaks kolm', 'neli'), ('kolm', 'neli')]
    assert touching_span_texts == expected_touching_span_texts

# --------------------- Iterate over starting and ending spans


def test_iterate_terminal_spans():
    s1 = ElementaryBaseSpan(0,  3)
    s2 = ElementaryBaseSpan(1, 10)
    s3 = ElementaryBaseSpan(5,  7)
    s5 = ElementaryBaseSpan(8,  9)

    layer = Layer('layer_1')
    assert tuple(iterate_starting_spans(layer)) == ()
    assert tuple(iterate_ending_spans(layer)) == ()

    layer.add_annotation(s3)
    assert list(iterate_starting_spans(layer)) == [layer[0]]
    assert list(iterate_ending_spans(layer)) == [layer[0]]

    layer.add_annotation(s1)
    layer.add_annotation(s5)
    assert list(iterate_starting_spans(layer)) == [layer[0]]
    assert list(iterate_ending_spans(layer)) == [layer[-1]]

    layer.add_annotation(s2)
    assert list(iterate_starting_spans(layer)) == [layer[0], layer[1]]
    assert list(iterate_ending_spans(layer)) == [layer[1], layer[3]]


# --------------------- Iterate over intersecting Spans in SpanList 

def test_yield_spanlist_intersections():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    # Test on SpanList
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0,  3))   # üks
    spanlist.add_annotation((4,  8))   # kaks
    spanlist.add_annotation((9,  13))  # kolm
    spanlist.add_annotation((4,  13))  # 'kaks kolm'
    spanlist.add_annotation((13, 17))  # neli
    spanlist.add_annotation((9,  17))  # kolmneli
    spanlist.add_annotation((18, 22))  # viis
    spanlist.add_annotation((22, 26))  # kuus
    spanlist.add_annotation((18, 26))  # viiskuus
    spanlist.add_annotation((27, 33))  # seitse
    spanlist.add_annotation((22, 33))  # 'kuus seitse'
    
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
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0, 3))  # üks
    spanlist.add_annotation((4, 8))  # kaks
    
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
    layer.add_annotation(( 0, 3))   # üks
    layer.add_annotation(( 4, 8))   # kaks
    layer.add_annotation(( 9, 13))  # kolm
    layer.add_annotation(( 4, 13))  # 'kaks kolm'
    layer.add_annotation((13, 17))  # neli
    layer.add_annotation(( 9, 17))  # kolmneli
    layer.add_annotation((18, 22))  # viis
    layer.add_annotation((22, 26))  # kuus
    layer.add_annotation((18, 26))  # viiskuus
    layer.add_annotation((27, 33))  # seitse
    layer.add_annotation((22, 33))  # 'kuus seitse'
    text['test_layer'] = layer
    
    intersections   = list( iterate_intersecting_spans( text['test_layer'].span_list ) )
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
    spanlist = Layer('layer_1')
    spanlist.add_annotation((0,  1))    # A
    spanlist.add_annotation((2,  3))    # B
    spanlist.add_annotation((4,  5))    # C
    spanlist.add_annotation((5,  6))    # D
    spanlist.add_annotation((4,  6))    # CD
    spanlist.add_annotation((7,  8))    # E
    spanlist.add_annotation((8,  9))    # F
    spanlist.add_annotation((7,  9))    # EF
    spanlist.add_annotation((10, 11))  # G

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
    spanlist = Layer('layer_1')
    spanlist.add_annotation(( 0,  1))    # A
    spanlist.add_annotation(( 2,  3))    # B
    spanlist.add_annotation(( 4,  5))    # C
    spanlist.add_annotation(( 2,  5))    # 'B C'
    spanlist.add_annotation(( 5,  6))    # D
    spanlist.add_annotation(( 4,  6))    # CD
    spanlist.add_annotation(( 7,  8))    # E
    spanlist.add_annotation(( 8,  9))    # F
    spanlist.add_annotation(( 7,  9))    # EF
    spanlist.add_annotation((10, 11))    # G
    spanlist.add_annotation(( 8, 11))    # 'F G'
    
    overlapping = list( iterate_overlapping_spans( spanlist ) )
    overlapping_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in overlapping ]
    #print( overlapping_texts )
    assert overlapping_texts == \
        [('B C', 'CD'), ('EF', 'F G')]
