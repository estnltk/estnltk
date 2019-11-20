from estnltk import Text, Annotation
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import VabamorfAnalyzer
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


# ----------------------------------

def test_default_morph_analysis_reorderer_on_normalized_words():
    # Test that morph analysis reorderer can handle multiple normalized texts
    # Create text with default morph analysis
    text=Text('Ja teisyki on yelnud vaid üht ...')
    text.tag_layer(['words','sentences'])
    # Change misspelled words: add multiple normalizations
    for word in text.words:
        if word.text == 'teisyki':
            # Change word's annotations
            word.clear_annotations()
            word.add_annotation( Annotation(word, normalized_form='teisigi') )
            word.add_annotation( Annotation(word, normalized_form='teisedki') )
        if word.text == 'yelnud':
            # Change word's annotations
            word.clear_annotations()
            word.add_annotation( Annotation(word, normalized_form='öelnud') )
            word.add_annotation( Annotation(word, normalized_form='ütelnud') )
    # Add morph analysis without disambiguation
    vm_analyser = VabamorfAnalyzer()
    vm_analyser.tag(text)
    # Fix ordering of analyses
    analysis_reorderer = MorphAnalysisReorderer()
    analysis_reorderer.retag( text )
    # Collect ambiguous analyses
    ambiguous_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        if len( annotations ) > 1:
            ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    # ==============
    #print()
    #for a in ambiguous_analyses:
    #    print(a)
    # ==============
    expected_orderings = [ \
      ['teisyki', ('teine', 'P', 'pl p'), ('teine', 'P', 'pl n'), ('teine', 'O', 'pl p'), ('teine', 'O', 'pl n')],
      ['on', ('ole', 'V', 'b'), ('ole', 'V', 'vad')],
      ['yelnud', ('ütle', 'V', 'nud'), ('ütle', 'V', 'nud'), ('öel=nud', 'A', 'pl n'), ('öel=nud', 'A', ''), ('öel=nud', 'A', 'sg n'), ('öel=nu', 'S', 'pl n'), ('ütel=nud', 'A', 'pl n'), ('ütel=nud', 'A', 'sg n'), ('ütel=nud', 'A', ''), ('ütel=nu', 'S', 'pl n')],
      ['vaid', ('vaid', 'D', ''), ('vaid', 'J', '')],
      ['üht', ('üks', 'P', 'sg p'), ('üks', 'N', 'sg p')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings

