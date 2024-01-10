import unittest

from estnltk import Text
from estnltk_neural.taggers import CoreferenceTagger
from estnltk.converters import dict_to_layer, layer_to_dict
from estnltk.downloader import get_resource_paths

# Try to get the resources path for coreferencetagger. If missing, do nothing. It's up for the user to download the missing resources
COREF_V1_MODEL_PATH = get_resource_paths("coreference_v1", only_latest=True, download_missing=False)

skip_message_missing_models = \
  "CoreferenceTagger's resources have not been downloaded. Use estnltk.download('coreference_v1') to fetch the missing resources."

#
#  Note: since each initialization of CoreferenceTagger retrains the model, 
#  the outcome depends on specific versions of libraries used during in the 
#  training. 
#  Notable prediction differences appeared when xgboost version was changed 
#  from 1.7.4 to 2.0.0, mostly due to the change of the default tree method 
#  in xgboost. 
#  So, currently, we test for varying outcomes, although a more stable 
#  solution is desirable.
#

@unittest.skipIf(COREF_V1_MODEL_PATH is None,
                 reason=skip_message_missing_models)
def test_coreference_tagger_smoke():
    # Test that CoreferenceTagger runs OK with default options
    coref_tagger = CoreferenceTagger(resources_dir=COREF_V1_MODEL_PATH,
                                     xgb_tree_method='approx')
    text = Text('Mina ei tagane sammugi, põrutas kapten Silver Üksjalg meestele.')
    coref_tagger.tag(text)
    assert coref_tagger.output_layer in text.relation_layers
    coref_layer = text[coref_tagger.output_layer]
    assert coref_layer[0]['pronoun'].text == 'Mina'
    assert coref_layer[0]['mention'].text == 'Silver'
    expected_coref_layer_dict = \
        {'ambiguous': False,
         'attributes': ('chain_id',),
         'display_order': (),
         'enveloping': None,
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (39, 45), 'pronoun': (0, 4)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    #from pprint import pprint
    #pprint( layer_to_dict( coref_layer ) )
    assert layer_to_dict(coref_layer) == expected_coref_layer_dict


@unittest.skipIf(COREF_V1_MODEL_PATH is None,
                 reason=skip_message_missing_models)
def test_coreference_tagger_multisentence_text():
    # Test CoreferenceTagger on multisentence text
    coref_tagger = CoreferenceTagger(resources_dir=COREF_V1_MODEL_PATH,
                                     xgb_tree_method='approx')
    text = Text('Piilupart Donald, kes kunagi ei anna järele, läks uuele ringile. '+\
                'Ta kärkis ja paukus, kuni muusika vaikis ja pasadoobel seiskus. '+\
                'Mis sa tühja lällad, küsis rahvas.')
    coref_tagger.tag(text)
    assert coref_tagger.output_layer in text.relation_layers
    coref_layer = text[coref_tagger.output_layer]
    #from pprint import pprint
    #pprint( layer_to_dict(coref_layer) )
    # There are different outcomes, depending on the xgboost version:
    expected_coref_layer_dict_1 = \
        {'ambiguous': False,
         'attributes': ('chain_id',),
         'display_order': (),
         'enveloping': None,
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (65, 67)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (133, 135)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    expected_coref_layer_dict_2 = \
        {'ambiguous': False,
         'attributes': ('chain_id',),
         'display_order': (),
         'enveloping': None,
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (65, 67)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    assert layer_to_dict(coref_layer) == expected_coref_layer_dict_1 or \
           layer_to_dict(coref_layer) == expected_coref_layer_dict_2


@unittest.skipIf(COREF_V1_MODEL_PATH is None,
                 reason=skip_message_missing_models)
def test_coreference_tagger_with_named_entities_layer():
    # Test CoreferenceTagger works in combination with named entities layer
    text = Text('Piilupart Donald, kes kunagi ei anna järele, läks uuele ringile. '+\
                'Ta kärkis ja paukus, kuni muusika vaikis ja pasadoobel seiskus. '+\
                'Mis sa tühja lällad, küsis rahvas.')
    # Add words and ner layer
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 9)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (10, 16)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (16, 17)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (18, 21)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (22, 28)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (29, 31)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (32, 36)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (37, 43)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (43, 44)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (45, 49)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (50, 55)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (56, 63)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (63, 64)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (65, 67)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (68, 74)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (75, 77)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (78, 84)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (84, 85)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (86, 90)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (91, 98)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (99, 105)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (106, 108)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (109, 119)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (120, 127)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (127, 128)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (129, 132)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (133, 135)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (136, 141)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (142, 148)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (148, 149)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (150, 155)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (156, 162)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (162, 163)}]}
    text.add_layer( dict_to_layer(words_layer_dict) )
    ner_layer_dict = \
        {'ambiguous': False,
         'attributes': ('nertag',),
         'enveloping': 'words',
         'meta': {},
         'name': 'ner',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'nertag': 'PER'}],
                    'base_span': ((0, 9), (10, 16))}]}
    text.add_layer( dict_to_layer(ner_layer_dict) )
    coref_tagger = CoreferenceTagger(resources_dir=COREF_V1_MODEL_PATH, 
                                     ner_layer='ner')
    coref_tagger.tag(text)
    assert coref_tagger.output_layer in text.relation_layers
    coref_layer = text[coref_tagger.output_layer]
    # There are different outcomes, depending on the xgboost version:
    expected_coref_layer_dict_1 = \
        {'ambiguous': False,
         'attributes': ('chain_id',),
         'display_order': (),
         'enveloping': None,
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (0, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (0, 16), 'pronoun': (65, 67)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (0, 16), 'pronoun': (133, 135)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    expected_coref_layer_dict_2 = \
        {'ambiguous': False,
         'attributes': ('chain_id',),
         'display_order': (),
         'enveloping': None,
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (0, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{'chain_id': 0}],
                        'named_spans': {'mention': (0, 16), 'pronoun': (65, 67)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    assert layer_to_dict(coref_layer) == expected_coref_layer_dict_1 or \
           layer_to_dict(coref_layer) == expected_coref_layer_dict_2

