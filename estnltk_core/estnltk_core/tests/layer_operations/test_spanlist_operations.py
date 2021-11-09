from estnltk_core import ElementaryBaseSpan, Span, Layer

from estnltk_core.layer_operations.iterators.consecutive import iterate_consecutive_spans
from estnltk_core.layer_operations.iterators.consecutive import iterate_touching_spans
from estnltk_core.layer_operations.iterators.consecutive import iterate_hovering_spans
from estnltk_core.layer_operations.iterators.consecutive import iterate_starting_spans
from estnltk_core.layer_operations.iterators.consecutive import iterate_ending_spans

from estnltk_core.layer_operations.iterators.intersections import iterate_intersecting_spans
from estnltk_core.layer_operations.iterators.intersections import iterate_nested_spans
from estnltk_core.layer_operations.iterators.intersections import iterate_overlapping_spans

from estnltk_core.common import load_text_class

# --------------------- Iterate over hovering spans in a layer or in a list of spans


def test_iterate_hovering_spans_1():
    # Example text:
    text = 'A B C D'
    
    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0, 1))   # A
    layer.add_annotation((2, 3))   # B
    layer.add_annotation((4, 5))   # C
    layer.add_annotation((6, 7))   # D
    hovering = list(iterate_hovering_spans(layer, text))
    expected_hovering_span_texts = \
        [('A', 'B'), ('B', 'C'), ('C', 'D')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


def test_iterate_hovering_spans_2():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'

    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0,  3))    # üks
    layer.add_annotation((4,  8))    # kaks
    layer.add_annotation((9,  13))   # kolm
    layer.add_annotation((13, 17))  # neli
    layer.add_annotation((22, 26))  # kuus
    layer.add_annotation((18, 22))  # viis
    layer.add_annotation((27, 33))  # seitse
    hovering = list(iterate_hovering_spans(layer, text))
    expected_hovering_span_texts = \
        [('üks', 'kaks'), ('kaks', 'kolm'), ('neli', 'viis'), ('kuus', 'seitse')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


def test_iterate_hovering_spans_with_min_gap():
    # Example text:
    text = 'A  B C  D E'
    
    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0,  1))     # A
    layer.add_annotation((3,  4))     # B
    layer.add_annotation((5,  6))     # C
    layer.add_annotation((8,  9))     # D
    layer.add_annotation((10, 11))   # E
    hovering = list(iterate_hovering_spans(layer, text, min_gap=2))
    expected_hovering_span_texts = \
        [('A', 'B'), ('C', 'D')]
    hovering_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in hovering]
    #print( hovering_span_texts )
    assert hovering_span_texts == expected_hovering_span_texts


# --------------------- Iterate over consecutive spans in a layer or in a list of spans

def test_iterate_consecutive_spans():
    # Example text:
    text = 'üks kaks kolmneli viis'

    # Test on SpanList
    layer = Layer('layer_1', ambiguous=True)
    layer.add_annotation((0,  3))    # üks
    layer.add_annotation((4,  8))    # kaks
    layer.add_annotation((9,  13))   # kolm
    layer.add_annotation((4,  13))   # 'kaks kolm'
    layer.add_annotation((13, 17))   # neli
    layer.add_annotation((9,  17))   # kolmneli
    layer.add_annotation((18, 22))   # viis
    consecutive = list(iterate_consecutive_spans(layer, text))
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'),
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    consecutive_span_texts = \
        [(text[s1.start:s1.end], text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print(consecutive_span_texts)
    assert consecutive_span_texts == expected_consecutive_span_texts
    
    # Test on list of Spans
    spanlist = []
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 9, end=13), layer=None))  # kolm
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 0, end= 3), layer=None))  # üks
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end= 8), layer=None))  # kaks
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=13, end=17), layer=None))  # neli
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 9, end=17), layer=None))  # kolmneli
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=18, end=22), layer=None))  # viis
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end=13), layer=None))  # 'kaks kolm'
    consecutive = list(iterate_consecutive_spans(spanlist, text))
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print(consecutive_span_texts)
    expected_consecutive_span_texts = \
        [('üks', 'kaks'), ('üks', 'kaks kolm'), ('kaks', 'kolm'), ('kaks', 'kolmneli'),
         ('kaks kolm', 'neli'), ('kolm', 'neli'), ('kolmneli', 'viis'), ('neli', 'viis')]
    assert consecutive_span_texts == expected_consecutive_span_texts


def test_iterate_consecutive_spans_with_max_gap():
    # Example text:
    text = 'A  B    CD  E    F'

    # Test on SpanList
    layer = Layer('layer_1')
    layer.add_annotation(( 0,  1))    # A
    layer.add_annotation(( 3,  4))    # B
    layer.add_annotation(( 8,  9))    # C
    layer.add_annotation(( 8, 10))    # CD
    layer.add_annotation(( 9, 10))    # D
    layer.add_annotation((12, 13))    # E
    layer.add_annotation((17, 18))    # F

    consecutive = list( iterate_consecutive_spans(layer, text, max_gap=2) )
    consecutive_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in consecutive]
    #print( consecutive_span_texts )
    expected_consecutive_span_texts = \
        [('A', 'B'), ('C', 'D'), ('CD', 'E'), ('D', 'E')]
    assert consecutive_span_texts == expected_consecutive_span_texts


def test_iterate_consecutive_spans_with_gap_validator():
    def gap_validator(s):
        return False

    # Example text:
    text = 'A  B    CD  E    F'

    # Test on SpanList
    layer = Layer('layer_1')
    layer.add_annotation(( 0, 1))    # A
    layer.add_annotation(( 3, 4))    # B
    layer.add_annotation(( 8, 9))    # C
    layer.add_annotation(( 8, 10))   # CD
    layer.add_annotation(( 9, 10))   # D
    layer.add_annotation((12, 13))   # E
    layer.add_annotation((17, 18))   # F

    consecutive = tuple(iterate_consecutive_spans(layer, text, max_gap=2, gap_validator=gap_validator))
    assert consecutive == ()

    #########################################

    def gap_validator(s):
        return s.strip() == ''

    # Example text:
    text = 'A  B    CD  E    F'

    spanlist = [
        Span(base_span=ElementaryBaseSpan(start= 0, end= 1), layer=None),  # A
        Span(base_span=ElementaryBaseSpan(start= 3, end= 4), layer=None),  # B
        Span(base_span=ElementaryBaseSpan(start=12, end=13), layer=None),  # E
        Span(base_span=ElementaryBaseSpan(start=17, end=18), layer=None)   # F
        ]

    consecutive = tuple(iterate_consecutive_spans(spanlist, text, gap_validator=gap_validator))
    consecutive_span_texts = \
        [(text[s1.start:s1.end], text[s2.start:s2.end]) for s1, s2 in consecutive]
    expected_consecutive_span_texts = [('A', 'B'), ('E', 'F')]
    assert consecutive_span_texts == expected_consecutive_span_texts


# --------------------- Iterate over touching Spans in SpanList 

def test_iterate_touching_spans_1():
    # Example text:
    text = 'AB'
    
    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0, 1))  # A
    layer.add_annotation((1, 2))  # B
    layer.add_annotation((0, 2))  # AB
    
    touching = list(iterate_touching_spans(layer, text))
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('A', 'B')]
    assert touching_span_texts == expected_touching_span_texts


def test_iterate_touching_spans_2():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    #t = Text('üks kaks kolmneli viiskuus seitse')
    #t.tag_layer(['words'])
    
    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation(( 0,  3)) # üks
    layer.add_annotation(( 4,  8)) # kaks
    layer.add_annotation(( 9, 13)) # kolm
    layer.add_annotation((13, 17)) # neli
    layer.add_annotation((22, 26)) # kuus
    layer.add_annotation((18, 22)) # viis
    layer.add_annotation((27, 33)) # seitse
    
    touching = list(iterate_touching_spans(layer, text))
    touching_span_texts = \
        [(text[s1.start:s1.end],text[s2.start:s2.end]) for s1, s2 in touching]
    #print( touching_span_texts )
    expected_touching_span_texts = \
        [('kolm', 'neli'), ('viis', 'kuus')]
    assert touching_span_texts == expected_touching_span_texts


def test_iterate_touching_spans_3():
    # Example text:
    text = 'üks kaks kolmneli viis'
    
    # Create a SpanList
    layer = Layer('layer_1')
    layer.add_annotation(( 0,  3))  # üks
    layer.add_annotation(( 4,  8))  # kaks
    layer.add_annotation(( 9, 13))  # kolm
    layer.add_annotation(( 4, 13))  # 'kaks kolm'
    layer.add_annotation((13, 17))  # neli
    layer.add_annotation(( 9, 17))  # kolmneli
    layer.add_annotation((18, 22))  # viis
    touching = list(iterate_touching_spans(layer, text))
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

def test_iterate_intersecting_spans_1():
    # Example text:
    text = 'üks kaks kolmneli viiskuus seitse'
    
    # Test on SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0,  3))   # üks
    layer.add_annotation((4,  8))   # kaks
    layer.add_annotation((9,  13))  # kolm
    layer.add_annotation((4,  13))  # 'kaks kolm'
    layer.add_annotation((13, 17))  # neli
    layer.add_annotation((9,  17))  # kolmneli
    layer.add_annotation((18, 22))  # viis
    layer.add_annotation((22, 26))  # kuus
    layer.add_annotation((18, 26))  # viiskuus
    layer.add_annotation((27, 33))  # seitse
    layer.add_annotation((22, 33))  # 'kuus seitse'
    
    intersections = list(iterate_intersecting_spans(layer))
    intersect_texts = \
        [(text[a.start:a.end],text[b.start:b.end]) for a, b in intersections ]
    #print( intersect_texts )
    assert intersect_texts == \
        [('kaks', 'kaks kolm'), ('kaks kolm', 'kolm'), ('kaks kolm', 'kolmneli'), ('kolm', 'kolmneli'),\
         ('kolmneli', 'neli'), ('viis', 'viiskuus'), ('viiskuus', 'kuus'), ('viiskuus', 'kuus seitse'),\
         ('kuus', 'kuus seitse'), ('kuus seitse', 'seitse')]


def test_iterate_intersecting_spans_2():
    # Example text:
    text = 'üks kaks'
    
    # Test items
    layer = Layer('layer_1')
    layer.add_annotation((0, 3))  # üks
    layer.add_annotation((4, 8))  # kaks
    
    intersections = list(iterate_intersecting_spans(layer))
    intersect_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in intersections ]
    assert intersect_texts == []


def test_iterate_intersecting_spans_3():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Example text:
    text = Text('üks kaks kolmneli viiskuus seitse')
    #text.tag_layer(['words'])
    
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
    text.add_layer(layer)
    
    intersections   = list(iterate_intersecting_spans(text['test_layer']))
    intersect_texts = [ (a.text,b.text) for a, b in intersections ]
    #print( intersect_texts )
    assert intersect_texts == \
        [('kaks', 'kaks kolm'), ('kaks kolm', 'kolm'), ('kaks kolm', 'kolmneli'), ('kolm', 'kolmneli'),\
         ('kolmneli', 'neli'), ('viis', 'viiskuus'), ('viiskuus', 'kuus'), ('viiskuus', 'kuus seitse'),\
         ('kuus', 'kuus seitse'), ('kuus seitse', 'seitse')]


# --------------------- Iterate over nested Spans in SpanList 

def test_iterate_nested_spans():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create SpanList
    layer = Layer('layer_1')
    layer.add_annotation((0,  1))    # A
    layer.add_annotation((2,  3))    # B
    layer.add_annotation((4,  5))    # C
    layer.add_annotation((5,  6))    # D
    layer.add_annotation((4,  6))    # CD
    layer.add_annotation((7,  8))    # E
    layer.add_annotation((8,  9))    # F
    layer.add_annotation((7,  9))    # EF
    layer.add_annotation((10, 11))  # G

    nested = list(iterate_nested_spans(layer))
    nested_spans_texts = [(text[a.start:a.end],text[b.start:b.end]) for a, b in nested]
    #print( nested_spans_texts )
    assert nested_spans_texts == [('C', 'CD'), ('CD', 'D'), ('E', 'EF'), ('EF', 'F')]


# --------------------- Iterate over overlapped Spans in SpanList

def test_iterate_overlapping_spans():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create SpanList
    layer = Layer('layer_1')
    layer.add_annotation(( 0,  1))    # A
    layer.add_annotation(( 2,  3))    # B
    layer.add_annotation(( 4,  5))    # C
    layer.add_annotation(( 2,  5))    # 'B C'
    layer.add_annotation(( 5,  6))    # D
    layer.add_annotation(( 4,  6))    # CD
    layer.add_annotation(( 7,  8))    # E
    layer.add_annotation(( 8,  9))    # F
    layer.add_annotation(( 7,  9))    # EF
    layer.add_annotation((10, 11))    # G
    layer.add_annotation(( 8, 11))    # 'F G'
    
    overlapping = list(iterate_overlapping_spans(layer))
    overlapping_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in overlapping ]
    #print( overlapping_texts )
    assert overlapping_texts == \
        [('B C', 'CD'), ('EF', 'F G')]

# --------------------- Iterate over conflicting (i.e. intersecting) Spans in SpanList

def test_iterate_conflicting_spans():
    # Example text: 
    text = 'A B CD EF G'
    
    # Create a list of spans
    spanlist = []
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 0, end=1), layer=None))  # A
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 0, end=1), layer=None))  # A
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 2, end=3), layer=None))  # B
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end=5), layer=None))  # C
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 2, end=5), layer=None))  # 'B C'
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 5, end=6), layer=None))  # D
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 4, end=6), layer=None))  # CD
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 7, end=8), layer=None))  # E
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 8, end=9), layer=None))  # F
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 7, end=9), layer=None))  # EF
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=10, end=11), layer=None)) # G
    spanlist.append(Span(base_span=ElementaryBaseSpan(start=10, end=11), layer=None)) # G
    spanlist.append(Span(base_span=ElementaryBaseSpan(start= 8, end=11), layer=None)) # 'F G'
    
    conflicting = list( iterate_intersecting_spans(spanlist) )
    conflicting_texts = \
        [ (text[a.start:a.end],text[b.start:b.end]) for a, b in conflicting ]
    #print( conflicting_texts )
    assert conflicting_texts == \
        [('A', 'A'), ('B', 'B C'), ('B C', 'C'), ('B C', 'CD'), ('C', 'CD'), \
         ('CD', 'D'), ('E', 'EF'), ('EF', 'F'), ('EF', 'F G'), ('F', 'F G'), \
         ('F G', 'G'), ('F G', 'G'), ('G', 'G')]


