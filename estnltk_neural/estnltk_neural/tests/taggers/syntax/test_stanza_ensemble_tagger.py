import os
import unittest
from collections import OrderedDict

from estnltk import Text
from estnltk.converters import dict_to_layer, layer_to_dict
from estnltk_neural.taggers import StanzaSyntaxEnsembleTagger
from estnltk.downloader import get_resource_paths

# Try to get the resources path for stanzasyntaxensembletagger. If missing, do nothing. It's up for the user to download the missing resources
STANZA_SYNTAX_MODELS_PATH = get_resource_paths("stanzasyntaxensembletagger", only_latest=True, download_missing=False)

skip_message_missing_models = \
  "StanzaSyntaxEnsembleTagger's resources have not been downloaded. Use estnltk.download('stanzasyntaxensembletagger') to fetch the missing resources."


# Check if the ensemble models exist @ STANZA_SYNTAX_MODELS_PATH and can be tested
def ensemble_models_exist():
    if STANZA_SYNTAX_MODELS_PATH is None or not os.path.isdir(STANZA_SYNTAX_MODELS_PATH):
        return False
    ensemble_path = os.path.join(STANZA_SYNTAX_MODELS_PATH, 'et', 'depparse', 'ensemble_models')
    if not os.path.isdir(ensemble_path):
        return False
    models_count = 0
    for model in os.listdir(ensemble_path):
        models_count += 1 if model.endswith('.pt') else 0
    return models_count > 0
    
 
@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None, skip_message_missing_models)
@unittest.skipIf( not ensemble_models_exist(), skip_message_missing_models )
def test_stanza_syntax_ensemble_tagger():
    # Smoke test StanzaSyntaxEnsembleTagger
    text = Text('Väike jänes jooksis metsa! Mina ei jookse kuhugi.')

    text.tag_layer('morph_extended')
    stanza_ensemble_tagger = StanzaSyntaxEnsembleTagger(output_layer='stanza_ensemble_syntax')
    stanza_ensemble_tagger.tag(text)

    assert 'stanza_ensemble_syntax' in text.layers
    expected_output_layer_dict = \
        {'ambiguous': False,
         'attributes': ('id',
                        'lemma',
                        'upostag',
                        'xpostag',
                        'feats',
                        'head',
                        'deprel',
                        'deps',
                        'misc'),
         'enveloping': None,
         'meta': {},
         'name': 'stanza_ensemble_syntax',
         'parent': 'morph_extended',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': OrderedDict([('pos', 'pos'),
                                                           ('sg', 'sg'),
                                                           ('nom', 'nom')]),
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'väike',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (0, 5)},
                   {'annotations': [{'deprel': 'nsubj',
                                     'deps': '_',
                                     'feats': OrderedDict([('com', 'com'),
                                                           ('sg', 'sg'),
                                                           ('nom', 'nom')]),
                                     'head': 3,
                                     'id': 2,
                                     'lemma': 'jänes',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (6, 11)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': OrderedDict([('main', 'main'),
                                                           ('indic', 'indic'),
                                                           ('impf', 'impf'),
                                                           ('ps3', 'ps3'),
                                                           ('sg', 'sg'),
                                                           ('ps', 'ps'),
                                                           ('af', 'af')]),
                                     'head': 0,
                                     'id': 3,
                                     'lemma': 'jooksma',
                                     'misc': '_',
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (12, 19)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': '_',
                                     'feats': OrderedDict([('com', 'com'),
                                                           ('sg', 'sg'),
                                                           ('adit', 'adit')]),
                                     'head': 3,
                                     'id': 4,
                                     'lemma': 'mets',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (20, 25)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': OrderedDict(),
                                     'head': 3,
                                     'id': 5,
                                     'lemma': '!',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (25, 26)},
                   {'annotations': [{'deprel': 'nsubj',
                                     'deps': '_',
                                     'feats': OrderedDict([('sg', 'sg'),
                                                           ('nom', 'nom')]),
                                     'head': 3,
                                     'id': 1,
                                     'lemma': 'mina',
                                     'misc': '_',
                                     'upostag': 'P',
                                     'xpostag': 'P'}],
                    'base_span': (27, 31)},
                   {'annotations': [{'deprel': 'aux',
                                     'deps': '_',
                                     'feats': OrderedDict([('aux', 'aux'),
                                                           ('neg', 'neg')]),
                                     'head': 3,
                                     'id': 2,
                                     'lemma': 'ei',
                                     'misc': '_',
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (32, 34)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': OrderedDict([('mod', 'mod'),
                                                           ('imper', 'imper'),
                                                           ('pres', 'pres'),
                                                           ('ps2', 'ps2'),
                                                           ('sg', 'sg'),
                                                           ('ps', 'ps'),
                                                           ('af', 'af')]),
                                     'head': 0,
                                     'id': 3,
                                     'lemma': 'jooksma',
                                     'misc': '_',
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (35, 41)},
                   {'annotations': [{'deprel': 'advmod',
                                     'deps': '_',
                                     'feats': OrderedDict(),
                                     'head': 3,
                                     'id': 4,
                                     'lemma': 'kuhugi',
                                     'misc': '_',
                                     'upostag': 'D',
                                     'xpostag': 'D'}],
                    'base_span': (42, 48)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': OrderedDict(),
                                     'head': 3,
                                     'id': 5,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (48, 49)}]}
    #                
    #from pprint import pprint
    #print( layer_to_dict(text['stanza_ensemble_syntax']) )
    #
    assert expected_output_layer_dict == layer_to_dict(text['stanza_ensemble_syntax'])



