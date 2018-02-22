from estnltk import Text
from estnltk.core import PACKAGE_PATH

from estnltk.taggers import VabamorfTagger
from estnltk.taggers.morph.userdict_tagger import UserDictTagger


import os.path

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
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Add analysis of a single word
    userdict.add_word('kopsujoonis', {'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S'} )
    # Tag corrections
    userdict.tag(text)
    expected_records = [ \
        [{'root_tokens': ('patsient',), 'lemma': 'patsient', 'end': 9, 'start': 0, 'form': 'sg g', 'root': 'patsient', 'ending': '0', 'clitic': '', 'partofspeech': 'S'}], \
        [{'ending': '0', 'clitic': '', 'start': 10, 'lemma': 'kopsujoonis', 'form': 'sg n', 'root_tokens': ('kopsu', 'joonis'), 'partofspeech': 'S', 'end': 21, 'root': 'kopsu_joonis'}],\
        [{'root_tokens': ('ole',), 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'b', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}, {'root_tokens': ('ole',), 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'vad', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}], \
        [{'root_tokens': ('loetamatu',), 'lemma': 'loetamatu', 'end': 34, 'start': 25, 'form': 'sg n', 'root': 'loetamatu', 'ending': '0', 'clitic': '', 'partofspeech': 'A'}], \
        [{'root_tokens': ('.',), 'lemma': '.', 'end': 35, 'start': 34, 'form': '', 'root': '.', 'ending': '', 'clitic': '', 'partofspeech': 'Z'}]
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
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Add analysis of a single word
    userdict.add_word('femorises', {'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S'} )
    # Tag corrections
    userdict.tag(text)
    expected_records = [ \
        [{'form': '', 'lemma': 'jah', 'clitic': '', 'start': 0, 'end': 3, 'root_tokens': ('jah',), 'root': 'jah', 'ending': '0', 'partofspeech': 'D'}],\
        [{'form': '', 'lemma': ',', 'clitic': '', 'start': 3, 'end': 4, 'root_tokens': (',',), 'root': ',', 'ending': '', 'partofspeech': 'Z'}], \
        [{'start': 5, 'root': 'femoris', 'root_tokens': ('femoris',), 'ending': 's', 'form': 'sg in', 'end': 14, 'partofspeech': 'S', 'lemma': 'femoris', 'clitic': ''}], \
        [{'form': '', 'lemma': '.', 'clitic': '', 'start': 14, 'end': 15, 'root_tokens': ('.',), 'root': '.', 'ending': '', 'partofspeech': 'Z'}] ]
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
    userdict.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'root_tokens': ('pneumofibroos',), 'root': 'pneumofibroos', 'form': 'sg g', 'ending': '0', 'lemma': 'pneumofibroos', 'end': 14, 'start': 0, 'clitic': '', 'partofspeech': 'S'}], \
        [{'root_tokens': ('unkovertebraalartroos',), 'root': 'unkovertebraalartroos', 'form': 'sg el', 'ending': 'st', 'lemma': 'unkovertebraalartroos', 'end': 39, 'start': 15, 'clitic': '', 'partofspeech': 'S'}], \
        [{'root_tokens': ('duodenum',), 'root': 'duodenum', 'form': 'sg ill', 'ending': 'sse', 'lemma': 'duodenum', 'end': 52, 'start': 40, 'clitic': '', 'partofspeech': 'S'}], \
        [{'root_tokens': ('?',), 'root': '?', 'form': '', 'ending': '', 'lemma': '?', 'end': 53, 'start': 52, 'clitic': '', 'partofspeech': 'Z'}] \
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
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Add completely new analyses for a single word
    userdict.add_word('kopsujoonis', \
        [{'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S', 'clitic':''},\
         {'form': 'pl in', 'root': 'kopsu_joon',  'ending':'is', 'partofspeech': 'S', 'clitic':''}] )
    # Tag corrections
    userdict.tag(text)
    expected_records = [ \
        [{'root_tokens': ('patsient',), 'lemma': 'patsient', 'end': 9, 'start': 0, 'form': 'sg g', 'root': 'patsient', 'ending': '0', 'clitic': '', 'partofspeech': 'S'}], \
        [{'ending': '0', 'partofspeech': 'S', 'form': 'sg n', 'start': 10, 'root': 'kopsu_joonis', 'end': 21, 'clitic': '', 'lemma': 'kopsujoonis', 'root_tokens': ('kopsu', 'joonis')}, \
         {'ending': 'is', 'partofspeech': 'S', 'form': 'pl in', 'start': 10, 'root': 'kopsu_joon', 'end': 21, 'clitic': '', 'lemma': 'kopsujoon', 'root_tokens': ('kopsu', 'joon')}],\
        [{'root_tokens': ('ole',), 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'b', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}, {'root_tokens': ('ole',), 'lemma': 'olema', 'end': 24, 'start': 22, 'form': 'vad', 'root': 'ole', 'ending': '0', 'clitic': '', 'partofspeech': 'V'}], \
        [{'root_tokens': ('loetamatu',), 'lemma': 'loetamatu', 'end': 34, 'start': 25, 'form': 'sg n', 'root': 'loetamatu', 'ending': '0', 'clitic': '', 'partofspeech': 'A'}], \
        [{'root_tokens': ('.',), 'lemma': '.', 'end': 35, 'start': 34, 'form': '', 'root': '.', 'ending': '', 'clitic': '', 'partofspeech': 'Z'}]
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
    userdict = UserDictTagger(ignore_case=True, autocorrect_root=True)
    # Add completely new analyses that should overwrite old analyses
    userdict.add_word('jämesoolelingud', \
        [{'form': 'pl n', 'root': 'jämesoole_ling', 'ending':'d', 'partofspeech': 'S', 'clitic':''}] )
    userdict.add_word('femorises', \
        [{'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S', 'clitic':''}] )
    # Tag corrections
    userdict.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'ending': '0', 'form': '', 'partofspeech': 'J', 'root_tokens': ('või',), 'end': 3, 'lemma': 'või', 'start': 0, 'clitic': '', 'root': 'või'}], \
        [{'end': 19, 'root_tokens': ('jämesoole', 'ling'), 'form': 'pl n', 'lemma': 'jämesooleling', 'root': 'jämesoole_ling', 'partofspeech': 'S', 'clitic': '', 'start': 4, 'ending': 'd'}], \
        [{'ending': 's', 'form': 'sg in', 'partofspeech': 'S', 'root_tokens': ('femoris',), 'end': 29, 'lemma': 'femoris', 'start': 20, 'clitic': '', 'root': 'femoris'}], \
        [{'ending': '', 'form': '', 'partofspeech': 'Z', 'root_tokens': ('?',), 'end': 30, 'lemma': '?', 'start': 29, 'clitic': '', 'root': '?'}] \
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
    userdict.tag(text)
    expected_records = [ \
        [{'lemma': 'ah', 'root': 'ah', 'end': 2, 'clitic': '', 'ending': '0', 'start': 0, 'form': '', 'partofspeech': 'I', 'root_tokens': ('ah',)}], \
        [{'lemma': ',', 'root': ',', 'end': 3, 'clitic': '', 'ending': '', 'start': 2, 'form': '', 'partofspeech': 'Z', 'root_tokens': (',',)}], \
        [{'lemma': 'jälle', 'root': 'jälle', 'end': 9, 'clitic': '', 'ending': '0', 'start': 4, 'form': '', 'partofspeech': 'D', 'root_tokens': ('jälle',)}], \
        [{'lemma': 'jämesooleling', 'root': 'jämesoole_ling', 'end': 25, 'clitic': '', 'ending': 'd', 'start': 10, 'form': 'pl n', 'partofspeech': 'S', 'root_tokens': ('jämesoole', 'ling')}], \
        [{'lemma': 'femoris', 'root': 'femoris', 'end': 35, 'clitic': '', 'ending': 's', 'start': 26, 'form': 'sg in', 'partofspeech': 'S', 'root_tokens': ('femoris',)}], \
        [{'lemma': '...', 'root': '...', 'end': 39, 'clitic': '', 'ending': '', 'start': 36, 'form': '', 'partofspeech': 'Z', 'root_tokens': ('...',)}] \
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
    morph_analyser = VabamorfTagger( disambiguate=False, guess=False, propername=False )
    
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
    userdict.tag(text)
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'root_tokens': ('mina',), 'start': 0, 'ending': '0', '_ignore': False, 'end': 2, 'clitic': '', 'partofspeech': 'P', 'root': 'mina', 'form': 'sg n', 'lemma': 'mina'}], \
        [{'root_tokens': ('taht',), 'start': 3, 'ending': 'ks', '_ignore': None, 'end': 8, 'clitic': '', 'partofspeech': 'V', 'root': 'taht', 'form': 'ks', 'lemma': 'tahtma'}], \
        [{'root_tokens': ('mine',), 'start': 9, 'ending': 'a', '_ignore': False, 'end': 14, 'clitic': '', 'partofspeech': 'V', 'root': 'mine', 'form': 'da', 'lemma': 'minema'}], \
        [{'root_tokens': ('järv',), 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'adt', 'lemma': 'järv'}, \
         {'root_tokens': ('järv',), 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'sg g', 'lemma': 'järv'}, \
         {'root_tokens': ('järv',), 'start': 15, 'ending': '0', '_ignore': False, 'end': 20, 'clitic': '', 'partofspeech': 'S', 'root': 'järv', 'form': 'sg p', 'lemma': 'järv'}], \
        [{'root_tokens': ('äärde',), 'start': 21, 'ending': '0', '_ignore': None, 'end': 25, 'clitic': '', 'partofspeech': 'K', 'root': 'äärde', 'form': '', 'lemma': 'äärde'}, \
         {'root_tokens': ('äär',), 'start': 21, 'ending': 'de', '_ignore': None, 'end': 25, 'clitic': '', 'partofspeech': 'S', 'root': 'äär', 'form': 'adt', 'lemma': 'äär'}] \
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

