from estnltk_core import Layer
from estnltk_core.layer_operations import flatten

from estnltk_core.common import load_text_class

def test_flatten_no_disambiguation():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Aias sadas saia.')

    layer_1 = Layer('test_1', attributes=['attr_1', 'attr_2'], text_object=text)
    text.add_layer(layer_1)
    result = flatten(layer_1, 'test_out')
    assert isinstance(result, Layer)
    assert result.ambiguous is True
    assert result.name == 'test_out'
    assert result.attributes == ('attr_1', 'attr_2')
    assert len(result) == 0

    layer_1.add_annotation((0, 5), attr_1=0, attr_2=1)
    layer_1.add_annotation((0, 10), attr_1=2, attr_2=3)
    layer_1.add_annotation((11, 15), attr_1=2, attr_2=3)

    result = flatten(layer_1, 'test_out')
    assert isinstance(result, Layer)
    assert result.name == 'test_out'
    assert result.attributes == ('attr_1', 'attr_2')
    assert len(result) == 3

    layer_2 = Layer('test_2', attributes=['attr_3', 'attr_4'], text_object=text, enveloping='test_1', ambiguous=True)
    layer_2.add_annotation([layer_1[0], layer_1[2]], attr_3=1)
    layer_2.add_annotation([layer_1[0], layer_1[2]], attr_3=2)
    layer_2.add_annotation([layer_1[1], layer_1[2]])

    result = flatten(layer_2, 'test_out')
    assert isinstance(result, Layer)
    assert result.name == 'test_out'
    assert result.attributes == ('attr_3', 'attr_4')
    assert len(result) == 1
    assert result.ambiguous is True
    assert result.enveloping is None
    span = result[0]
    assert span.start == 0
    assert span.end == 15
    assert len(span.annotations) == 3



def test_flatten_pick_first_disambiguation():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Aias sadas saia.')

    layer_1 = Layer('test_1', attributes=['lemma', 'pos'], \
                    text_object=text, ambiguous=True)
    layer_1.add_annotation((0, 4), lemma='aed', pos='S')
    layer_1.add_annotation((0, 4), lemma='Aed', pos='H')
    layer_1.add_annotation((5, 10), lemma='sadama', pos='V')
    layer_1.add_annotation((11, 15), lemma='sai', pos='S1')
    layer_1.add_annotation((11, 15), lemma='sai', pos='S2')
    
    result = flatten( layer_1, 'test_disambiguated_out', \
                      disambiguation_strategy='pick_first' )
    assert result.ambiguous is False
    assert len(result) == 3
    assert len(result[0].annotations) == 1
    assert result[0].annotations[0]['pos'] == 'S'
    assert result[0].annotations[0]['lemma'] == 'aed'
    assert len(result[1].annotations) == 1
    assert len(result[2].annotations) == 1



def test_flatten_cut_out_gaps_strategy():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()

    #
    # Case 1: simple nested/embedded structure
    #
    text = Text('Kõik suud, kes meie asjast teawad, on täieste kinni.')

    layer_words = Layer('words', text_object=text)
    layer_words.add_annotation( (0, 4) )
    layer_words.add_annotation( (5, 9) )
    layer_words.add_annotation( (9, 10) )
    layer_words.add_annotation( (11, 14) )
    layer_words.add_annotation( (15, 19) )
    layer_words.add_annotation( (20, 26) )
    layer_words.add_annotation( (27, 33) )
    layer_words.add_annotation( (33, 34) )
    layer_words.add_annotation( (35, 37) )
    layer_words.add_annotation( (38, 45) )
    layer_words.add_annotation( (46, 51) )
    layer_words.add_annotation( (51, 52) )
    text.add_layer( layer_words )

    layer_clauses = Layer( 'clauses', \
                           text_object=text, \
                           attributes=('clause_type',), \
                           enveloping='words' )
    layer_clauses.add_annotation( \
                [ (0, 4), (5, 9), (35, 37), (38, 45), (46, 51), (51, 52) ], \
                {'clause_type': 'regular'} )
    layer_clauses.add_annotation( \
                [ (9, 10), (11, 14), (15, 19), (20, 26), (27, 33), (33, 34) ], \
                {'clause_type': 'embedded'} )

    text.add_layer( layer_clauses )

    #
    # Default behaviour: Flatten without specifying gaps_strategy
    #
    result1 = flatten( layer_clauses, 'flatten_clauses_1' )
    assert len(result1) == 2
    assert result1[0].enclosing_text == 'Kõik suud, kes meie asjast teawad, on täieste kinni.'
    assert result1[1].enclosing_text == ', kes meie asjast teawad,'
    # Note that the result is not entirely correct as one span overlaps with another

    #
    # Flatten with specifying gaps_strategy='cut_out'
    #
    result2 = flatten( layer_clauses, 'flatten_clauses_2', gaps_strategy='cut_out' )
    assert len(result2) == 3
    assert result2[0].enclosing_text == 'Kõik suud'
    assert result2[1].enclosing_text == ', kes meie asjast teawad,'
    assert result2[2].enclosing_text == 'on täieste kinni.'

    #
    # Case 2: deeply nested/embedded clause structure
    #
    text2 = Text('Ja (vt konspekti (lk 53 (1)))')

    layer_words2 = Layer('words', text_object=text2)
    layer_words2.add_annotation( (0, 2) )
    layer_words2.add_annotation( (3, 4) )
    layer_words2.add_annotation( (4, 6) )
    layer_words2.add_annotation( (7, 16) )
    layer_words2.add_annotation( (17, 18) )
    layer_words2.add_annotation( (18, 20) )
    layer_words2.add_annotation( (21, 23) )
    layer_words2.add_annotation( (24, 25) )
    layer_words2.add_annotation( (25, 26) )
    layer_words2.add_annotation( (26, 27) )
    layer_words2.add_annotation( (27, 28) )
    layer_words2.add_annotation( (28, 29) )
    text2.add_layer( layer_words2 )
    
    layer_clauses2 = Layer( 'clauses', \
                            text_object=text2, \
                            attributes=('clause_type',), \
                            enveloping='words' )
    layer_clauses2.add_annotation( \
                [ (0, 2) ], {'clause_type': 'regular'} )
    layer_clauses2.add_annotation( \
                [ (3, 4), (4, 6), (7, 16), (28, 29) ], {'clause_type': 'embedded'} )
    layer_clauses2.add_annotation( \
                [ (17, 18), (18, 20), (21, 23), (27, 28) ], {'clause_type': 'embedded'} )
    layer_clauses2.add_annotation( \
                [ (24, 25), (25, 26), (26, 27) ], {'clause_type': 'embedded'} )
    text2.add_layer( layer_clauses2 )

    #
    # Default behaviour: Flatten without specifying gaps_strategy
    #
    result3 = flatten( layer_clauses2, 'flatten_clauses_3' )
    #print([s.enclosing_text for s in result3] )
    assert len(result3) == 4
    assert [s.enclosing_text for s in result3] == \
        ['Ja', '(vt konspekti (lk 53 (1)))', '(lk 53 (1))', '(1)']

    #
    # Flatten with specifying gaps_strategy='cut_out'
    #
    result4 = flatten( layer_clauses2, 'flatten_clauses_4', gaps_strategy='cut_out' )
    #print([s.enclosing_text for s in result4] )
    assert len(result4) == 6
    assert [s.enclosing_text for s in result4] == \
        ['Ja', '(vt konspekti', '(lk 53', '(1)', ')', ')']

