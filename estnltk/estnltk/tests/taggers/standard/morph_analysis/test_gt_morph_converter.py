from estnltk import Text
from estnltk.taggers import VabamorfAnalyzer
from estnltk.taggers import GTMorphConverter
from estnltk.converters import layer_to_records

# ----------------------------------
#   Helper functions
# ----------------------------------


def _sort_morph_analysis_records( morph_analysis_records:list ):
    """Sorts sublists (lists of analyses of a single word) of
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order."""
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
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )

    # Assert that the new layer is created
    assert 'gt_morph_analysis' in text.layers
    
    # Assert content of the layer
    #print( layer_to_records(text['gt_morph_analysis']) )
    expected_records = [
        [{'normalized_text': 'Rändur', 'form': 'Sg Nom', 'clitic': '', 'root_tokens': ('rändur',), 'end': 6, 'root': 'rändur', 'lemma': 'rändur', 'start': 0, 'partofspeech': 'S', 'ending': '0'}], \
        [{'normalized_text': 'võttis', 'form': 'Pers Prt Ind Sg 3 Aff', 'clitic': '', 'root_tokens': ('võt',), 'end': 13, 'root': 'võt', 'lemma': 'võtma', 'start': 7, 'partofspeech': 'V', 'ending': 'is'}], \
        [{'normalized_text': 'istet', 'form': 'Sg Par', 'clitic': '', 'root_tokens': ('iste',), 'end': 19, 'root': 'iste', 'lemma': 'iste', 'start': 14, 'partofspeech': 'S', 'ending': 't'}], \
        [{'normalized_text': '.', 'form': '', 'clitic': '', 'root_tokens': ('.',), 'end': 20, 'root': '.', 'lemma': '.', 'start': 19, 'partofspeech': 'Z', 'ending': ''}] \
    ]
    assert expected_records == layer_to_records( text['gt_morph_analysis'] )

    # Case 2
    text = Text('Rändur võttis seljakotist vilepilli ja tõstis huultele.')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    
    # Assert content of the layer    
    #print( layer_to_records(text['gt_morph_analysis']) )
    expected_records = [ \
          [{'normalized_text': 'Rändur', 'start': 0, 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'end': 6, 'form': 'Sg Nom', 'root_tokens': ('rändur',), 'root': 'rändur', 'lemma': 'rändur'}], \
          [{'normalized_text': 'võttis', 'start': 7, 'ending': 'is', 'clitic': '', 'partofspeech': 'V', 'end': 13, 'form': 'Pers Prt Ind Sg 3 Aff', 'root_tokens': ('võt',), 'root': 'võt', 'lemma': 'võtma'}], \
          [{'normalized_text': 'seljakotist', 'start': 14, 'ending': 'st', 'clitic': '', 'partofspeech': 'S', 'end': 25, 'form': 'Sg Ela', 'root_tokens': ('selja', 'kott'), 'root': 'selja_kott', 'lemma': 'seljakott'}], \
          [{'normalized_text': 'vilepilli', 'start': 26, 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'end': 35, 'form': 'Sg Par', 'root_tokens': ('vile', 'pill'), 'root': 'vile_pill', 'lemma': 'vilepill'}], \
          [{'normalized_text': 'ja', 'start': 36, 'ending': '0', 'clitic': '', 'partofspeech': 'J', 'end': 38, 'form': '', 'root_tokens': ('ja',), 'root': 'ja', 'lemma': 'ja'}], \
          [{'normalized_text': 'tõstis', 'start': 39, 'ending': 'is', 'clitic': '', 'partofspeech': 'V', 'end': 45, 'form': 'Pers Prt Ind Sg 3 Aff', 'root_tokens': ('tõst',), 'root': 'tõst', 'lemma': 'tõstma'}], \
          [{'normalized_text': 'huultele', 'start': 46, 'ending': 'tele', 'clitic': '', 'partofspeech': 'S', 'end': 54, 'form': 'Pl All', 'root_tokens': ('huul',), 'root': 'huul', 'lemma': 'huul'}], \
          [{'normalized_text': '.', 'start': 54, 'ending': '', 'clitic': '', 'partofspeech': 'Z', 'end': 55, 'form': '', 'root_tokens': ('.',), 'root': '.', 'lemma': '.'}] \
    ]
    assert expected_records == layer_to_records( text['gt_morph_analysis'] )


def test_gt_conversion_2_neg():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Ärge peatuge: siin ei tohi kiirust vähendada!')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )

    # Assert content of the layer
    #print( layer_to_records(text['gt_morph_analysis']) )
    expected_records = [ \
        [{'normalized_text': 'Ärge', 'root': 'ära', 'ending': 'ge', 'partofspeech': 'V', 'root_tokens': ('ära',), 'form': 'Pers Prs Imprt Pl 2 Neg', 'clitic': '', 'end': 4, 'lemma': 'ära', 'start': 0}], \
        [{'normalized_text': 'peatuge', 'root': 'peatu', 'ending': 'ge', 'partofspeech': 'V', 'root_tokens': ('peatu',), 'form': 'Pers Prs Imprt Pl 2', 'clitic': '', 'end': 12, 'lemma': 'peatuma', 'start': 5}], \
        [{'normalized_text': ':', 'root': ':', 'ending': '', 'partofspeech': 'Z', 'root_tokens': (':',), 'form': '', 'clitic': '', 'end': 13, 'lemma': ':', 'start': 12}], \
        [{'normalized_text': 'siin', 'root': 'siin', 'ending': '0', 'partofspeech': 'D', 'root_tokens': ('siin',), 'form': '', 'clitic': '', 'end': 18, 'lemma': 'siin', 'start': 14}], \
        [{'normalized_text': 'ei', 'root': 'ei', 'ending': '0', 'partofspeech': 'V', 'root_tokens': ('ei',), 'form': 'Neg', 'clitic': '', 'end': 21, 'lemma': 'ei', 'start': 19}], \
        [{'normalized_text': 'tohi', 'root': 'tohti', 'ending': '0', 'partofspeech': 'V', 'root_tokens': ('tohti',), 'form': 'Pers Prs Ind Neg', 'clitic': '', 'end': 26, 'lemma': 'tohtima', 'start': 22}], \
        [{'normalized_text': 'kiirust', 'root': 'kiirus', 'ending': 't', 'partofspeech': 'S', 'root_tokens': ('kiirus',), 'form': 'Sg Par', 'clitic': '', 'end': 34, 'lemma': 'kiirus', 'start': 27}], \
        [{'normalized_text': 'vähendada', 'root': 'vähenda', 'ending': 'da', 'partofspeech': 'V', 'root_tokens': ('vähenda',), 'form': 'Inf', 'clitic': '', 'end': 44, 'lemma': 'vähendama', 'start': 35}], \
        [{'normalized_text': '!', 'root': '!', 'ending': '', 'partofspeech': 'Z', 'root_tokens': ('!',), 'form': '', 'clitic': '', 'end': 45, 'lemma': '!', 'start': 44}] \
    ]
    assert expected_records == layer_to_records( text['gt_morph_analysis'] )

    # Case 2
    text = Text('Mine sa tea!')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print( layer_to_records( text['gt_morph_analysis'] ) )
    expected_records = [ \
        [{'normalized_text': 'Mine', 'ending': '0', 'partofspeech': 'V', 'lemma': 'minema', 'root_tokens': ('mine',), 'root': 'mine', 'clitic': '', 'start': 0, 'end': 4, 'form': 'Pers Prs Imprt Sg 2'}], \
        [{'normalized_text': 'sa', 'ending': '0', 'partofspeech': 'P', 'lemma': 'sina', 'root_tokens': ('sina',), 'root': 'sina', 'clitic': '', 'start': 5, 'end': 7, 'form': 'Sg Nom'}], \
        [{'normalized_text': 'tea', 'ending': '0', 'partofspeech': 'V', 'lemma': 'teadma', 'root_tokens': ('tead',), 'root': 'tead', 'clitic': '', 'start': 8, 'end': 11, 'form': 'Pers Prs Imprt Sg 2'}], \
        [{'normalized_text': '!', 'ending': '', 'partofspeech': 'Z', 'lemma': '!', 'root_tokens': ('!',), 'root': '!', 'clitic': '', 'start': 11, 'end': 12, 'form': ''}] \
    ]
    assert expected_records == layer_to_records( text['gt_morph_analysis'] )


def test_gt_conversion_3_ambiguous():
    gt_converter = GTMorphConverter()
    
    # Case 1
    text = Text('Sellist asja ei olnud.')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print( layer_to_records( text['gt_morph_analysis'] ) )
    expected_records = [ \
        [{'normalized_text': 'Sellist', 'start': 0, 'ending': 't', 'clitic': '', 'end': 7, 'lemma': 'selline', 'form': 'Sg Par', 'root': 'selline', 'partofspeech': 'P', 'root_tokens': ('selline',)}], \
        [{'normalized_text': 'asja', 'start': 8, 'ending': '0', 'clitic': '', 'end': 12, 'lemma': 'asi', 'form': 'Sg Par', 'root': 'asi', 'partofspeech': 'S', 'root_tokens': ('asi',)}], \
        [{'normalized_text': 'ei', 'start': 13, 'ending': '0', 'clitic': '', 'end': 15, 'lemma': 'ei', 'form': 'Neg', 'root': 'ei', 'partofspeech': 'V', 'root_tokens': ('ei',)}], \
        [{'normalized_text': 'olnud', 'start': 16, 'ending': 'nud', 'clitic': '', 'end': 21, 'lemma': 'olema', 'form': 'Pers Prt Ind Neg', 'root': 'ole', 'partofspeech': 'V', 'root_tokens': ('ole',)}, \
         {'normalized_text': 'olnud', 'start': 16, 'ending': '0', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': '', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)}, \
         {'normalized_text': 'olnud', 'start': 16, 'ending': '0', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': 'Sg Nom', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)}, \
         {'normalized_text': 'olnud', 'start': 16, 'ending': 'd', 'clitic': '', 'end': 21, 'lemma': 'olnud', 'form': 'Pl Nom', 'root': 'ol=nud', 'partofspeech': 'A', 'root_tokens': ('olnud',)} 
        ], \
        [{'normalized_text': '.', 'start': 21, 'ending': '', 'clitic': '', 'end': 22, 'lemma': '.', 'form': '', 'root': '.', 'partofspeech': 'Z', 'root_tokens': ('.',)}] \
    ]
    assert expected_records == layer_to_records( text['gt_morph_analysis'] )


def test_gt_conversion_3_sid_ksid():
    gt_converter = GTMorphConverter()
    
    # Case 1 : -ksid
    text = Text('Oleksid Sa siin olnud, siis oleksid nad ära läinud.')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    expected_records = [ \
        [{'normalized_text': 'Oleksid', 'partofspeech': 'V', 'end': 7, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 0, 'lemma': 'olema', 'form': 'Pers Prs Cond Sg 2 Aff', 'ending': 'ksid'}], \
        [{'normalized_text': 'Sa', 'partofspeech': 'P', 'end': 10, 'root_tokens': ('sina',), 'root': 'sina', 'clitic': '', 'start': 8, 'lemma': 'sina', 'form': 'Sg Nom', 'ending': '0'}], \
        [{'normalized_text': 'siin', 'partofspeech': 'D', 'end': 15, 'root_tokens': ('siin',), 'root': 'siin', 'clitic': '', 'start': 11, 'lemma': 'siin', 'form': '', 'ending': '0'}], \
        [{'normalized_text': 'olnud', 'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': '', 'ending': '0'}, \
         {'normalized_text': 'olnud', 'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': 'Sg Nom', 'ending': '0'}, \
         {'normalized_text': 'olnud', 'partofspeech': 'A', 'end': 21, 'root_tokens': ('olnud',), 'root': 'ol=nud', 'clitic': '', 'start': 16, 'lemma': 'olnud', 'form': 'Pl Nom', 'ending': 'd'}, \
         {'normalized_text': 'olnud', 'partofspeech': 'V', 'end': 21, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 16, 'lemma': 'olema', 'form': 'Pers Prt Prc', 'ending': 'nud'}], \
        [{'normalized_text': ',', 'partofspeech': 'Z', 'end': 22, 'root_tokens': (',',), 'root': ',', 'clitic': '', 'start': 21, 'lemma': ',', 'form': '', 'ending': ''}], \
        [{'normalized_text': 'siis', 'partofspeech': 'D', 'end': 27, 'root_tokens': ('siis',), 'root': 'siis', 'clitic': '', 'start': 23, 'lemma': 'siis', 'form': '', 'ending': '0'}], \
        [{'normalized_text': 'oleksid', 'partofspeech': 'V', 'end': 35, 'root_tokens': ('ole',), 'root': 'ole', 'clitic': '', 'start': 28, 'lemma': 'olema', 'form': 'Pers Prs Cond Pl 3 Aff', 'ending': 'ksid'}], \
        [{'normalized_text': 'nad', 'partofspeech': 'P', 'end': 39, 'root_tokens': ('tema',), 'root': 'tema', 'clitic': '', 'start': 36, 'lemma': 'tema', 'form': 'Pl Nom', 'ending': 'd'}], \
        [{'normalized_text': 'ära', 'partofspeech': 'D', 'end': 43, 'root_tokens': ('ära',), 'root': 'ära', 'clitic': '', 'start': 40, 'lemma': 'ära', 'form': '', 'ending': '0'}], \
        [{'normalized_text': 'läinud', 'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': '', 'ending': '0'}, \
         {'normalized_text': 'läinud', 'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': 'Sg Nom', 'ending': '0'}, \
         {'normalized_text': 'läinud', 'partofspeech': 'A', 'end': 50, 'root_tokens': ('läinud',), 'root': 'läinud', 'clitic': '', 'start': 44, 'lemma': 'läinud', 'form': 'Pl Nom', 'ending': 'd'}, \
         {'normalized_text': 'läinud', 'partofspeech': 'V', 'end': 50, 'root_tokens': ('mine',), 'root': 'mine', 'clitic': '', 'start': 44, 'lemma': 'minema', 'form': 'Pers Prt Prc', 'ending': 'nud'}], \
        [{'normalized_text': '.', 'partofspeech': 'Z', 'end': 51, 'root_tokens': ('.',), 'root': '.', 'clitic': '', 'start': 50, 'lemma': '.', 'form': '', 'ending': ''}]
    ]
    results = layer_to_records( text['gt_morph_analysis'] )
    _sort_morph_analysis_records( results )
    _sort_morph_analysis_records( expected_records )
    assert expected_records == results
    
    # Case 2 : -sid
    text = Text('Sa läksid ära. Aga nemad tõttasid edasi, sind nad ei näinud.')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    #print( layer_to_records(text['gt_morph_analysis']) )
    
    # Assert content of the layer
    expected_records = [ \
         [{'normalized_text': 'Sa', 'lemma': 'sina', 'root_tokens': ('sina',), 'clitic': '', 'start': 0, 'root': 'sina', 'partofspeech': 'P', 'end': 2, 'ending': '0', 'form': 'Sg Nom'}], \
         [{'normalized_text': 'läksid', 'lemma': 'minema', 'root_tokens': ('mine',), 'clitic': '', 'start': 3, 'root': 'mine', 'partofspeech': 'V', 'end': 9, 'ending': 'sid', 'form': 'Pers Prt Ind Sg 2 Aff'}], \
         [{'normalized_text': 'ära', 'lemma': 'ära', 'root_tokens': ('ära',), 'clitic': '', 'start': 10, 'root': 'ära', 'partofspeech': 'D', 'end': 13, 'ending': '0', 'form': ''}], \
         [{'normalized_text': '.', 'lemma': '.', 'root_tokens': ('.',), 'clitic': '', 'start': 13, 'root': '.', 'partofspeech': 'Z', 'end': 14, 'ending': '', 'form': ''}], \
         [{'normalized_text': 'Aga', 'lemma': 'aga', 'root_tokens': ('aga',), 'clitic': '', 'start': 15, 'root': 'aga', 'partofspeech': 'J', 'end': 18, 'ending': '0', 'form': ''}], \
         [{'normalized_text': 'nemad', 'lemma': 'tema', 'root_tokens': ('tema',), 'clitic': '', 'start': 19, 'root': 'tema', 'partofspeech': 'P', 'end': 24, 'ending': 'd', 'form': 'Pl Nom'}], \
         [{'normalized_text': 'tõttasid', 'lemma': 'tõttama', 'root_tokens': ('tõtta',), 'clitic': '', 'start': 25, 'root': 'tõtta', 'partofspeech': 'V', 'end': 33, 'ending': 'sid', 'form': 'Pers Prt Ind Pl 3 Aff'}], \
         [{'normalized_text': 'edasi', 'lemma': 'edasi', 'root_tokens': ('edasi',), 'clitic': '', 'start': 34, 'root': 'edasi', 'partofspeech': 'D', 'end': 39, 'ending': '0', 'form': ''}], \
         [{'normalized_text': ',', 'lemma': ',', 'root_tokens': (',',), 'clitic': '', 'start': 39, 'root': ',', 'partofspeech': 'Z', 'end': 40, 'ending': '', 'form': ''}], \
         [{'normalized_text': 'sind', 'lemma': 'sina', 'root_tokens': ('sina',), 'clitic': '', 'start': 41, 'root': 'sina', 'partofspeech': 'P', 'end': 45, 'ending': 'd', 'form': 'Sg Par'}], \
         [{'normalized_text': 'nad', 'lemma': 'tema', 'root_tokens': ('tema',), 'clitic': '', 'start': 46, 'root': 'tema', 'partofspeech': 'P', 'end': 49, 'ending': 'd', 'form': 'Pl Nom'}], \
         [{'normalized_text': 'ei', 'lemma': 'ei', 'root_tokens': ('ei',), 'clitic': '', 'start': 50, 'root': 'ei', 'partofspeech': 'V', 'end': 52, 'ending': '0', 'form': 'Neg'}], \
         [{'normalized_text': 'näinud', 'lemma': 'nägema', 'root_tokens': ('näge',), 'clitic': '', 'start': 53, 'root': 'näge', 'partofspeech': 'V', 'end': 59, 'ending': 'nud', 'form': 'Pers Prt Ind Neg'}, \
          {'normalized_text': 'näinud', 'lemma': 'näinud', 'root_tokens': ('näinud',), 'clitic': '', 'start': 53, 'root': 'näi=nud', 'partofspeech': 'A', 'end': 59, 'ending': '0', 'form': ''}, \
          {'normalized_text': 'näinud', 'lemma': 'näinud', 'root_tokens': ('näinud',), 'clitic': '', 'start': 53, 'root': 'näi=nud', 'partofspeech': 'A', 'end': 59, 'ending': '0', 'form': 'Sg Nom'}, \
          {'normalized_text': 'näinud', 'lemma': 'näinud', 'root_tokens': ('näinud',), 'clitic': '', 'start': 53, 'root': 'näi=nud', 'partofspeech': 'A', 'end': 59, 'ending': 'd', 'form': 'Pl Nom'}, 
          {'normalized_text': 'näinud', 'lemma': 'näima', 'root_tokens': ('näi',), 'clitic': '', 'start': 53, 'root': 'näi', 'partofspeech': 'V', 'end': 59, 'ending': 'nud', 'form': 'Pers Prt Ind Neg'}], \
         [{'normalized_text': '.', 'lemma': '.', 'root_tokens': ('.',), 'clitic': '', 'start': 59, 'root': '.', 'partofspeech': 'Z', 'end': 60, 'ending': '', 'form': ''}]
    ]
    results = layer_to_records( text['gt_morph_analysis'] )
    _sort_morph_analysis_records( results )
    _sort_morph_analysis_records( expected_records )
    assert expected_records == results



def test_gt_conversion_4_empty():
    gt_converter = GTMorphConverter()
    
    text = Text('')
    text.tag_layer(['morph_analysis', 'clauses'])
    gt_converter.tag( text )
    
    # Assert content of the layer
    #print(layer_to_records(text['gt_morph_analysis']))
    expected_records = []
    assert expected_records == layer_to_records(text['gt_morph_analysis'])


def test_gt_conversion_5_unknown_words():
    # Tests that the conversion does not crash on unknown words
    analyzer = VabamorfAnalyzer(guess=False, propername=False)
    gt_converter = GTMorphConverter()
    
    text = Text('Ma tahax minna järve ääde')
    text.tag_layer(['words','sentences'])
    analyzer.tag(text)
    text.tag_layer(['clauses'])
    gt_converter.tag( text )
    #print(layer_to_records(text['gt_morph_analysis']))

    expected_records = [ \
        [{'normalized_text': 'Ma', 'start': 0, 'root': 'mina', 'form': 'Sg Nom', 'ending': '0', 'partofspeech': 'P', 'clitic': '', 'lemma': 'mina', 'root_tokens': ('mina',), 'end': 2}], \
        [{'normalized_text': None, 'start': 3, 'root': None, 'form': None, 'ending': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'root_tokens': None, 'end': 8}], \
        [{'normalized_text': 'minna', 'start': 9, 'root': 'mine', 'form': 'Inf', 'ending': 'a', 'partofspeech': 'V', 'clitic': '', 'lemma': 'minema', 'root_tokens': ('mine',), 'end': 14}], \
        [{'normalized_text': 'järve', 'start': 15, 'root': 'järv', 'form': 'Sg Ill', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}, \
         {'normalized_text': 'järve', 'start': 15, 'root': 'järv', 'form': 'Sg Gen', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}, \
         {'normalized_text': 'järve', 'start': 15, 'root': 'järv', 'form': 'Sg Par', 'ending': '0', 'partofspeech': 'S', 'clitic': '', 'lemma': 'järv', 'root_tokens': ('järv',), 'end': 20}], \
        [{'normalized_text': None, 'start': 21, 'root': None, 'form': None, 'ending': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'root_tokens': None, 'end': 25}]]
    
    # Assert content of the layer
    results_dict = layer_to_records(text['gt_morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

