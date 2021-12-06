#
#   Tests for Hfst morph analyser that is based on hfst command line tools (HfstClMorphAnalyser)
#

import pytest

from estnltk import Annotation
from estnltk import Text

from estnltk.converters import layer_to_records

from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_analyser_cmd_line import check_if_hfst_is_in_path
from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_analyser_cmd_line import HfstClMorphAnalyser

@pytest.mark.skipif(not check_if_hfst_is_in_path(),
                    reason="hfst command line tools are required for this test")
def test_hfst_morph_analyser_raw_output():
    # Test HfstClMorphAnalyser's raw output format
    hfstAnalyser = HfstClMorphAnalyser( output_format='raw' )

    # Case 1
    input_text_str = 'No, tore talv! Vannaemale ei öeldud, et mäesuusatamine võib-olla tore Juhhhei'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [ 
       [{'weight': 6.0, 'raw_analysis': 'no+Interj', 'start': 0, 'end': 2}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 2, 'end': 3}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 4, 'end': 8}], \
       [{'weight': 6.0, 'raw_analysis': 'talv+N+Sg+Nom', 'start': 9, 'end': 13}], \
       [{'weight': 0.0, 'raw_analysis': '!+CLB', 'start': 13, 'end': 14}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 15, 'end': 25}], \
       [{'weight': 1.0, 'raw_analysis': 'ei+Adv', 'start': 26, 'end': 28}, \
        {'weight': 2.0, 'raw_analysis': 'ei+V+Neg', 'start': 26, 'end': 28}], \
       [{'weight': 5.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Prc', 'start': 29, 'end': 35}, \
        {'weight': 6.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Ind+Neg', 'start': 29, 'end': 35}, \
        {'weight': 9.0, 'raw_analysis': 'öeldu+N+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 10.0, 'raw_analysis': 'öeldud+A+Sg+Nom', 'start': 29, 'end': 35}, \
        {'weight': 11.0, 'raw_analysis': 'öeldud+A+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 13.0, 'raw_analysis': 'ütlema+V+Der/tud+A', 'start': 29, 'end': 35}, \
        {'weight': 14.0, 'raw_analysis': 'ütlema+V+Der/tu+A+Pl+Nom', 'start': 29, 'end': 35}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 35, 'end': 36}], \
       [{'weight': 1.0, 'raw_analysis': 'et+CS', 'start': 37, 'end': 39}], \
       [{'weight': 40.0, 'raw_analysis': 'mäesuusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 56.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 66.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatama+V+Der/mine+N+Sg+Nom', 'start': 40, 'end': 54}], \
       [{'weight': 5.0, 'raw_analysis': 'võib-olla+Adv', 'start': 55, 'end': 64}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 65, 'end': 69}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 70, 'end': 77 }] ]
    assert results == expected_results

    # Case 2
    input_text_str = 'Trinidad ja Tobago olidki saanud suusariigiks'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [ 
       [{'raw_analysis': 'Trinidad+N+Prop+Sg+Nom', 'end': 8, 'weight': 11.0, 'start': 0}], \
       [{'raw_analysis': 'ja+CC', 'end': 11, 'weight': 0.0, 'start': 9}], \
       [{'raw_analysis': 'Tobago+N+Prop+Sg+Nom', 'end': 18, 'weight': 11.0, 'start': 12}, \
        {'raw_analysis': 'Tobago+N+Prop+Sg+Gen', 'end': 18, 'weight': 12.0, 'start': 12}], \
       [{'raw_analysis': 'olema+V+Pers+Prt+Ind+Pl3+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}, \
        {'raw_analysis': 'olema+V+Pers+Prt+Ind+Sg2+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}], \
       [{'raw_analysis': 'saama+V+Pers+Prt+Prc', 'end': 32, 'weight': 3.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Pers+Prt+Ind+Neg', 'end': 32, 'weight': 4.0, 'start': 26}, \
        {'raw_analysis': 'saanu+N+Pl+Nom', 'end': 32, 'weight': 10.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Sg+Nom', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nu+N+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}], \
       [{'raw_analysis': 'suusk+N+Sg+Gen#riik+N+Sg+Tra', 'end': 45, 'weight': 56.0, 'start': 33}] ]
    assert results == expected_results
    #         
    # *** Test lookup method
    
    # Case 3
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('alpimajakene')
        #print(records)
        expected_records = [ \
           {'raw_analysis': 'alpi+Pref#majake+N+Sg+Nom+Use/Rare', 'weight': 84.0}, \
           {'raw_analysis': 'alpi+Pref#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 90.0}, \
           {'raw_analysis': 'alpi+N+Sg+Gen#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 92.0}, \
           {'raw_analysis': 'alp+A+Sg+Nom#imama+V+Der/ja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 110.0}, \
           {'raw_analysis': 'alpi+Guess#majake+N+Sg+Nom+Use/Rare', 'weight': 269.0}, \
           {'raw_analysis': 'alpi+Guess#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 275.0} \
        ]
        #assert records == expected_records
    
    # Case 4
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('äraguugeldatud') # as in: "Kui Sul on äraguugeldatud, võid tulla kohvi jooma."
        #print(records)
        expected_records = [ \
           {'raw_analysis': 'ära+Adv#guugeldama+V+Der/tud+A', 'weight': 65.0}, \
           {'raw_analysis': 'ära+Adv#guugeldama+V+Der/tu+A+Pl+Nom', 'weight': 66.0} \
        ]
        #assert records == expected_records

    # Case 5
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('xyxrjxxf3tg5') # totally unknown word
        #assert records == []


@pytest.mark.skipif(not check_if_hfst_is_in_path(),
                    reason="hfst command line tools are required for this test")
def test_hfst_morph_analyser_raw_output_file_based_io():
    # Test HfstClMorphAnalyser's raw output format with file based I/O
    hfstAnalyser = HfstClMorphAnalyser( output_format='raw', use_stream=False )

    # Case 1
    input_text_str = 'No, tore talv! Vannaemale ei öeldud, et mäesuusatamine võib-olla tore Juhhhei'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [ 
       [{'weight': 6.0, 'raw_analysis': 'no+Interj', 'start': 0, 'end': 2}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 2, 'end': 3}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 4, 'end': 8}], \
       [{'weight': 6.0, 'raw_analysis': 'talv+N+Sg+Nom', 'start': 9, 'end': 13}], \
       [{'weight': 0.0, 'raw_analysis': '!+CLB', 'start': 13, 'end': 14}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 15, 'end': 25}], \
       [{'weight': 1.0, 'raw_analysis': 'ei+Adv', 'start': 26, 'end': 28}, \
        {'weight': 2.0, 'raw_analysis': 'ei+V+Neg', 'start': 26, 'end': 28}], \
       [{'weight': 5.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Prc', 'start': 29, 'end': 35}, \
        {'weight': 6.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Ind+Neg', 'start': 29, 'end': 35}, \
        {'weight': 9.0, 'raw_analysis': 'öeldu+N+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 10.0, 'raw_analysis': 'öeldud+A+Sg+Nom', 'start': 29, 'end': 35}, \
        {'weight': 11.0, 'raw_analysis': 'öeldud+A+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 13.0, 'raw_analysis': 'ütlema+V+Der/tud+A', 'start': 29, 'end': 35}, \
        {'weight': 14.0, 'raw_analysis': 'ütlema+V+Der/tu+A+Pl+Nom', 'start': 29, 'end': 35}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 35, 'end': 36}], \
       [{'weight': 1.0, 'raw_analysis': 'et+CS', 'start': 37, 'end': 39}], \
       [{'weight': 40.0, 'raw_analysis': 'mäesuusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 56.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 66.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatama+V+Der/mine+N+Sg+Nom', 'start': 40, 'end': 54}], \
       [{'weight': 5.0, 'raw_analysis': 'võib-olla+Adv', 'start': 55, 'end': 64}], \
       [{'weight': 6.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 65, 'end': 69}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 70, 'end': 77 }] ]
    assert results == expected_results

    # Case 2
    input_text_str = 'Trinidad ja Tobago olidki saanud suusariigiks'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [ 
       [{'raw_analysis': 'Trinidad+N+Prop+Sg+Nom', 'end': 8, 'weight': 11.0, 'start': 0}], \
       [{'raw_analysis': 'ja+CC', 'end': 11, 'weight': 0.0, 'start': 9}], \
       [{'raw_analysis': 'Tobago+N+Prop+Sg+Nom', 'end': 18, 'weight': 11.0, 'start': 12}, \
        {'raw_analysis': 'Tobago+N+Prop+Sg+Gen', 'end': 18, 'weight': 12.0, 'start': 12}], \
       [{'raw_analysis': 'olema+V+Pers+Prt+Ind+Pl3+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}, \
        {'raw_analysis': 'olema+V+Pers+Prt+Ind+Sg2+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}], \
       [{'raw_analysis': 'saama+V+Pers+Prt+Prc', 'end': 32, 'weight': 3.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Pers+Prt+Ind+Neg', 'end': 32, 'weight': 4.0, 'start': 26}, \
        {'raw_analysis': 'saanu+N+Pl+Nom', 'end': 32, 'weight': 10.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Sg+Nom', 'end': 32, 'weight': 12.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nu+N+Pl+Nom', 'end': 32, 'weight': 13.0, 'start': 26}], \
       [{'raw_analysis': 'suusk+N+Sg+Gen#riik+N+Sg+Tra', 'end': 45, 'weight': 56.0, 'start': 33}] ]
    assert results == expected_results
    #         
    # *** Test lookup method
    
    # Case 3
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('alpimajakene')
        #print(records)
        expected_records = [ \
           {'raw_analysis': 'alpi+Pref#majake+N+Sg+Nom+Use/Rare', 'weight': 84.0}, \
           {'raw_analysis': 'alpi+Pref#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 90.0}, \
           {'raw_analysis': 'alpi+N+Sg+Gen#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 92.0}, \
           {'raw_analysis': 'alp+A+Sg+Nom#imama+V+Der/ja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 110.0}, \
           {'raw_analysis': 'alpi+Guess#majake+N+Sg+Nom+Use/Rare', 'weight': 269.0}, \
           {'raw_analysis': 'alpi+Guess#maja+N+Dim/ke+Sg+Nom+Use/Rare', 'weight': 275.0} \
        ]
        #assert records == expected_records


@pytest.mark.skipif(not check_if_hfst_is_in_path(),
                    reason="hfst command line tools are required for this test")
def test_hfst_morph_analyser_raw_output_on_multiple_normalized_word_forms():
    # Test HfstClMorphAnalyser's raw output format
    hfstAnalyser = HfstClMorphAnalyser( output_format='raw' )
    # Case 1: word normalizations without unknown words
    text = Text('''isaand kui juuuubbeee ...''')
    text.tag_layer(['compound_tokens', 'words'])
    # Add multiple normalized forms
    for word in text.words:
        if word.text == 'isaand':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['isand', 'issand']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='isand') )
                word.add_annotation( Annotation(word, normalized_form='issand') )
        if word.text == 'juuuubbeee':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['jube']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='jube') )
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = \
    [
      [{'start': 0, 'weight': 7.0, 'raw_analysis': 'isand+N+Sg+Nom', 'end': 6}, 
       {'start': 0, 'weight': 7.0, 'raw_analysis': 'issand+N+Sg+Nom', 'end': 6}], 
      [{'start': 7, 'weight': 2.0, 'raw_analysis': 'kui+CS', 'end': 10}, 
       {'start': 7, 'weight': 2.0, 'raw_analysis': 'kui+Adv', 'end': 10}, 
       {'start': 7, 'weight': 200.0, 'raw_analysis': 'kui+Guess+N+Sg+Nom', 'end': 10}, 
       {'start': 7, 'weight': 201.0, 'raw_analysis': 'kui+Guess+N+Sg+Gen', 'end': 10}], 
      [{'start': 11, 'weight': 7.0, 'raw_analysis': 'jube+A+Sg+Nom', 'end': 21}, 
       {'start': 11, 'weight': 7.0, 'raw_analysis': 'jube+Adv', 'end': 21}], 
      [{'start': 22, 'weight': 0.0, 'raw_analysis': '...+CLB', 'end': 25}]
    ]
    assert results == expected_results
    
    # Case 2: word normalizations with unknown words
    text = Text('''päris hää !''')
    text.tag_layer(['compound_tokens', 'words'])
    # Add multiple normalized forms (include unknown words)
    for word in text.words:
        if word.text == 'hää':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['hea', 'hääx0R', 'head']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='hea') )
                word.add_annotation( Annotation(word, normalized_form='hääx0R') )
                word.add_annotation( Annotation(word, normalized_form='head') )
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = \
    [
        [{'weight': 5.0, 'end': 5, 'raw_analysis': 'päris+A', 'start': 0}, 
         {'weight': 5.0, 'end': 5, 'raw_analysis': 'päris+Adv', 'start': 0}, 
         {'weight': 7.0, 'end': 5, 'raw_analysis': 'pärima+V+Pers+Prt+Ind+Sg3+Aff', 'start': 0}], 
        [{'weight': 4.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Nom', 'start': 6}, 
         {'weight': 4.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Nom', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Gen', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Gen', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+A+Pl+Nom', 'start': 6}, 
         {'weight': 5.0, 'end': 9, 'raw_analysis': 'hea+N+Pl+Nom', 'start': 6}, 
         {'weight': 6.0, 'end': 9, 'raw_analysis': 'hea+A+Sg+Par', 'start': 6}, 
         {'weight': 6.0, 'end': 9, 'raw_analysis': 'hea+N+Sg+Par', 'start': 6}], 
        [{'weight': 0.0, 'end': 11, 'raw_analysis': '!+CLB', 'start': 10}] ]
    assert results == expected_results



@pytest.mark.skipif(not check_if_hfst_is_in_path(),
                    reason="hfst command line tools are required for this test")
def test_hfst_morph_analyser_morphemes_lemmas_output():
    # Test HfstClMorphAnalyser's morphemes_lemmas output format
    hfstAnalyser = HfstClMorphAnalyser( output_format='morphemes_lemmas' )

    # Case 1
    input_text_str = 'Ülipüüdlik vannaemake rohib võib-olla Zathumaeres iluaedasid.'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [
       [{'weight': 54.0, 'end': 10, 'forms': ('', 'Sg+Nom'), 'postags': ('Pref', 'A'), 'morphemes_lemmas': ('üli', 'püüdlik'), 'is_guessed': False, 'has_clitic': False, 'start': 0, 'usage': ()}, 
        {'weight': 64.0, 'end': 10, 'forms': ('', 'Der', 'Sg+Nom'), 'postags': ('Pref', 'N', 'A'), 'morphemes_lemmas': ('üli', 'püüd', 'lik'), 'is_guessed': False, 'has_clitic': False, 'start': 0, 'usage': ()},
        {'weight': 249.0, 'end': 10, 'forms': ('', 'Der', 'Sg+Nom'), 'postags': ('', 'N', 'A'), 'morphemes_lemmas': ('üli', 'püüd', 'lik'), 'is_guessed': True, 'has_clitic': False, 'start': 0, 'usage': ()}], 
       [{'weight': 239.0, 'end': 21, 'forms': ('', 'Sg+Nom'), 'postags':  ('', 'N'), 'morphemes_lemmas': ('vanna', 'emake'), 'is_guessed': True, 'has_clitic': False, 'start': 11, 'usage': ()}], 
       [{'weight': 10.0, 'end': 27, 'forms': ('Pers+Prs+Ind+Sg3+Aff',), 'postags': ('V',), 'morphemes_lemmas': ('rohima',), 'is_guessed': False, 'has_clitic': False, 'start': 22, 'usage': ()}], 
       [{'weight': 5.0, 'end': 37, 'forms': ('',), 'postags': ('Adv',), 'morphemes_lemmas': ('võib-olla',), 'is_guessed': False, 'has_clitic': False, 'start': 28, 'usage': ()}], 
       [{'weight': float('inf'), 'end': 49, 'forms': None, 'postags': None, 'morphemes_lemmas': None, 'is_guessed': None, 'has_clitic': None, 'start': 38, 'usage': None}], 
       [{'weight': 74.0, 'end': 60, 'forms': ('Pl+Par',), 'postags': ('N',), 'morphemes_lemmas': ('iluaed',), 'is_guessed': False, 'has_clitic': False, 'start': 50, 'usage': ('Use/Rare',)}, 
        {'weight': 87.0, 'end': 60, 'forms': ('Sg+Gen', 'Pl+Par'), 'postags': ('N', 'N'), 'morphemes_lemmas': ('ilu', 'aed'), 'is_guessed': False, 'has_clitic': False, 'start': 50, 'usage': ('Use/Rare',)} ], 
       [{'weight': 0.0, 'end': 61, 'forms': ('',), 'postags': ('CLB',), 'morphemes_lemmas': ('.',), 'is_guessed': False, 'has_clitic': False, 'start': 60, 'usage': ()}]
    ]
    assert results == expected_results
    
    # Case 2
    input_text_str = 'Äralõigatud ühendusega allmaaraudteejaamaski ulgus tuulekene.'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = layer_to_records( text['hfst_gt_morph_analysis'] )
    #print(results)
    expected_results = [
       [{'postags': ('Adv', 'V', 'A'), 'is_guessed': False, 'end': 11, 'morphemes_lemmas': ('ära', 'lõikama', 'tud'), 'has_clitic': False, 'forms': ('', 'Der', ''), 'weight': 60.0, 'start': 0, 'usage': ()}, 
        {'postags': ('Adv', 'V', 'A'), 'is_guessed': False, 'end': 11, 'morphemes_lemmas': ('ära', 'lõikama', 'tu'), 'has_clitic': False, 'forms': ('', 'Der', 'Pl+Nom'), 'weight': 61.0, 'start': 0, 'usage': ()}], 
       [{'postags': ('N',), 'is_guessed': False, 'end': 22, 'morphemes_lemmas': ('ühendus',), 'has_clitic': False, 'forms': ('Sg+Com',), 'weight': 9.0, 'start': 12, 'usage': ()}, 
        {'postags': ('V', 'N'), 'is_guessed': False, 'end': 22, 'morphemes_lemmas': ('ühendama', 'us'), 'has_clitic': False, 'forms': ('Der', 'Sg+Com'), 'weight': 19.0, 'start': 12, 'usage': ()}], 
       [{'postags': ('N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('allmaaraudtee', 'jaam'), 'has_clitic': True, 'forms': ('Sg+Gen', 'Sg+Ine'), 'weight': 152.0, 'start': 23, 'usage': ()}, 
        {'postags': ('Pref', 'N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('all', 'maa', 'raudteejaam'), 'has_clitic': True, 'forms': ('', 'Sg+Gen', 'Sg+Ine'), 'weight': 161.0, 'start': 23, 'usage': ()}, 
        {'postags': ('Pref', 'N', 'N', 'N'), 'is_guessed': False, 'end': 44, 'morphemes_lemmas': ('all', 'maa', 'raudtee', 'jaam'), 'has_clitic': True, 'forms': ('', 'Sg+Gen', 'Sg+Gen', 'Sg+Ine'), 'weight': 178.0, 'start': 23, 'usage': ()}], 
       [{'postags': ('V',), 'is_guessed': False, 'end': 50, 'morphemes_lemmas': ('ulguma',), 'has_clitic': False, 'forms': ('Pers+Prt+Ind+Sg3+Aff',), 'weight': 10.0, 'start': 45, 'usage': ()}], 
       [{'postags': ('N',), 'is_guessed': False, 'end': 60, 'morphemes_lemmas': ('tuuleke',), 'has_clitic': False, 'forms': ('Sg+Nom',), 'weight': 41.0, 'start': 51, 'usage': ('Use/Rare',)}, 
        {'postags': ('N', ''), 'is_guessed': False, 'end': 60, 'morphemes_lemmas': ('tuul', 'ke'), 'has_clitic': False, 'forms': ('Dim', 'Sg+Nom'), 'weight': 46.0, 'start': 51, 'usage': ('Use/Rare',)}],
       [{'postags': ('CLB',), 'is_guessed': False, 'end': 61, 'morphemes_lemmas': ('.',), 'has_clitic': False, 'forms': ('',), 'weight': 0.0, 'start': 60, 'usage': ()}]
    ]
    assert results == expected_results

    # *** Test lookup method
    
    # Case 3
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('alpikannike')
        #print(records)
        expected_records = [ \
            {'has_clitic': False, 'morphemes_lemmas': ('alpikann', 'ke'), 'forms': ('Dim', 'Sg+Nom'), 'weight': 51.0, 'postags': ('N', ''), 'usage': (), 'is_guessed': False}, \
            {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 56.0, 'postags': ('Pref', 'N'), 'usage': (), 'is_guessed': False}, \
            {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ke'), 'forms': ('', 'Dim', 'Sg+Nom'), 'weight': 63.0, 'postags': ('Pref', 'N', ''), 'usage': (), 'is_guessed': False}, \
            {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ike'), 'forms': ('', 'Sg+Nom', 'Sg+Nom'), 'weight': 106.0, 'postags': ('Pref', 'N', 'N'), 'usage': (), 'is_guessed': False}, \
            {'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 241.0, 'postags': ('', 'N'), 'usage': (), 'is_guessed': True} \
        ]
        #{'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kannike'), 'forms': ('', 'Sg+Nom'), 'weight': 240.0, 'postags': ('', 'N'), 'usage': (), 'is_guessed': True}, \
        #{'has_clitic': False, 'morphemes_lemmas': ('alpi', 'kann', 'ke'), 'forms': ('', 'Dim', 'Sg+Nom'), 'weight': 250.0, 'postags': ('', 'N', ''), 'usage': (), 'is_guessed': True} \
        #assert records == expected_records
    
    # Case 4
    with pytest.raises(NotImplementedError):
        records = hfstAnalyser.lookup('üleguugeldanud') # as in: "Oled ennast täitsa üleguugeldanud!"
        #print(records)
        expected_records = [ \
            {'weight': 64.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', ''), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
            {'weight': 64.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', 'Sg+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
            {'weight': 65.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'A'), 'forms': ('', 'Der', 'Pl+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nud'), 'has_clitic': False}, \
            {'weight': 65.0, 'is_guessed': False, 'postags': ('Adv', 'V', 'N'), 'forms': ('', 'Der', 'Pl+Nom'), 'usage': (), 'morphemes_lemmas': ('üle', 'guugeldama', 'nu'), 'has_clitic': False} \
        ]
        #assert records == expected_records



@pytest.mark.skipif(not check_if_hfst_is_in_path(),
                    reason="hfst command line tools are required for this test")
def test_hfst_morph_analyser_with_guessing_switched_on_and_off():
    # Test HfstClMorphAnalyser's with guessing switched on and off
    # Case 1: lookup
    hfstAnalyser = HfstClMorphAnalyser( output_format='raw', remove_guesses=True )
    hfstAnalyserGuesser = HfstClMorphAnalyser( output_format='raw' )
    with pytest.raises(NotImplementedError):
        records1 = hfstAnalyser.lookup('kiwikübarad')
        #assert records1 == []
        records2 = hfstAnalyserGuesser.lookup('kiwikübarad')
        #assert records2 == [{'raw_analysis': 'kiwi+Guess#kübar+N+Pl+Nom', 'weight': 239.0}]
    
    # Case 2: tagging
    text = Text('bronzemehikesed')
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser = HfstClMorphAnalyser(remove_guesses=True)
    hfstAnalyserGuesser = HfstClMorphAnalyser(output_layer='hfst_gt_morph_analysis_w_guesses')
    hfstAnalyser.tag(text)
    results1 = layer_to_records( text['hfst_gt_morph_analysis'] )
    assert results1 == [[{'weight': float('inf'), 'postags': None, 'forms': None, 'morphemes_lemmas': None, 'end': 15, 'usage': None, 'start': 0, 'has_clitic': None, 'is_guessed': None}]]
    hfstAnalyserGuesser.tag(text)
    results2 = layer_to_records( text['hfst_gt_morph_analysis_w_guesses'] )
    assert results2 == [[{'weight': 240.0, 'postags': ('', 'N'), 'forms': ('', 'Pl+Nom'), 'morphemes_lemmas': ('bronze', 'mehike'), 'end': 15, 'usage': (), 'start': 0, 'has_clitic': False, 'is_guessed': True}, \
                         {'weight': 242.0, 'postags': ('', 'N'), 'forms': ('', 'Pl+Nom'), 'morphemes_lemmas': ('bronze', 'mehikene'), 'end': 15, 'usage': (), 'start': 0, 'has_clitic': False, 'is_guessed': True}]] 

