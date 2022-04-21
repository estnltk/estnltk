import os
from collections import OrderedDict

import pytest
from estnltk import Text
from estnltk.converters import dict_to_layer
from estnltk.taggers import ConllMorphTagger
from estnltk.taggers.standard.syntax.udpipe_tagger.udpipe_tagger import check_if_udpipe_is_in_path
from estnltk.taggers.standard.syntax.vislcg3_syntax import check_if_vislcg_is_in_path
from estnltk.downloader import get_resource_paths

# Try to get the resources for udpipetagger. If missing, do nothing. It's up for the user to download the missing resources
UDPIPE_SYNTAX_MODELS_PATH = get_resource_paths("udpipetagger", only_latest=True, download_missing=False)


udpipe_dict = {
    'name': 'udpipe_syntax',
    'text': 'Nuriseti , et hääbuvale kultuurile rõhumine mõjus pigem masendavalt ega omanud seost etnofuturismiga .',
    'meta': {},
    'parent': 'conll_morph',

    'attributes': ('id',
                   'form',
                   'lemma',
                   'upostag',
                   'xpostag',
                   'feats',
                   'head',
                   'deprel',
                   'deps',
                   'misc'),

    'enveloping': None,
    'ambiguous': True,
    'spans': [{'base_span': (0, 8),
               'annotations': [{'id': 1,
                                'form': 'Nuriseti',
                                'lemma': 'nurise',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats': OrderedDict([('indic', ''), ('impf', ''), ('imps', '')]),
                                'head': 0,
                                'deprel': 'root',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (9, 10),
               'annotations': [{'id': 2,
                                'form': ',',
                                'lemma': ',',
                                'upostag': 'Z',
                                'xpostag': 'Z',
                                'feats': OrderedDict([('Com', '')]),
                                'head': 1,
                                'deprel': '@Punc',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (11, 13),
               'annotations': [{'id': 3,
                                'form': 'et',
                                'lemma': 'et',
                                'upostag': 'J',
                                'xpostag': 'Js',
                                'feats': OrderedDict([]),
                                'head': 7,
                                'deprel': '@J',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (14, 23),
               'annotations': [{'id': 4,
                                'form': 'hääbuvale',
                                'lemma': 'hääbuv',
                                'upostag': 'A',
                                'xpostag': 'A',
                                'feats': OrderedDict([('sg', ''), ('all', '')]),
                                'head': 5,
                                'deprel': '@AN>',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (24, 34),
               'annotations': [{'id': 5,
                                'form': 'kultuurile',
                                'lemma': 'kultuur',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats':  OrderedDict([('sg', ''), ('all', '')]),
                                'head': 6,
                                'deprel': '@NN>',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (35, 43),
               'annotations': [{'id': 6,
                                'form': 'rõhumine',
                                'lemma': 'rõhu=mine',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats': OrderedDict([('sg', ''), ('nom', '')]),
                                'head': 7,
                                'deprel': '@SUBJ',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (44, 49),
               'annotations': [{'id': 7,
                                'form': 'mõjus',
                                'lemma': 'mõju',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats':  OrderedDict([('indic', ''), ('impf', ''), ('ps3', ''), ('sg', '')]),
                                'head': 1,
                                'deprel': '@FMV',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (50, 55),
               'annotations': [{'id': 8,
                                'form': 'pigem',
                                'lemma': 'pigem',
                                'upostag': 'D',
                                'xpostag': 'D',
                                'feats': OrderedDict([]),
                                'head': 9,
                                'deprel': '@ADVL',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (56, 67),
               'annotations': [{'id': 9,
                                'form': 'masendavalt',
                                'lemma': 'masendavalt',
                                'upostag': 'D',
                                'xpostag': 'D',
                                'feats':  OrderedDict([]),
                                'head': 7,
                                'deprel': '@ADVL',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (68, 71),
               'annotations': [{'id': 10,
                                'form': 'ega',
                                'lemma': 'ega',
                                'upostag': 'J',
                                'xpostag': 'Jc',
                                'feats': OrderedDict([]),
                                'head': 11,
                                'deprel': '@J',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (72, 78),
               'annotations': [{'id': 11,
                                'form': 'omanud',
                                'lemma': 'oma',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats': OrderedDict([('indic', ''), ('impf', ''), ('neg', '')]),
                                'head': 1,
                                'deprel': '@FMV',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (79, 84),
               'annotations': [{'id': 12,
                                'form': 'seost',
                                'lemma': 'seos',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats': OrderedDict([('sg', ''), ('part', '')]),
                                'head': 11,
                                'deprel': '@OBJ',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (85, 100),
               'annotations': [{'id': 13,
                                'form': 'etnofuturismiga',
                                'lemma': 'etno_futurism',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats': OrderedDict([('sg', ''), ('kom', '')]),
                                'head': 11,
                                'deprel': '@ADVL',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (101, 102),
               'annotations': [{'id': 14,
                                'form': '.',
                                'lemma': '.',
                                'upostag': 'Z',
                                'xpostag': 'Z',
                                'feats': OrderedDict([('Fst', '')]),
                                'head': 13,
                                'deprel': '@Punc',
                                'deps': '_',
                                'misc': '_'}]},
              ]}

@pytest.mark.skipif(not check_if_udpipe_is_in_path('udpipe'),
                    reason="a directory containing udpipe executable must be inside the system PATH")
@pytest.mark.skipif(UDPIPE_SYNTAX_MODELS_PATH is None,
                    reason="UDPipeTagger's resources have not been downloaded. Use estnltk.download('udpipetagger') to fetch the missing resources.")
@pytest.mark.skipif(not check_if_vislcg_is_in_path('vislcg3'),
                    reason="a directory containing vislcg3 executable must be inside the system PATH")
def test_udpipe_tagger():
    from estnltk.taggers.standard.syntax.udpipe_tagger.udpipe_tagger import UDPipeTagger
    text = Text(
        'Nuriseti , et hääbuvale kultuurile rõhumine mõjus pigem masendavalt ega omanud seost etnofuturismiga .')
    text.tag_layer('morph_extended')
    conll = ConllMorphTagger() # requires vislcg3
    conll.tag(text)
    tagger = UDPipeTagger()
    tagger.tag(text)
    assert dict_to_layer(udpipe_dict) == text.udpipe_syntax, text.udpipe_syntax.diff(dict_to_layer(udpipe_dict))


@pytest.mark.skipif(not check_if_udpipe_is_in_path('udpipe'),
                    reason="a directory containing udpipe executable must be inside the system PATH")
@pytest.mark.skipif(UDPIPE_SYNTAX_MODELS_PATH is None,
                    reason="UDPipeTagger's resources have not been downloaded. Use estnltk.download('udpipetagger') to fetch the missing resources.")
@pytest.mark.skipif(not check_if_vislcg_is_in_path('vislcg3'),
                    reason="a directory containing vislcg3 executable must be inside the system PATH")
def test_udpipe_tagger_all_configurations():
    from estnltk.taggers.standard.syntax.udpipe_tagger.udpipe_tagger import UDPipeTagger
    # Smoke test that all models/configurations of UDPipeTagger work
    for conf in [{'version':'conllx', 'input_type':'visl_morph'}, # this is default! 
                 {'version':'conllx', 'input_type':'morph_analysis'}, 
                 {'version':'conllx', 'input_type':'morph_extended'}, 
                 {'version':'conllu', 'input_type':'visl_morph'},
                 {'version':'conllu', 'input_type':'morph_analysis'},
                 {'version':'conllu', 'input_type':'morph_extended'}]:
        text=Text('See on üks väga ilus lause!')
        if conf['input_type'] == 'visl_morph':
            text.tag_layer('morph_extended')
            conll_morph = ConllMorphTagger(output_layer='conll_morph')
            conll_morph.tag(text)
            udpipe_tagger = UDPipeTagger(**conf)
            udpipe_tagger.tag(text)
            assert 'udpipe_syntax' in text.layers
            assert len(text['udpipe_syntax']) == len(text['words'])
        elif conf['input_type'] == 'morph_extended':
            text.tag_layer('morph_extended')
            conll_morph = ConllMorphTagger(output_layer='conll_morph', morph_extended_layer='morph_extended', no_visl=True)
            conll_morph.tag(text)
            udpipe_tagger = UDPipeTagger(**conf)
            udpipe_tagger.tag(text)
            assert 'udpipe_syntax' in text.layers
            assert len(text['udpipe_syntax']) == len(text['words'])
        elif conf['input_type'] == 'morph_analysis':
            text.tag_layer('morph_analysis')
            conll_morph = ConllMorphTagger(output_layer='conll_morph', morph_extended_layer='morph_analysis', no_visl=True)
            conll_morph.tag(text)
            udpipe_tagger = UDPipeTagger(**conf)
            udpipe_tagger.tag(text)
            assert 'udpipe_syntax' in text.layers
            assert len(text['udpipe_syntax']) == len(text['words'])
        