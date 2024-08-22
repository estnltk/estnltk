import pytest

from estnltk import Text
from estnltk.taggers import CompoundWordTagger

from estnltk.converters import layer_to_dict, dict_to_layer


def test_compound_word_tagger_smoke():
    # Initialize segmenter's context
    cw_tagger = CompoundWordTagger()
    
    text = Text('Kaubahoovi edelanurgas, rehepeksumasina tagaluugi kõrval. Seal on kosmoselaev. VÄLK-JA-PAUK!')
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text', 'subwords'),
         'enveloping': None,
         'meta': {},
         'name': 'compound_words',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_text': 'Kaubahoovi',
                                     'subwords': ['Kauba', 'hoovi']}],
                    'base_span': (0, 10)},
                   {'annotations': [{'normalized_text': 'edelanurgas',
                                     'subwords': ['edela', 'nurgas']}],
                    'base_span': (11, 22)},
                   {'annotations': [{'normalized_text': ',', 'subwords': [',']}],
                    'base_span': (22, 23)},
                   {'annotations': [{'normalized_text': 'rehepeksumasina',
                                     'subwords': ['rehe', 'peksu', 'masina']}],
                    'base_span': (24, 39)},
                   {'annotations': [{'normalized_text': 'tagaluugi',
                                     'subwords': ['taga', 'luugi']}],
                    'base_span': (40, 49)},
                   {'annotations': [{'normalized_text': 'kõrval',
                                     'subwords': ['kõrval']}],
                    'base_span': (50, 56)},
                   {'annotations': [{'normalized_text': '.', 'subwords': ['.']}],
                    'base_span': (56, 57)},
                   {'annotations': [{'normalized_text': 'Seal', 'subwords': ['Seal']}],
                    'base_span': (58, 62)},
                   {'annotations': [{'normalized_text': 'on', 'subwords': ['on']}],
                    'base_span': (63, 65)},
                   {'annotations': [{'normalized_text': 'kosmoselaev',
                                     'subwords': ['kosmose', 'laev']}],
                    'base_span': (66, 77)},
                   {'annotations': [{'normalized_text': '.', 'subwords': ['.']}],
                    'base_span': (77, 78)},
                   {'annotations': [{'normalized_text': 'VÄLK-JA-PAUK',
                                     'subwords': ['VÄLK', 'JA', 'PAUK']}],
                    'base_span': (79, 91)},
                   {'annotations': [{'normalized_text': '!', 'subwords': ['!']}],
                    'base_span': (91, 92)}]}
    #from pprint import pprint
    #pprint( layer_to_dict( text[cw_tagger.output_layer] ) )
    assert layer_to_dict( text[cw_tagger.output_layer] ) == expected_layer_dict


