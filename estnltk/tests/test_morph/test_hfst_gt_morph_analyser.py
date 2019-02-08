import pytest
import pkgutil
import os.path
import sys, faulthandler
faulthandler.enable(file=sys.stderr, all_threads=True)


def check_if_hfst_is_available():
    # Check that HFST is available
    return pkgutil.find_loader("hfst") is not None


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
@pytest.mark.skipif(not os.path.exists('analyser-gt-desc.hfstol'),
                    reason="transducer model file is required for this test")
def test_hfst_gt_morph_analyser_raw_output():
    import hfst  # (!) Important: this import must come before importing estnltk's Vabamorf;
    
    from estnltk import Text
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import HfstEstMorphAnalyser
    
    # Test HfstEstMorphAnalyser's raw output format
    hfstAnalyser = HfstEstMorphAnalyser( transducer_file='analyser-gt-desc.hfstol', output_format='raw' )

    # Case 1
    input_text_str = 'No, tore talv! Vannaemale ei öeldud, et mäesuusatamine võib-olla tore Juhhhei'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [ 
       [{'weight': 0.0, 'raw_analysis': 'no+Interj', 'start': 0, 'end': 2}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 2, 'end': 3}], \
       [{'weight': 0.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 4, 'end': 8}], \
       [{'weight': 0.0, 'raw_analysis': 'talv+N+Sg+Nom', 'start': 9, 'end': 13}], \
       [{'weight': 0.0, 'raw_analysis': '!+CLB', 'start': 13, 'end': 14}], \
       [{'weight': 243.0, 'raw_analysis': 'vanna+Guess#ema+N+Sg+All', 'start': 15, 'end': 25}], \
       [{'weight': 0.0, 'raw_analysis': 'ei+Adv', 'start': 26, 'end': 28}, \
        {'weight': 1.0, 'raw_analysis': 'ei+V+Neg', 'start': 26, 'end': 28}], \
       [{'weight': 0.0, 'raw_analysis': 'öeldud+A+Sg+Nom', 'start': 29, 'end': 35}, \
        {'weight': 1.0, 'raw_analysis': 'öeldud+A+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 1.0, 'raw_analysis': 'öeldu+N+Pl+Nom', 'start': 29, 'end': 35}, \
        {'weight': 2.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Prc', 'start': 29, 'end': 35}, \
        {'weight': 3.0, 'raw_analysis': 'ütlema+V+Impers+Prt+Ind+Neg', 'start': 29, 'end': 35}, \
        {'weight': 10.0, 'raw_analysis': 'ütlema+V+Der/tud+A', 'start': 29, 'end': 35}, \
        {'weight': 11.0, 'raw_analysis': 'ütlema+V+Der/tu+A+Pl+Nom', 'start': 29, 'end': 35}], \
       [{'weight': 0.0, 'raw_analysis': ',+CLB', 'start': 35, 'end': 36}], \
       [{'weight': 0.0, 'raw_analysis': 'et+CS', 'start': 37, 'end': 39}], \
       [{'weight': 30.0, 'raw_analysis': 'mäesuusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 41.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatamine+N+Sg+Nom', 'start': 40, 'end': 54}, \
        {'weight': 51.0, 'raw_analysis': 'mägi+N+Sg+Gen#suusatama+V+Der/mine+N+Sg+Nom', 'start': 40, 'end': 54}], \
       [{'weight': 0.0, 'raw_analysis': 'võib-olla+Adv', 'start': 55, 'end': 64}], \
       [{'weight': 0.0, 'raw_analysis': 'tore+A+Sg+Nom', 'start': 65, 'end': 69}], \
       [{'weight': float('inf'), 'raw_analysis': None, 'start': 70, 'end': 77 }] ]
    assert results == expected_results

    # Case 2
    input_text_str = 'Trinidad ja Tobago olidki saanud suusariigiks'
    text = Text(input_text_str)
    text.tag_layer(['compound_tokens', 'words'])
    hfstAnalyser.tag(text)
    results = text['hfst_gt_morph_analysis'].to_records()
    #print(results)
    expected_results = [ 
       [{'raw_analysis': 'Trinidad+N+Prop+Sg+Nom', 'end': 8, 'weight': 0.0, 'start': 0}], \
       [{'raw_analysis': 'ja+CC', 'end': 11, 'weight': 0.0, 'start': 9}], \
       [{'raw_analysis': 'Tobago+N+Prop+Sg+Nom', 'end': 18, 'weight': 0.0, 'start': 12}, \
        {'raw_analysis': 'Tobago+N+Prop+Sg+Gen', 'end': 18, 'weight': 1.0, 'start': 12}], \
       [{'raw_analysis': 'olema+V+Pers+Prt+Ind+Pl3+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}, \
        {'raw_analysis': 'olema+V+Pers+Prt+Ind+Sg2+Aff+Foc/gi', 'end': 25, 'weight': 1.0, 'start': 19}], \
       [{'raw_analysis': 'saanu+N+Pl+Nom', 'end': 32, 'weight': 1.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Pers+Prt+Prc', 'end': 32, 'weight': 1.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Pers+Prt+Ind+Neg', 'end': 32, 'weight': 2.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A', 'end': 32, 'weight': 10.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Sg+Nom', 'end': 32, 'weight': 10.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nu+N+Pl+Nom', 'end': 32, 'weight': 11.0, 'start': 26}, \
        {'raw_analysis': 'saama+V+Der/nud+A+Pl+Nom', 'end': 32, 'weight': 11.0, 'start': 26}], \
       [{'raw_analysis': 'suusk+N+Sg+Gen#riik+N+Sg+Tra', 'end': 45, 'weight': 44.0, 'start': 33}, \
        {'raw_analysis': 'suusa+Guess#riik+N+Sg+Tra', 'end': 45, 'weight': 243.0, 'start': 33}]]
    assert results == expected_results


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_split_analyses_into_morphemes():
    import hfst  # (!) Important: this import must come before importing estnltk's Vabamorf;
    
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import split_into_morphemes
    
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_morphemes':['talv+N+Sg+Nom']}, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_morphemes':['miski+Pron+Sg+Ine', '+Use/NotNorm']}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_morphemes':['ütlema+V+Pers+Prt+Ind+Neg']}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_morphemes':['karu+N+Sg+Gen', 'tapma+V+Der', 'ja+N+Sg+Nom', '+Foc/gi']}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_morphemes':['üli+Pref', 'püüd+N+Der', 'lik+A+Sg+Nom']}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_morphemes':['laupäev+N+Sg+Gen', 'hommik+N+Der', 'ti+Adv']}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_morphemes':['kild+N+Dim', 'ke+Sg+Nom']}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_morphemes':['ilu+N+Sg+Gen', 'aed+N+Pl+Par', '+Use/Rare']}, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        assert  morphemes == test_item['expected_morphemes']


@pytest.mark.skipif(not check_if_hfst_is_available(),
                    reason="package hfst is required for this test")
def test_hfst_gt_morph_analyser_extract_morpheme_features():
    import hfst  # (!) Important: this import must come before importing estnltk's Vabamorf;
    
    from estnltk.taggers.morph_analysis.hfst.hfst_gt_morph_analyser import split_into_morphemes, extract_morpheme_features
    from collections import OrderedDict
    
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_features': OrderedDict([('morphemes', ['talv']), ('postags', ['N']), ('forms', ['Sg+Nom']), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_features': OrderedDict([('morphemes', ['miski']), ('postags', ['Pron']), ('forms', ['Sg+Ine']), ('has_clitic', False), ('is_guessed', False), ('usage', '+Use/NotNorm')])}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_features': OrderedDict([('morphemes', ['ütlema']), ('postags', ['V']), ('forms', ['Pers+Prt+Ind+Neg']), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_features': OrderedDict([('morphemes', ['karu', 'tapma', 'ja']), ('postags', ['N', 'V', 'N']), ('forms', ['Sg+Gen', 'Der', 'Sg+Nom']), ('has_clitic', True), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['üli', 'püüd', 'lik']), ('postags', ['Pref', 'N', 'A']), ('forms', ['', 'Der', 'Sg+Nom']), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_features': OrderedDict([('morphemes', ['laupäev', 'hommik', 'ti']), ('postags', ['N', 'N', 'Adv']), ('forms', ['Sg+Gen', 'Der', '']), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['kild', 'ke']), ('postags', ['N', '']), ('forms', ['Dim', 'Sg+Nom']), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_features': OrderedDict([('morphemes', ['ilu', 'aed']), ('postags', ['N', 'N']), ('forms', ['Sg+Gen', 'Pl+Par']), ('has_clitic', False), ('is_guessed', False), ('usage', '+Use/Rare')])}, \
                  {'word':'vannaema',\
                   'raw_analysis':'vanna+Guess#ema+N+Sg+Gen' , \
                   'expected_features': OrderedDict([('morphemes', ['vanna', 'ema']), ('postags', ['', 'N']), ('forms', ['', 'Sg+Gen']), ('has_clitic', False), ('is_guessed', True), ('usage', '')])}, \
                  # It should also work on empty string
                  {'word':'',\
                   'raw_analysis':'' , \
                   'expected_features': OrderedDict([('morphemes', []), ('postags', []), ('forms', []), ('has_clitic', False), ('is_guessed', False), ('usage', '')])}, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        morpheme_feats = extract_morpheme_features( morphemes )
        print(morpheme_feats)
        assert morpheme_feats == test_item['expected_features']

