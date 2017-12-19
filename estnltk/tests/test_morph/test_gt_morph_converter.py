from estnltk.text import Text
from estnltk.taggers.morf import VabamorfAnalyzer
from estnltk.taggers.gt_morf import GTMorphConverter

# ----------------------------------
#   Helper functions
# ----------------------------------

def _sort_morph_analysis_records( morph_analysis_records:list ):
    '''Sorts sublists (lists of analyses of a single word) of 
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order. '''
    for wrid, word_records_list in enumerate( morph_analysis_records ):
        sorted_records = sorted( word_records_list, key = lambda x : \
            str(x['root'])+str(x['ending'])+str(x['clitic'])+\
            str(x['partofspeech'])+str(x['form']) )
        morph_analysis_records[wrid] = sorted_records

# ----------------------------------

def test_gt_conversion_1_simple():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Rändur võttis istet.')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )

    # Assert that the new layer is created
    assert 'gt_morph_analysis' in text.layers
    
    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
        [{'form': 'Sg Nom', 'clitic': '', 'root_tokens': ('rändur',), 'end': 6, 'root': 'rändur', 'lemma': 'rändur', 'start': 0, 'partofspeech': 'S', 'ending': '0'}], \
        [{'form': 'Pers Prt Ind Sg 3 Aff', 'clitic': '', 'root_tokens': ('võt',), 'end': 13, 'root': 'võt', 'lemma': 'võtma', 'start': 7, 'partofspeech': 'V', 'ending': 'is'}], \
        [{'form': 'Sg Par', 'clitic': '', 'root_tokens': ('iste',), 'end': 19, 'root': 'iste', 'lemma': 'iste', 'start': 14, 'partofspeech': 'S', 'ending': 't'}], \
        [{'form': '', 'clitic': '', 'root_tokens': ('.',), 'end': 20, 'root': '.', 'lemma': '.', 'start': 19, 'partofspeech': 'Z', 'ending': ''}] \
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()

    # Case 2
    text = Text('Rändur võttis seljakotist vilepilli ja tõstis huultele.')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )
    
    # Assert content of the layer    
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
          [{'start': 0, 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'end': 6, 'form': 'Sg Nom', 'root_tokens': ('rändur',), 'root': 'rändur', 'lemma': 'rändur'}], \
          [{'start': 7, 'ending': 'is', 'clitic': '', 'partofspeech': 'V', 'end': 13, 'form': 'Pers Prt Ind Sg 3 Aff', 'root_tokens': ('võt',), 'root': 'võt', 'lemma': 'võtma'}], \
          [{'start': 14, 'ending': 'st', 'clitic': '', 'partofspeech': 'S', 'end': 25, 'form': 'Sg Ela', 'root_tokens': ('selja', 'kott'), 'root': 'selja_kott', 'lemma': 'seljakott'}], \
          [{'start': 26, 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'end': 35, 'form': 'Sg Par', 'root_tokens': ('vile', 'pill'), 'root': 'vile_pill', 'lemma': 'vilepill'}], \
          [{'start': 36, 'ending': '0', 'clitic': '', 'partofspeech': 'J', 'end': 38, 'form': '', 'root_tokens': ('ja',), 'root': 'ja', 'lemma': 'ja'}], \
          [{'start': 39, 'ending': 'is', 'clitic': '', 'partofspeech': 'V', 'end': 45, 'form': 'Pers Prt Ind Sg 3 Aff', 'root_tokens': ('tõst',), 'root': 'tõst', 'lemma': 'tõstma'}], \
          [{'start': 46, 'ending': 'tele', 'clitic': '', 'partofspeech': 'S', 'end': 54, 'form': 'Pl All', 'root_tokens': ('huul',), 'root': 'huul', 'lemma': 'huul'}], \
          [{'start': 54, 'ending': '', 'clitic': '', 'partofspeech': 'Z', 'end': 55, 'form': '', 'root_tokens': ('.',), 'root': '.', 'lemma': '.'}] \
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()


def test_gt_conversion_2_neg():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Ärge peatuge: siin ei tohi kiirust vähendada!')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )

    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
        [{'root': 'ära', 'ending': 'ge', 'partofspeech': 'V', 'root_tokens': ('ära',), 'form': 'Pers Prs Imprt Pl 2 Neg', 'clitic': '', 'end': 4, 'lemma': 'ära', 'start': 0}], \
        [{'root': 'peatu', 'ending': 'ge', 'partofspeech': 'V', 'root_tokens': ('peatu',), 'form': 'Pers Prs Imprt Pl 2', 'clitic': '', 'end': 12, 'lemma': 'peatuma', 'start': 5}], \
        [{'root': ':', 'ending': '', 'partofspeech': 'Z', 'root_tokens': (':',), 'form': '', 'clitic': '', 'end': 13, 'lemma': ':', 'start': 12}], \
        [{'root': 'siin', 'ending': '0', 'partofspeech': 'D', 'root_tokens': ('siin',), 'form': '', 'clitic': '', 'end': 18, 'lemma': 'siin', 'start': 14}], \
        [{'root': 'ei', 'ending': '0', 'partofspeech': 'V', 'root_tokens': ('ei',), 'form': 'Neg', 'clitic': '', 'end': 21, 'lemma': 'ei', 'start': 19}], \
        [{'root': 'tohti', 'ending': '0', 'partofspeech': 'V', 'root_tokens': ('tohti',), 'form': 'Pers Prs Ind Neg', 'clitic': '', 'end': 26, 'lemma': 'tohtima', 'start': 22}], \
        [{'root': 'kiirus', 'ending': 't', 'partofspeech': 'S', 'root_tokens': ('kiirus',), 'form': 'Sg Par', 'clitic': '', 'end': 34, 'lemma': 'kiirus', 'start': 27}], \
        [{'root': 'vähenda', 'ending': 'da', 'partofspeech': 'V', 'root_tokens': ('vähenda',), 'form': 'Inf', 'clitic': '', 'end': 44, 'lemma': 'vähendama', 'start': 35}], \
        [{'root': '!', 'ending': '', 'partofspeech': 'Z', 'root_tokens': ('!',), 'form': '', 'clitic': '', 'end': 45, 'lemma': '!', 'start': 44}] \
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()

    # Case 2
    text = Text('Mine sa tea!')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
        [{'ending': '0', 'partofspeech': 'V', 'lemma': 'minema', 'root_tokens': ('mine',), 'root': 'mine', 'clitic': '', 'start': 0, 'end': 4, 'form': 'Pers Prs Imprt Sg 2'}], \
        [{'ending': '0', 'partofspeech': 'P', 'lemma': 'sina', 'root_tokens': ('sina',), 'root': 'sina', 'clitic': '', 'start': 5, 'end': 7, 'form': 'Sg Nom'}], \
        [{'ending': '0', 'partofspeech': 'V', 'lemma': 'teadma', 'root_tokens': ('tead',), 'root': 'tead', 'clitic': '', 'start': 8, 'end': 11, 'form': 'Pers Prs Imprt Sg 2'}], \
        [{'ending': '', 'partofspeech': 'Z', 'lemma': '!', 'root_tokens': ('!',), 'root': '!', 'clitic': '', 'start': 11, 'end': 12, 'form': ''}] \
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()


def test_gt_conversion_3_ambiguous():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Sellist asja ei olnud.')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
        [{'start': 0, 'ending': 't', 'clitic': '', 'end': 7, 'lemma': 'selline', 'form': 'Sg Par', 'root': 'selline', 'partofspeech': 'P', 'root_tokens': ('selline',)}], \
        [{'start': 8, 'ending': '0', 'clitic': '', 'end': 12, 'lemma': 'asi', 'form': 'Sg Par', 'root': 'asi', 'partofspeech': 'S', 'root_tokens': ('asi',)}], \
        [{'start': 13, 'ending': '0', 'clitic': '', 'end': 15, 'lemma': 'ei', 'form': 'Neg', 'root': 'ei', 'partofspeech': 'V', 'root_tokens': ('ei',)}], \
        [{'start': 16, 'ending': '0', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': '', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)}, \
         {'start': 16, 'ending': '0', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': 'Sg Nom', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)}, \
         {'start': 16, 'ending': 'd', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': 'Pl Nom', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)}, \
         {'start': 16, 'ending': 'nud', 'clitic': '', 'end': 21, 'lemma': 'olema', 'form': 'Pers Prt Ind Neg', 'root': 'ole', 'partofspeech': 'V', 'root_tokens': ('ole',)}], \
        [{'start': 21, 'ending': '', 'clitic': '', 'end': 22, 'lemma': '.', 'form': '', 'root': '.', 'partofspeech': 'Z', 'root_tokens': ('.',)}] \
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()


def test_gt_conversion_3_sid_ksid():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Oleksid Sa siin olnud, siis oleksid nad ära läinud.')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = [ \
        [{'partofspeech': 'V', 'end': 7, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 0, 'lemma': 'olema', 'form': 'Pers Prs Cond Pl 3 Aff', 'ending': 'ksid'}, \
         {'partofspeech': 'V', 'end': 7, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 0, 'lemma': 'olema', 'form': 'Pers Prs Cond Sg 2 Aff', 'ending': 'ksid'}], \
        [{'partofspeech': 'P', 'end': 10, 'root_tokens': ('sina',), 'root': 'sina', 'clitic': '', 'start': 8, 'lemma': 'sina', 'form': 'Sg Nom', 'ending': '0'}], \
        [{'partofspeech': 'D', 'end': 15, 'root_tokens': ('siin',), 'root': 'siin', 'clitic': '', 'start': 11, 'lemma': 'siin', 'form': '', 'ending': '0'}], \
        [{'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': '', 'ending': '0'}, \
         {'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': 'Sg Nom', 'ending': '0'}, \
         {'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': 'Pl Nom', 'ending': 'd'}, \
         {'partofspeech': 'V', 'end': 21, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 16, 'lemma': 'olema', 'form': 'Pers Prt Prc', 'ending': 'nud'}], \
        [{'partofspeech': 'Z', 'end': 22, 'root_tokens': (',',), 'root': ',', 'clitic': '', 'start': 21, 'lemma': ',', 'form': '', 'ending': ''}], \
        [{'partofspeech': 'D', 'end': 27, 'root_tokens': ('siis',), 'root': 'siis', 'clitic': '', 'start': 23, 'lemma': 'siis', 'form': '', 'ending': '0'}], \
        [{'partofspeech': 'V', 'end': 35, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 28, 'lemma': 'olema', 'form': 'Pers Prs Cond Pl 3 Aff', 'ending': 'ksid'}, \
         {'partofspeech': 'V', 'end': 35, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 28, 'lemma': 'olema', 'form': 'Pers Prs Cond Sg 2 Aff', 'ending': 'ksid'}], \
        [{'partofspeech': 'P', 'end': 39, 'root_tokens': ('tema',), 'root': 'tema', 'clitic': '', 'start': 36, 'lemma': 'tema', 'form': 'Pl Nom', 'ending': 'd'}], \
        [{'partofspeech': 'D', 'end': 43, 'root_tokens': ('ära',), 'root': 'ära', 'clitic': '', 'start': 40, 'lemma': 'ära', 'form': '', 'ending': '0'}], \
        [{'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': '', 'ending': '0'}, \
         {'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': 'Sg Nom', 'ending': '0'}, \
         {'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': 'Pl Nom', 'ending': 'd'}, \
         {'partofspeech': 'V', 'end': 50, 'root_tokens': ('mine',), 'root': 'mine', 'clitic': '', 'start': 44, 'lemma': 'minema', 'form': 'Pers Prt Prc', 'ending': 'nud'}], \
        [{'partofspeech': 'Z', 'end': 51, 'root_tokens': ('.',), 'root': '.', 'clitic': '', 'start': 50, 'lemma': '.', 'form': '', 'ending': ''}]
    ]
    assert expected_records == text['gt_morph_analysis'].to_records()


def test_gt_conversion_4_empty():
    gt_converter = GTMorphConverter()
    
    text = Text('')
    text.tag_layer(['morph_analysis'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print(text['gt_morph_analysis'].to_records())
    expected_records = []
    assert expected_records == text['gt_morph_analysis'].to_records()


def test_gt_conversion_5_unknown_words():
    # Tests that the conversion does not crash on unknown words
    analyzer = VabamorfAnalyzer()
    gt_converter = GTMorphConverter()
    
    text = Text('Ma tahax minna järve ääde')
    text.tag_layer(['words','sentences'])
    analyzer.tag(text, guess=False, propername=False)
    gt_converter.tag( text )
    #print(text['gt_morph_analysis'].to_records())

    expected_records = [ \
        [{'start': 0, 'root': 'mina', 'form': 'Sg Nom', 'ending': '0', 'partofspeech': 'P', 'clitic': '', 'lemma': 'mina', 'root_tokens': ('mina',), 'end': 2}], \
        [{'start': 3, 'root': None, 'form': None, 'ending': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'root_tokens': None, 'end': 8}], \
        [{'start': 9, 'root': 'mine', 'form': 'Inf', 'ending': 'a', 'partofspeech': 'V', 'clitic': '', 'lemma': 'minema', 'root_tokens': ('mine',), 'end': 14}], \
        [{'start': 15, 'root': 'järv', 'form': 'Sg Ill', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}, \
         {'start': 15, 'root': 'järv', 'form': 'Sg Gen', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}, \
         {'start': 15, 'root': 'järv', 'form': 'Sg Par', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}], \
        [{'start': 21, 'root': None, 'form': None, 'ending': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'root_tokens': None, 'end': 25}]]
    
    # Assert content of the layer
    results_dict = text['gt_morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

