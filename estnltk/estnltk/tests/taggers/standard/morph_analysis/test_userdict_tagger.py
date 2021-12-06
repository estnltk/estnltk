from estnltk import Text
from estnltk.common import PACKAGE_PATH

from estnltk.taggers import VabamorfTagger
from estnltk.taggers import UserDictTagger

from estnltk.taggers.standard.morph_analysis.userdict_tagger import CSV_UNSPECIFIED_FIELD

from estnltk.converters import layer_to_dict
from estnltk.converters import dict_to_layer
from estnltk.converters import layer_to_records

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
    # Dictionary with a single entry
    words_dict = { 'kopsujoonis' : {'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S'} }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Tag corrections
    userdict.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'patsient',
                                     'normalized_text': 'Patsiendi',
                                     'partofspeech': 'S',
                                     'root': 'patsient',
                                     'root_tokens': ['patsient']}],
                    'base_span': (0, 9)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'kopsujoonis',
                                     'normalized_text': 'kopsujoonis',
                                     'partofspeech': 'S',
                                     'root': 'kopsu_joonis',
                                     'root_tokens': ['kopsu', 'joonis']}],
                    'base_span': (10, 21)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'vad',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (22, 24)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'loetamatu',
                                     'normalized_text': 'loetamatu',
                                     'partofspeech': 'A',
                                     'root': 'loetamatu',
                                     'root_tokens': ['loetamatu']}],
                    'base_span': (25, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (34, 35)}]
    }
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']

    # Case 2
    text = Text("Jah, femorises.")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Dictionary with a single entry
    words_dict = { 'femorises' : {'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S'} }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Tag corrections
    userdict.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'jah',
                                     'normalized_text': 'Jah',
                                     'partofspeech': 'D',
                                     'root': 'jah',
                                     'root_tokens': ['jah']}],
                    'base_span': (0, 3)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (3, 4)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'femoris',
                                     'normalized_text': 'femorises',
                                     'partofspeech': 'S',
                                     'root': 'femoris',
                                     'root_tokens': ['femoris']}],
                    'base_span': (5, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (14, 15)}]}
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']
    
    # Case 3
    text = Text("Pneumofibroosi unkovertebraalartroosist duodenumisse?")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Dictionary with multiple entries
    words_dict = { 'pneumofibroosi':            {'form': 'sg g', 'root': 'pneumofibroos', 'ending':'0', 'partofspeech': 'S'}, 
                   'unkovertebraalartroosist':  {'form': 'sg el', 'root': 'unkovertebraalartroos', 'ending':'st', 'partofspeech': 'S'},
                   'duodenumisse':              {'form': 'sg ill', 'root': 'duodenum', 'ending':'sse', 'partofspeech': 'S'},
                 }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True)
    # Tag corrections
    userdict.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'pneumofibroos',
                                     'normalized_text': 'Pneumofibroosi',
                                     'partofspeech': 'S',
                                     'root': 'pneumofibroos',
                                     'root_tokens': ['pneumofibroos']}],
                    'base_span': (0, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'st',
                                     'form': 'sg el',
                                     'lemma': 'unkovertebraalartroos',
                                     'normalized_text': 'unkovertebraalartroosist',
                                     'partofspeech': 'S',
                                     'root': 'unkovertebraalartroos',
                                     'root_tokens': ['unkovertebraalartroos']}],
                    'base_span': (15, 39)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'sse',
                                     'form': 'sg ill',
                                     'lemma': 'duodenum',
                                     'normalized_text': 'duodenumisse',
                                     'partofspeech': 'S',
                                     'root': 'duodenum',
                                     'root_tokens': ['duodenum']}],
                    'base_span': (40, 52)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '?',
                                     'normalized_text': '?',
                                     'partofspeech': 'Z',
                                     'root': '?',
                                     'root_tokens': ['?']}],
                    'base_span': (52, 53)}]}
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']


def test_userdict_tagger_complete_overwriting():
    # Tests complete overwriting of all analyses of a word
    
    # Case 1 
    text = Text('Patsiendi kopsujoonis on loetamatu.')
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Dictionary with a single entry
    words_dict = { 'kopsujoonis': [{'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S', 'clitic':''},\
                                   {'form': 'pl in', 'root': 'kopsu_joon',  'ending':'is', 'partofspeech': 'S', 'clitic':''}] }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
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
    #print(layer_to_records(text['morph_analysis']))
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 2
    text = Text("Või jämesoolelingud femorises?")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Dictionary with multiple entries ( completely new analyses that should overwrite old analyses )
    words_dict = { 'jämesoolelingud':  [{'form': 'pl n', 'root': 'jämesoole_ling', 'ending':'d', 'partofspeech': 'S', 'clitic':''}],
                   'femorises':        [{'form': 'sg in', 'root': 'femoris', 'ending':'s', 'partofspeech': 'S', 'clitic':''}] }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True, replace_missing_normalized_text_with_text = True)
    # Tag corrections
    userdict.retag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Või', 'ending': '0', 'form': '', 'partofspeech': 'J', 'root_tokens': ['või',], 'end': 3, 'lemma': 'või', 'start': 0, 'clitic': '', 'root': 'või'}], \
        [{'normalized_text': 'jämesoolelingud', 'end': 19, 'root_tokens': ['jämesoole', 'ling'], 'form': 'pl n', 'lemma': 'jämesooleling', 'root': 'jämesoole_ling', 'partofspeech': 'S', 'clitic': '', 'start': 4, 'ending': 'd'}], \
        [{'normalized_text': 'femorises', 'ending': 's', 'form': 'sg in', 'partofspeech': 'S', 'root_tokens': ['femoris',], 'end': 29, 'lemma': 'femoris', 'start': 20, 'clitic': '', 'root': 'femoris'}], \
        [{'normalized_text': '?', 'ending': '', 'form': '', 'partofspeech': 'Z', 'root_tokens': ['?',], 'end': 30, 'lemma': '?', 'start': 29, 'clitic': '', 'root': '?'}] \
    ]
    #print(layer_to_records(text['morph_analysis']))
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_userdict_tagger_dict_from_csv_file():
    # Tests complete overwriting of all analyses of a word
    # Construct path to testing csv file
    csv_dict_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'taggers', 'standard', 'morph_analysis', 'test_userdict.csv')
    # Load completely new analyses (from a csv file)
    userdict = UserDictTagger(csv_file=csv_dict_path, ignore_case=True, autocorrect_root=True, delimiter=',')
    
    # Case 1
    text = Text("Ah, jälle jämesoolelingud femorises ...")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Tag corrections
    userdict.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ah',
                                     'normalized_text': 'Ah',
                                     'partofspeech': 'I',
                                     'root': 'ah',
                                     'root_tokens': ['ah']}],
                    'base_span': (0, 2)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (2, 3)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'jälle',
                                     'normalized_text': 'jälle',
                                     'partofspeech': 'D',
                                     'root': 'jälle',
                                     'root_tokens': ['jälle']}],
                    'base_span': (4, 9)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'jämesooleling',
                                     'normalized_text': None,
                                     'partofspeech': 'S',
                                     'root': 'jämesoole_ling',
                                     'root_tokens': ['jämesoole', 'ling']}],
                    'base_span': (10, 25)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'femoris',
                                     'normalized_text': None,
                                     'partofspeech': 'S',
                                     'root': 'femoris',
                                     'root_tokens': ['femoris']}],
                    'base_span': (26, 35)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '...',
                                     'normalized_text': '...',
                                     'partofspeech': 'Z',
                                     'root': '...',
                                     'root_tokens': ['...']}],
                    'base_span': (36, 39)}]}
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']


def test_userdict_tagger_post_analysis():
    # Tests that userdict_tagger can be applied after morph analysis and before disambiguation
    morph_analyser = VabamorfTagger(disambiguate=False, guess=False, propername=False)
    
    # Case 1
    text = Text("Ma tahax minna järve ääde")
    # Tag required layers
    text.tag_layer(['words', 'sentences'])
    # Analyse morphology (without guessing, propernames and disambiguation)
    morph_analyser.tag(text)
    # Create user dict tagger (from csv file)
    csv_dict_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'taggers', 'standard', 'morph_analysis', 'test_userdict.csv')
    userdict = UserDictTagger(csv_file=csv_dict_path, ignore_case=True, autocorrect_root=True, delimiter=',')
    # Tag corrections
    userdict.retag(text)
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech',
                        '_ignore'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mina',
                                     'normalized_text': 'Ma',
                                     'partofspeech': 'P',
                                     'root': 'mina',
                                     'root_tokens': ['mina']}],
                    'base_span': (0, 2)},
                   {'annotations': [{'_ignore': None,
                                     'clitic': '',
                                     'ending': 'ks',
                                     'form': 'ks',
                                     'lemma': 'tahtma',
                                     'normalized_text': None,
                                     'partofspeech': 'V',
                                     'root': 'taht',
                                     'root_tokens': ['taht']}],
                    'base_span': (3, 8)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'a',
                                     'form': 'da',
                                     'lemma': 'minema',
                                     'normalized_text': 'minna',
                                     'partofspeech': 'V',
                                     'root': 'mine',
                                     'root_tokens': ['mine']}],
                    'base_span': (9, 14)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'adt',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg p',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']}],
                    'base_span': (15, 20)},
                   {'annotations': [{'_ignore': None,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'äärde',
                                     'normalized_text': None,
                                     'partofspeech': 'K',
                                     'root': 'äärde',
                                     'root_tokens': ['äärde']},
                                    {'_ignore': None,
                                     'clitic': '',
                                     'ending': 'de',
                                     'form': 'adt',
                                     'lemma': 'äär',
                                     'normalized_text': None,
                                     'partofspeech': 'S',
                                     'root': 'äär',
                                     'root_tokens': ['äär']}],
                    'base_span': (21, 25)}]}
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']


def test_userdict_tagger_save_as_csv():
    # Case 1: save as csv 
    # Initialize a dictionary with multiple entries
    words_dict = { 'abieluettepanek':  { 'root': 'abielu_ettepanek', 'partofspeech': 'S' },
                   'kopsujoonis':      [{'form': 'sg n', 'root': 'kopsu_joonis', 'ending':'0', 'partofspeech': 'S', 'clitic':''}],
                   'tahax':            [{'normalized_text':'tahaks', 'root_tokens': ['taht',], 'ending': 'ks', 'clitic': '', 'partofspeech': 'V', 'root': 'taht', 'form': 'ks', 'lemma': 'tahtma'}] }
    userdict = UserDictTagger(words_dict=words_dict, ignore_case=True, autocorrect_root=True)
    result_string = userdict.save_as_csv(None, delimiter=',')
    expected_string = 'text,normalized_text,root,ending,clitic,form,partofspeech\n'+\
        'abieluettepanek,,abielu_ettepanek,'+CSV_UNSPECIFIED_FIELD+','+CSV_UNSPECIFIED_FIELD+','+CSV_UNSPECIFIED_FIELD+',S\n'+\
        'kopsujoonis,,kopsu_joonis,0,,sg n,S\n'+\
        'tahax,tahaks,taht,ks,,ks,V\n'
    result_string_fixed = result_string.replace('\r\n', '\n') # a fix for Windows ( to avoid \r\n )
    assert result_string_fixed == expected_string

    # Case 2: restore from saved csv
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False)
    # Write output of the save_as_csv 
    fp.write( result_string_fixed )
    fp.close()
    result_string2 = ''
    try:
        userdict2 = UserDictTagger( csv_file=fp.name, encoding='utf-8', delimiter=',' )
        result_string2 = userdict2.save_as_csv(None, delimiter=',')
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)
    assert result_string2 == result_string



def test_userdict_tagger_words_with_skip_existing_analyses():
    # Create a morph analyser that does not guess unknown words
    morph_analyser = VabamorfTagger( disambiguate=False, guess=False, propername=False )
    # Example text
    example_text_str = 'vampiiri olla öösel üts vai läbistand'
    # Create UserDictTagger that does not overwrite existing / analysed words
    # Initialize a dictionary with multiple entries
    words_dict = { \
      'vampiiri':  [{'form': 'sg g', 'root': 'vampiir', 'ending':'0', 'partofspeech': 'S', 'clitic':''}],
      'vai':       [{'form': '', 'root': 'või', 'ending':'0', 'partofspeech': 'J', 'clitic':''}],
      'üts':       [{'form': 'sg n', 'root': 'üks', 'ending':'0', 'partofspeech': 'N', 'clitic':''}],
      'läbistand': [{'form': 'nud', 'root': 'läbista', 'ending':'nud', 'partofspeech': 'V', 'clitic':''}],
    }
    userdict = UserDictTagger( words_dict=words_dict, ignore_case=True, overwrite_existing=False )
    text = Text( example_text_str )
    text.tag_layer( ['words', 'sentences'] )
    morph_analyser.tag( text )
    # Check analyses before applying userdict
    before_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        before_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    assert before_analyses == [ ['vampiiri', ('vampiir', 'S', 'adt'), ('vampiir', 'S', 'sg g'), ('vampiir', 'S', 'sg p')], \
                                ['olla', ('ole', 'V', 'da')], ['öösel', ('öösel', 'D', '')], ['üts', (None, None, None)], \
                                ['vai', ('vai', 'S', 'sg n')], ['läbistand', (None, None, None)] ]
    userdict.retag( text )
    # Check analyses after applying userdict
    after_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        after_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    assert after_analyses == [ ['vampiiri', ('vampiir', 'S', 'adt'), ('vampiir', 'S', 'sg g'), ('vampiir', 'S', 'sg p')], \
                               ['olla', ('ole', 'V', 'da')], ['öösel', ('öösel', 'D', '')], ['üts', ('üks', 'N', 'sg n')], \
                               ['vai', ('vai', 'S', 'sg n')], ['läbistand', ('läbista', 'V', 'nud')] ]


