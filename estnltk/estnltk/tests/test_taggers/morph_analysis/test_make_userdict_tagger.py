#
# Tests make_userdict: an automatic creation of UserDictTagger based on given normalizations 
#
from estnltk import Text

from estnltk.taggers.standard.morph_analysis.make_userdict import make_userdict

from estnltk.converters import layer_to_dict
from estnltk.converters import dict_to_layer

# ----------------------------------

def test_make_userdict_1():
    # Case 1

    text = Text("see onn hädavajalik vajd merel, xhus vxi metsas")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Create UserDictTagger with corrections
    userdict = make_userdict({'onn':'on',
                              'vajd':'vaid',
                              'xhus':'õhus',
                              'vxi':'või'}, 
                              ignore_case=True)
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
                                     'form': 'sg n',
                                     'lemma': 'see',
                                     'normalized_text': 'see',
                                     'partofspeech': 'P',
                                     'root': 'see',
                                     'root_tokens': ['see']}],
                    'base_span': (0, 3)},
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
                    'base_span': (4, 7)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'hädavajalik',
                                     'normalized_text': 'hädavajalik',
                                     'partofspeech': 'A',
                                     'root': 'häda_vajalik',
                                     'root_tokens': ['häda', 'vajalik']}],
                    'base_span': (8, 19)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'vaid',
                                     'normalized_text': 'vaid',
                                     'partofspeech': 'D',
                                     'root': 'vaid',
                                     'root_tokens': ['vaid']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'vaid',
                                     'normalized_text': 'vaid',
                                     'partofspeech': 'J',
                                     'root': 'vaid',
                                     'root_tokens': ['vaid']}],
                    'base_span': (20, 24)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'l',
                                     'form': 'sg ad',
                                     'lemma': 'meri',
                                     'normalized_text': 'merel',
                                     'partofspeech': 'S',
                                     'root': 'meri',
                                     'root_tokens': ['meri']}],
                    'base_span': (25, 30)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (30, 31)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'õhk',
                                     'normalized_text': 'õhus',
                                     'partofspeech': 'S',
                                     'root': 'õhk',
                                     'root_tokens': ['õhk']}],
                    'base_span': (32, 36)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'või',
                                     'normalized_text': 'või',
                                     'partofspeech': 'S',
                                     'root': 'või',
                                     'root_tokens': ['või']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'o',
                                     'lemma': 'võima',
                                     'normalized_text': 'või',
                                     'partofspeech': 'V',
                                     'root': 'või',
                                     'root_tokens': ['või']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'või',
                                     'normalized_text': 'või',
                                     'partofspeech': 'D',
                                     'root': 'või',
                                     'root_tokens': ['või']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'või',
                                     'normalized_text': 'või',
                                     'partofspeech': 'J',
                                     'root': 'või',
                                     'root_tokens': ['või']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'või',
                                     'normalized_text': 'või',
                                     'partofspeech': 'S',
                                     'root': 'või',
                                     'root_tokens': ['või']}],
                    'base_span': (37, 40)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'mets',
                                     'normalized_text': 'metsas',
                                     'partofspeech': 'S',
                                     'root': 'mets',
                                     'root_tokens': ['mets']}],
                    'base_span': (41, 47)}]
    }
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']


def test_make_userdict_2():
    # Case 2

    text = Text("Mxnel ka igapäävased kxnekeeleväljändid sellged")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Create UserDictTagger with corrections
    userdict = make_userdict({'mxnel':'mõnel',
                              'igapäävased':'igapäevased',
                              'kxnekeeleväljändid':'kõnekeeleväljendid',
                              'sellged':'selged'}, 
                              ignore_case=True)
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
                                     'ending': 'l',
                                     'form': 'sg ad',
                                     'lemma': 'mõni',
                                     'normalized_text': 'mõnel',
                                     'partofspeech': 'P',
                                     'root': 'mõni',
                                     'root_tokens': ['mõni']}],
                    'base_span': (0, 5)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ka',
                                     'normalized_text': 'ka',
                                     'partofspeech': 'D',
                                     'root': 'ka',
                                     'root_tokens': ['ka']}],
                    'base_span': (6, 8)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'igapäevane',
                                     'normalized_text': 'igapäevased',
                                     'partofspeech': 'A',
                                     'root': 'iga_päevane',
                                     'root_tokens': ['iga', 'päevane']}],
                    'base_span': (9, 20)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'kõnekeeleväljend',
                                     'normalized_text': 'kõnekeeleväljendid',
                                     'partofspeech': 'S',
                                     'root': 'kõne_keele_väljend',
                                     'root_tokens': ['kõne', 'keele', 'väljend']}],
                    'base_span': (21, 39)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'selge',
                                     'normalized_text': 'selged',
                                     'partofspeech': 'A',
                                     'root': 'selge',
                                     'root_tokens': ['selge']}],
                    'base_span': (40, 47)}]
    }
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']


def test_make_userdict_3():
    # Case 3 (some words may have more than one possible normalizations)
    
    text = Text("Mxne mehed neet nyt")
    # Tag required layers
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # Create UserDictTagger with corrections
    userdict = make_userdict({'mxne':['mõne', 'mõned'],
                              'neet':'need',
                              'nyt':'nüüd'}, 
                              ignore_case=True)
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
                                     'lemma': 'mõni',
                                     'normalized_text': 'mõne',
                                     'partofspeech': 'P',
                                     'root': 'mõni',
                                     'root_tokens': ['mõni']},
                                    {'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'mõni',
                                     'normalized_text': 'mõned',
                                     'partofspeech': 'P',
                                     'root': 'mõni',
                                     'root_tokens': ['mõni']}],
                    'base_span': (0, 4)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'mees',
                                     'normalized_text': 'mehed',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']}],
                    'base_span': (5, 10)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'see',
                                     'normalized_text': 'need',
                                     'partofspeech': 'P',
                                     'root': 'see',
                                     'root_tokens': ['see']}],
                    'base_span': (11, 15)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'nüüd',
                                     'normalized_text': 'nüüd',
                                     'partofspeech': 'D',
                                     'root': 'nüüd',
                                     'root_tokens': ['nüüd']}],
                    'base_span': (16, 19)}]
    }
    # Check results
    assert dict_to_layer( expected_layer_dict ) == text['morph_analysis']

