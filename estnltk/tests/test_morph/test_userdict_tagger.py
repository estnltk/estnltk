from estnltk import Text
from estnltk.core import PACKAGE_PATH

from estnltk.taggers import VabamorfTagger
from estnltk.taggers import UserDictTagger


import os, os.path, tempfile

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

def test_userdict_tagger_partial_corrections():
    # Tests partial corrections: 
    #   overwriting not all, but only some fields of analyses;
    
    # Case 1 
    text = Text('Patsiendi kopsujoonis on loetamatu.')
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Add analysis of a single word
    userdict.add_word('kopsujoonis', {'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S'} )
    # Tag corrections
    userdict.retag(text)
    expected_records = [ \
        [{'normalized_text': 'Patsiendi', 'root_tokens': ['patsient',], 'lemma': 'patsient', 'end': 9, 'start': 0, 'form': 'sg g', 'root': 'patsient', 'ending': '0', 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': 'kopsujoonis', 'ending': '0', 'clitic': '', 'start': 10, 'lemma': 'kopsujoonis', 'form': 'sg n', 'root_tokens': ['kopsu', 'joonis'], 'partofspeech': 'S', 'end': 21, 'root': 'kopsu_joonis'}],\
        [{'normalized_text': 'on', 'root_tokens': ['ole',], 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'b', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}, {'normalized_text': 'on', 'root_tokens': ['ole',], 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'vad', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}], \
        [{'normalized_text': 'loetamatu', 'root_tokens': ['loetamatu',], 'lemma': 'loetamatu', 'end': 34, 'start': 25, 'form': 'sg n', 'root': 'loetamatu', 'ending': '0', 'clitic': '', 'partofspeech': 'A'}], \
        [{'normalized_text': '.', 'root_tokens': ['.',], 'lemma': '.', 'end': 35, 'start': 34, 'form': '', 'root': '.', 'ending': '', 'clitic': '', 'partofspeech': 'Z'}]
    ]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2
    text = Text("Jah, femorises.")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Add analysis of a single word
    userdict.add_word('femorises', {'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S'} )
    # Tag corrections
    userdict.retag(text)
    expected_records = [ \
        [{'normalized_text': 'Jah', 'form': '', 'lemma': 'jah', 'clitic': '', 'start': 0, 'end': 3, 'root_tokens': ['jah',], 'root': 'jah', 'ending': '0', 'partofspeech': 'D'}],\
        [{'normalized_text': ',', 'form': '', 'lemma': ',', 'clitic': '', 'start': 3, 'end': 4, 'root_tokens': [',',], 'root': ',', 'ending': '', 'partofspeech': 'Z'}], \
        [{'normalized_text': 'femorises', 'start': 5, 'root': 'femoris', 'root_tokens': ['femoris',], 'ending': 's', 'form': 'sg in', 'end': 14, 'partofspeech': 'S', 'lemma': 'femoris', 'clitic': ''}], \
        [{'normalized_text': '.', 'form': '', 'lemma': '.', 'clitic': '', 'start': 14, 'end': 15, 'root_tokens': ['.',], 'root': '.', 'ending': '', 'partofspeech': 'Z'}] ]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 3
    text = Text("Pneumofibroosi unkovertebraalartroosist duodenumisse?")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Add partial corrections for words
    userdict.add_word('pneumofibroosi', \
        {'form': 'sg g', 'root': 'pneumofibroos', 'ending':'0', 'partofspeech': 'S'} )
    userdict.add_word('unkovertebraalartroosist', \
        {'form': 'sg el', 'root': 'unkovertebraalartroos', 'ending':'st', 'partofspeech': 'S'} )
    userdict.add_word('duodenumisse', \
        {'form': 'sg ill', 'root': 'duodenum', 'ending':'sse', 'partofspeech': 'S'} )
    # Tag corrections
    userdict.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'normalized_text': 'Pneumofibroosi', 'root_tokens': ['pneumofibroos',], 'root': 'pneumofibroos', 'form': 'sg g', 'ending': '0', 'lemma': 'pneumofibroos', 'end': 14, 'start': 0, 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': 'unkovertebraalartroosist', 'root_tokens': ['unkovertebraalartroos',], 'root': 'unkovertebraalartroos', 'form': 'sg el', 'ending': 'st', 'lemma': 'unkovertebraalartroos', 'end': 39, 'start': 15, 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': 'duodenumisse', 'root_tokens': ['duodenum',], 'root': 'duodenum', 'form': 'sg ill', 'ending': 'sse', 'lemma': 'duodenum', 'end': 52, 'start': 40, 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': '?', 'root_tokens': ['?',], 'root': '?', 'form': '', 'ending': '', 'lemma': '?', 'end': 53, 'start': 52, 'clitic': '', 'partofspeech': 'Z'}] \
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict



def test_userdict_tagger_complete_overwriting():
    # Tests complete overwriting of all analyses of a word
    
    # Case 1 
    text = Text('Patsiendi kopsujoonis on loetamatu.')
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Add completely new analyses for a single word
    userdict.add_word('kopsujoonis', \
        [{'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S', 'clitic':''},\
         {'form': 'pl in', 'root': 'kopsu_joon',  'ending':'is', 'partofspeech': 'S', 'clitic':''}] )
    # Tag corrections
    userdict.retag(text)
    expected_records = [ \
        [{'normalized_text': 'Patsiendi', 'root_tokens': ['patsient',], 'lemma': 'patsient', 'end': 9, 'start': 0, 'form': 'sg g', 'root': 'patsient', 'ending': '0', 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': 'kopsujoonis', 'ending': '0', 'partofspeech': 'S', 'form': 'sg n', 'start': 10, 'root': 'kopsu_joonis', 'end': 21, 'clitic': '', 'lemma': 'kopsujoonis', 'root_tokens': ['kopsu', 'joonis']}, \
         {'normalized_text': 'kopsujoonis', 'ending': 'is', 'partofspeech': 'S', 'form': 'pl in', 'start': 10, 'root': 'kopsu_joon', 'end': 21, 'clitic': '', 'lemma': 'kopsujoon', 'root_tokens': ['kopsu', 'joon']}],\
        [{'normalized_text': 'on', 'root_tokens': ['ole',], 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'b', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}, {'normalized_text': 'on', 'root_tokens': ['ole',], 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'vad', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}], \
        [{'normalized_text': 'loetamatu', 'root_tokens': ['loetamatu',], 'lemma': 'loetamatu', 'end': 34, 'start': 25, 'form': 'sg n', 'root': 'loetamatu', 'ending': '0', 'clitic': '', 'partofspeech': 'A'}], \
        [{'normalized_text': '.', 'root_tokens': ['.',], 'lemma': '.', 'end': 35, 'start': 34, 'form': '', 'root': '.', 'ending': '', 'clitic': '', 'partofspeech': 'Z'}]
    ]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 2
    text = Text("Või jämesoolelingud femorises?")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Add completely new analyses that should overwrite old analyses
    userdict.add_word('jämesoolelingud', \
        [{'form': 'pl n', 'root': 'jämesoole_ling', 'ending':'d', 'partofspeech': 'S', 'clitic':''}] )
    userdict.add_word('femorises', \
        [{'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S', 'clitic':''}] )
    # Tag corrections
    userdict.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'normalized_text': 'Või', 'ending': '0', 'form': '', 'partofspeech': 'J', 'root_tokens': ['või',], 'end': 3, 'lemma': 'või', 'start': 0, 'clitic': '', 'root': 'või'}], \
        [{'normalized_text': 'jämesoolelingud', 'end': 19, 'root_tokens': ['jämesoole', 'ling'], 'form': 'pl n', 'lemma': 'jämesooleling', 'root': 'jämesoole_ling', 'partofspeech': 'S', 'clitic': '', 'start': 4, 'ending': 'd'}], \
        [{'normalized_text': 'femorises', 'ending': 's', 'form': 'sg in', 'partofspeech': 'S', 'root_tokens': ['femoris',], 'end': 29, 'lemma': 'femoris', 'start': 20, 'clitic': '', 'root': 'femoris'}], \
        [{'normalized_text': '?', 'ending': '', 'form': '', 'partofspeech': 'Z', 'root_tokens': ['?',], 'end': 30, 'lemma': '?', 'start': 29, 'clitic': '', 'root': '?'}] \
    ]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_userdict_tagger_dict_from_csv_file():
    # Tests complete overwriting of all analyses of a word
    # Construct path to testing csv file
    csv_dict_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'test_morph', 'test_userdict.csv')
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Load completely new analyses (from csv file )
    userdict.add_words_from_csv_file( csv_dict_path , delimiter=',')
    
    # Case 1
    text = Text("Ah, jälle jämesoolelingud femorises ...")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Tag corrections
    userdict.retag(text)
    expected_records = [ \
        [{'normalized_text': 'Ah', 'lemma': 'ah', 'root': 'ah', 'end': 2, 'clitic': '', 'ending': '0', 'start': 0, 'form': '', 'partofspeech': 'I', 'root_tokens': ['ah',]}], \
        [{'normalized_text': ',', 'lemma': ',', 'root': ',', 'end': 3, 'clitic': '', 'ending': '', 'start': 2, 'form': '', 'partofspeech': 'Z', 'root_tokens': [',',]}], \
        [{'normalized_text': 'jälle', 'lemma': 'jälle', 'root': 'jälle', 'end': 9, 'clitic': '', 'ending': '0', 'start': 4, 'form': '', 'partofspeech': 'D', 'root_tokens': ['jälle',]}], \
        [{'normalized_text': None, 'lemma': 'jämesooleling', 'root': 'jämesoole_ling', 'end': 25, 'clitic': '', 'ending': 'd', 'start': 10, 'form': 'pl n', 'partofspeech': 'S', 'root_tokens': ['jämesoole', 'ling']}], \
        [{'normalized_text': None, 'lemma': 'femoris', 'root': 'femoris', 'end': 35, 'clitic': '', 'ending': 's', 'start': 26, 'form': 'sg in', 'partofspeech': 'S', 'root_tokens': ['femoris',]}], \
        [{'normalized_text': '...', 'lemma': '...', 'root': '...', 'end': 39, 'clitic': '', 'ending': '', 'start': 36, 'form': '', 'partofspeech': 'Z', 'root_tokens': ['...',]}] \
    ]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict



def test_userdict_tagger_post_analysis():
    # Tests that userdict_tagger can be applied after morph analysis and before disambiguation
    morph_analyser = VabamorfTagger(disambiguate=False, guess=False, propername=False)
    
    # Case 1
    text = Text("Ma tahax minna järve ääde")
    # Tag required layers
    text.tag_layer(['words', 'sentences'])
    # Analyse morphology (without guessing, propernames and disambiguation)
    morph_analyser.tag(text)
    # Create user dict tagger
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    csv_dict_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'test_morph', 'test_userdict.csv')
    # Load completely new analyses (from csv file)
    userdict.add_words_from_csv_file(csv_dict_path , delimiter=',')
    # Tag corrections
    userdict.retag(text)
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Ma', 'root_tokens': ['mina',], 'start': 0, 'ending': '0', '_ignore': False, 'end': 2, 'clitic': '', 'partofspeech': 'P', 'root': 'mina', 'form': 'sg n', 'lemma': 'mina'}], \
        [{'normalized_text': None, 'root_tokens': ['taht',], 'start': 3, 'ending': 'ks', '_ignore': None, 'end': 8, 'clitic': '', 'partofspeech': 'V', 'root': 'taht', 'form': 'ks', 'lemma': 'tahtma'}], \
        [{'normalized_text': 'minna', 'root_tokens': ['mine',], 'start': 9, 'ending': 'a', '_ignore': False, 'end': 14, 'clitic': '', 'partofspeech': 'V', 'root': 'mine', 'form': 'da', 'lemma': 'minema'}], \
        [{'normalized_text': 'järve', 'root_tokens': ['järv',], 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'adt', 'lemma': 'järv'}, \
         {'normalized_text': 'järve', 'root_tokens': ['järv',], 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'sg g', 'lemma': 'järv'}, \
         {'normalized_text': 'järve', 'root_tokens': ['järv',], 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'sg p', 'lemma': 'järv'}], \
        [{'normalized_text': None, 'root_tokens': ['äärde',], 'start': 21, 'ending': '0', '_ignore': None, 'end': 25, 'clitic': '', 'partofspeech': 'K', 'root': 'äärde', 'form': '', 'lemma': 'äärde'}, \
         {'normalized_text': None, 'root_tokens': ['äär',], 'start': 21, 'ending': 'de', '_ignore': None, 'end': 25, 'clitic': '', 'partofspeech': 'S', 'root': 'äär', 'form': 'adt', 'lemma': 'äär'}] \
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


from estnltk.taggers.morph_analysis.userdict_tagger import CSV_UNSPECIFIED_FIELD

def test_userdict_tagger_save_as_csv():
    # Case 1: save as csv 
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    userdict.add_word('abieluettepanek', \
        { 'root': 'abielu_ettepanek', 'partofspeech': 'S' } )
    userdict.add_word('kopsujoonis', \
        [{'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S', 'clitic':''}] )
    userdict.add_word('tahax', \
        [{'normalized_text':'tahaks', 'root_tokens': ['taht',], 'ending': 'ks', 'clitic': '', 'partofspeech': 'V', 'root': 'taht', 'form': 'ks', 'lemma': 'tahtma'}] )
    result_string = userdict.save_as_csv(None, delimiter=',')
    expected_string = 'text,normalized_text,root,ending,clitic,form,partofspeech\n'+\
        'abieluettepanek,,abielu_ettepanek,'+CSV_UNSPECIFIED_FIELD+','+CSV_UNSPECIFIED_FIELD+','+CSV_UNSPECIFIED_FIELD+',S\n'+\
        'kopsujoonis,,kopsu_joonis,0,,sg n,S\n'+\
        'tahax,tahaks,taht,ks,,ks,V\n'
    result_string_fixed = result_string.replace(os.linesep, '\n') # a fix for Windows ( to avoid \r\n )
    assert result_string_fixed == expected_string

    # Case 2: restore from saved csv
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False)
    # Write output of the save_as_csv 
    fp.write( result_string_fixed )
    fp.close()
    result_string2 = ''
    try:
        userdict2 = UserDictTagger()
        userdict2.add_words_from_csv_file(fp.name, encoding='utf-8', delimiter=',')
        result_string2 = userdict2.save_as_csv(None, delimiter=',')
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)
    assert result_string2 == result_string


