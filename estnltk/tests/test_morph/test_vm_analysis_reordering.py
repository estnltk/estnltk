from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import MorphAnalysisReorderer

# ----------------------------------

def test_default_morph_analysis_reorderer():
    # Case 1
    # Create text with default morph analysis
    text=Text('Üks ütles, et 1. mail näidatakse palju maid.')
    text.tag_layer(['words','sentences', 'morph_analysis'])
    # Fix ordering of analyses
    analysis_reorderer = MorphAnalysisReorderer()
    analysis_reorderer.retag( text )
    # Collect ambiguous analyses
    ambiguous_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        #ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
        if len( annotations ) > 1:
            ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    # ==============
    #print()
    #for a in ambiguous_analyses:
    #    print(a)
    # ==============
    expected_orderings = [ \
        ['Üks', ('üks', 'P', 'sg n'), ('üks', 'N', 'sg n')],
        ['mail', ('mai', 'S', 'sg ad'), ('maa', 'S', 'pl ad')],
        ['maid', ('maa', 'S', 'pl p'), ('mai', 'S', 'sg p')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings

    # Case 2
    # Create text with default morph analysis
    text=Text('Vaatan ja mõtlen, miks ühed pole kuidagi teistega seotud.')
    text.tag_layer(['words','sentences', 'morph_analysis'])
    # Fix ordering of analyses
    analysis_reorderer = MorphAnalysisReorderer()
    analysis_reorderer.retag( text )
    # Collect ambiguous analyses
    ambiguous_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        #ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
        if len( annotations ) > 1:
            ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    # ==============
    #print()
    #for a in ambiguous_analyses:
    #    print(a)
    # ==============
    expected_orderings = [ \
        ['miks', ('miks', 'D', ''), ('miks', 'S', 'sg n')],
        ['ühed', ('üks', 'P', 'pl n'), ('üks', 'N', 'pl n')],
        ['teistega', ('teine', 'P', 'pl kom'), ('teine', 'O', 'pl kom')],
        ['seotud', ('seotud', 'A', ''), ('sidu', 'V', 'tud'), ('seotud', 'A', 'pl n'), ('seotud', 'A', 'sg n')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings

