import pkgutil
import pytest
import tempfile, os

from estnltk.converters import dict_to_text
from estnltk.converters import layer_to_dict

def check_if_conllu_is_available():
    # Check if conllu is available
    return pkgutil.find_loader("conllu") is not None

input_conll_ner_str = \
'''
Meie			O
Päikesesüsteemis			O
on			O
lisaks			O
Maale			B-PLANEET
veel			O
kolm			O
väiksemat			O
siseplaneeti			O
:			O
Merkuur			B-PLANEET
,			O
Veenus			B-PLANEET
ja			O
Marss			B-PLANEET
.			O

Kaks			O
suurimat			O
planeeti			O
on			O
Jupiter			B-PLANEET
ja			O
Saturn			B-PLANEET
.			O
'''


@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_conll_ner_importer():
    from estnltk.converters.conll.conll_ner_importer import conll_to_ner_labelling
    
    # Write into .conll tempfile
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.conll', delete=False)
    fp.write( input_conll_ner_str )
    fp.close()

    # Read ner annotations from .conll 
    text = None
    try:
        text = conll_to_ner_labelling( fp.name, ner_layer='conll_wordner' )
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)
  
    expected_wordner_layer_dict = \
        {'ambiguous': False,
         'attributes': ('nertag',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'conll_wordner',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'nertag': 'O'}], 'base_span': (0, 4)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (5, 21)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (22, 24)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (25, 31)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (32, 37)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (38, 42)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (43, 47)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (48, 57)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (58, 70)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (71, 72)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (73, 80)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (81, 82)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (83, 89)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (90, 92)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (93, 98)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (99, 100)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (101, 105)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (106, 114)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (115, 123)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (124, 126)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (127, 134)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (135, 137)},
                   {'annotations': [{'nertag': 'B-PLANEET'}], 'base_span': (138, 144)},
                   {'annotations': [{'nertag': 'O'}], 'base_span': (145, 146)}]}
  
    assert 'conll_wordner' in text.layers
    assert layer_to_dict( text['conll_wordner'] ) == expected_wordner_layer_dict


@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_conll_ner_exporter():
    from estnltk.converters.conll.conll_ner_exporter import ner_labelling_to_conll

    input_text_with_ner_dict = \
        {'layers': [{'ambiguous': True,
                     'attributes': ('normalized_form',),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {},
                     'name': 'words',
                     'parent': None,
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'normalized_form': None}],
                                'base_span': (0, 2)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (3, 9)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (10, 18)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (19, 34)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (35, 38)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (39, 42)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (43, 51)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (51, 52)}]},
                    {'ambiguous': True,
                     'attributes': ('normalized_text',
                                    'lemma',
                                    'root',
                                    'root_tokens',
                                    'ending',
                                    'clitic',
                                    'form',
                                    'partofspeech'),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {},
                     'name': 'morph_analysis',
                     'parent': 'words',
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': 'sg n',
                                                 'lemma': 'tema',
                                                 'normalized_text': 'Ta',
                                                 'partofspeech': 'P',
                                                 'root': 'tema',
                                                 'root_tokens': ['tema']}],
                                'base_span': (0, 2)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'is',
                                                 'form': 's',
                                                 'lemma': 'jõudma',
                                                 'normalized_text': 'jõudis',
                                                 'partofspeech': 'V',
                                                 'root': 'jõud',
                                                 'root_tokens': ['jõud']}],
                                'base_span': (3, 9)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': 'sg g',
                                                 'lemma': 'Ameerika',
                                                 'normalized_text': 'Ameerika',
                                                 'partofspeech': 'H',
                                                 'root': 'Ameerika',
                                                 'root_tokens': ['Ameerika']}],
                                'base_span': (10, 18)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'desse',
                                                 'form': 'pl ill',
                                                 'lemma': 'ühendriik',
                                                 'normalized_text': 'Ühendriikidesse',
                                                 'partofspeech': 'S',
                                                 'root': 'ühend_riik',
                                                 'root_tokens': ['ühend', 'riik']}],
                                'base_span': (19, 34)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': '',
                                                 'lemma': 'või',
                                                 'normalized_text': 'või',
                                                 'partofspeech': 'J',
                                                 'root': 'või',
                                                 'root_tokens': ['või']}],
                                'base_span': (35, 38)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'i',
                                                 'form': 's',
                                                 'lemma': 'jääma',
                                                 'normalized_text': 'jäi',
                                                 'partofspeech': 'V',
                                                 'root': 'jää',
                                                 'root_tokens': ['jää']}],
                                'base_span': (39, 42)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'sse',
                                                 'form': 'sg ill',
                                                 'lemma': 'Poola',
                                                 'normalized_text': 'Poolasse',
                                                 'partofspeech': 'H',
                                                 'root': 'Poola',
                                                 'root_tokens': ['Poola']}],
                                'base_span': (43, 51)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '',
                                                 'form': '',
                                                 'lemma': '?',
                                                 'normalized_text': '?',
                                                 'partofspeech': 'Z',
                                                 'root': '?',
                                                 'root_tokens': ['?']}],
                                'base_span': (51, 52)}]},
                    {'ambiguous': False,
                     'attributes': ('nertag',),
                     'secondary_attributes': (),
                     'enveloping': None,
                     'meta': {},
                     'name': 'wordner',
                     'parent': 'words',
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'nertag': 'O'}], 'base_span': (0, 2)},
                               {'annotations': [{'nertag': 'O'}], 'base_span': (3, 9)},
                               {'annotations': [{'nertag': 'B-RIIK'}],
                                'base_span': (10, 18)},
                               {'annotations': [{'nertag': 'I-RIIK'}],
                                'base_span': (19, 34)},
                               {'annotations': [{'nertag': 'O'}],
                                'base_span': (35, 38)},
                               {'annotations': [{'nertag': 'O'}],
                                'base_span': (39, 42)},
                               {'annotations': [{'nertag': 'B-RIIK'}],
                                'base_span': (43, 51)},
                               {'annotations': [{'nertag': 'O'}],
                                'base_span': (51, 52)}]}],
         'meta': {},
         'text': 'Ta jõudis Ameerika Ühendriikidesse või jäi Poolasse?'}

    text = dict_to_text( input_text_with_ner_dict )
    result_conll_str = ner_labelling_to_conll( text, text['wordner'] )
    result_conll_str_fixed = result_conll_str.replace('\r\n', '\n') # a fix for Windows ( to avoid \r\n )

    expected_result_conll_ner_str = \
        'Ta\ttema+0\t_P_ sg n\tO\n'+\
        'jõudis\tjõud+is\t_V_ s\tO\n'+\
        'Ameerika\tAmeerika+0\t_H_ sg g\tB-RIIK\n'+\
        'Ühendriikidesse\tühend_riik+desse\t_S_ pl ill\tI-RIIK\n'+\
        'või\tvõi+0\t_J_\tO\n'+\
        'jäi\tjää+i\t_V_ s\tO\n'+\
        'Poolasse\tPoola+sse\t_H_ sg ill\tB-RIIK\n'+\
        '?\t?\t_Z_\tO\n\n\n'

    assert result_conll_str_fixed == expected_result_conll_ner_str
 