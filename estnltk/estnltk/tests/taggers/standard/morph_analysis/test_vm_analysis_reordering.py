import os, os.path

from estnltk.common import PACKAGE_PATH

from estnltk import Text, Annotation
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import VabamorfAnalyzer
from estnltk.taggers import MorphAnalysisReorderer
from estnltk.default_resolver import make_resolver

# ----------------------------------

def test_morph_reorderer_empty_run():
    # Tests that morph analysis reorderer runs without errors even if lexicon files are not provided
    analysis_reorderer = MorphAnalysisReorderer(reorderings_csv_file=None,
                                                postag_freq_csv_file=None,
                                                form_freq_csv_file=None)
    # Make default resolver without reorderer
    resolver = make_resolver( use_reorderer=False )
    # Create text and retag it
    text=Text('Üks ütles, et 1. mail näidatakse palju maid.')
    text.tag_layer(['words','sentences', 'morph_analysis'], resolver=resolver)
    analysis_reorderer.retag(text)
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
        ['Üks', ('üks', 'N', 'sg n'), ('üks', 'P', 'sg n')],
        ['mail', ('maa', 'S', 'pl ad'), ('mai', 'S', 'sg ad') ],
        ['maid', ('maa', 'S', 'pl p'), ('mai', 'S', 'sg p')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings


# ----------------------------------

def test_default_morph_analysis_reorderer_1():
    # test: reorder words that have entries in the reorderings_csv_file
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
        ['ühed', ('üks', 'P', 'pl n'), ('üks', 'N', 'pl n')],
        ['teistega', ('teine', 'P', 'pl kom'), ('teine', 'O', 'pl kom')],
        ['seotud', ('seotud', 'A', ''), ('sidu', 'V', 'tud'), ('seotud', 'A', 'pl n'), ('seotud', 'A', 'sg n')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings


# ----------------------------------

def test_default_morph_analysis_reorderer_2():
    # test: reorder words that do not have entries in the reorderings_csv_file;
    # Therefore, use the information from postag_freq_csv_file for reordering
    # Case 1
    # Create text with default morph analysis
    text=Text('Neid teisigi on veidi torgatud ja tõugatud.')
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
        ['teisigi', ('teine', 'P', 'pl p'), ('teine', 'O', 'pl p')],
        ['on', ('ole', 'V', 'b'), ('ole', 'V', 'vad')],
        ['torgatud', ('torka', 'V', 'tud'), ('torga=tud', 'A', ''), ('torga=tud', 'A', 'sg n'), ('torga=tud', 'A', 'pl n')],
        ['tõugatud', ('tõuka', 'V', 'tud'), ('tõugatud', 'A', ''), ('tõugatud', 'A', 'sg n'), ('tõugatud', 'A', 'pl n')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings
    
    # Case 2
    # Create text with default morph analysis
    text=Text('Neil teistelgi oli vaja tolles teiseski veenduda.')
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
        ['teistelgi', ('teine', 'P', 'pl ad'), ('teine', 'O', 'pl ad')],
        ['teiseski', ('teine', 'P', 'sg in'), ('teine', 'O', 'sg in')],
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



def test_reorderer_with_customized_postag_freq_info():
    # Tests that morph analysis reorderer runs with customized postag freq lexicon
    # Create new reorderer that loads postag freq info from CSV file
    csv_dict_file_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'taggers', 'standard', 'morph_analysis', 'test_reorderer_postag_freq.csv')
    morph_reorderer = MorphAnalysisReorderer( reorderings_csv_file=None,
                                              postag_freq_csv_file=csv_dict_file_path,
                                              form_freq_csv_file=None )
    # Make default resolver without reorderer
    resolver = make_resolver( use_reorderer=False )
    # Create text with default morph analysis
    text=Text('Vaatan ja mõtlen, miks ühed pole kuidagi teistega seotud.')
    text.tag_layer(['words','sentences', 'morph_analysis'],resolver=resolver)
    # Reorder analyses
    morph_reorderer.retag( text )
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
        ['ühed', ('üks', 'P', 'pl n'), ('üks', 'N', 'pl n')],
        ['teistega', ('teine', 'P', 'pl kom'), ('teine', 'O', 'pl kom')],
        ['seotud', ('sidu', 'V', 'tud'), ('seotud', 'A', ''), ('seotud', 'A', 'sg n'), ('seotud', 'A', 'pl n')],
    ]
    # Make assertion
    assert ambiguous_analyses == expected_orderings


