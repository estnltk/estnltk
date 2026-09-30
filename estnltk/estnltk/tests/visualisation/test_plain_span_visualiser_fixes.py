from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.visualisation.span_visualiser.plain_span_visualiser import PlainSpanVisualiser
from estnltk_core import Layer
from estnltk import Text

def test_plain_span_visualiser_on_embedded_clauses():
    # Test that PlainSpanVisualiser does not crash on clauses layer that 
    # contains embedded clauses enveloping around the words layer
    
    # Create text
    text = Text('Mees, keda seal kohtasime, tuli kaasa.')
    # Add words layer
    layer1 = Layer('words', attributes=(), text_object=text)
    layer1.add_annotation( (0,  4) )
    layer1.add_annotation( (4,  5) )
    layer1.add_annotation( (6, 10) )
    layer1.add_annotation( (11, 15) )
    layer1.add_annotation( (16, 25) )
    layer1.add_annotation( (25, 26) )
    layer1.add_annotation( (27, 31) )
    layer1.add_annotation( (32, 37) )
    layer1.add_annotation( (37, 38) )
    text.add_layer(layer1)
    # Add clauses layer enveloping words
    layer2 = Layer('clauses', attributes=('clause_type',), \
                   enveloping='words', text_object=text )
    layer2.add_annotation( [(0, 4), (27, 31), (32, 37), (37, 38)], clause_type='regular' )
    layer2.add_annotation( [(4, 5), (6, 10), (11, 15), (16, 25), (25, 26)], clause_type='embedded' )
    text.add_layer(layer2)

    # Decompose into spans
    actual_decomposed = decompose_to_elementary_spans(layer2, text.text)
    assert len(actual_decomposed) == 2
    segments, span_list = actual_decomposed
    expected_segments = \
        [['Mees', [0]], 
         [', keda seal kohtasime,', [0, 1]], 
         [' tuli kaasa.', [0]]]
    assert segments == expected_segments
    
    # try to put html together from js, css and html spans
    outputs = []
    span_decorator = PlainSpanVisualiser(text_id=0)
    for segment in segments:
        outputs.append( span_decorator(segment, span_list).replace("\n","<br>") )
    
    assert len(outputs) == 3
