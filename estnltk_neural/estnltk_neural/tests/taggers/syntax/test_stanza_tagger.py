import os, os.path
from importlib.util import find_spec
from collections import OrderedDict

import unittest

from estnltk import Text
from estnltk.converters import dict_to_layer, layer_to_dict
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from estnltk.downloader import get_resource_paths

# Try to get the resources path for stanzasyntaxtagger. If missing, do nothing. It's up for the user to download the missing resources
STANZA_SYNTAX_MODELS_PATH = get_resource_paths("stanzasyntaxtagger", only_latest=True, download_missing=False)

skip_message_missing_models = \
  "StanzaSyntaxTagger's resources have not been downloaded. Use estnltk.download('stanzasyntaxtagger') to fetch the missing resources."

# Get stanza model's version (the release date of the models)
STANZA_SYNTAX_MODELS_VER = STANZA_SYNTAX_MODELS_PATH.rstrip(r'\//')[-10:] if isinstance(STANZA_SYNTAX_MODELS_PATH, str) else ''

# Base: expected output_layer with "stanza_syntax_2023-01-21" models
stanza_dict_sentences = {
    'name': 'stanza_syntax',
    'meta': {},
    'parent': 'words',
    'serialisation_module': None,
    'attributes': ('id',
                   'lemma',
                   'upostag',
                   'xpostag',
                   'feats',
                   'head',
                   'deprel',
                   'deps',
                   'misc'),
    'secondary_attributes': (),
    'enveloping': None,
    'ambiguous': False,
    'spans': [{'base_span': (0, 5),
               'annotations': [{'id': 1,
                                'lemma': 'väike',
                                'upostag': 'ADJ',
                                'xpostag': 'A',
                                'feats': OrderedDict([('Case', 'Nom'),
                                                      ('Degree', 'Pos'),
                                                      ('Number', 'Sing')]),
                                'head': 2,
                                'deprel': 'amod',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (6, 11),
               'annotations': [{'id': 2,
                                'lemma': 'jänes',
                                'upostag': 'NOUN',
                                'xpostag': 'S',
                                'feats': OrderedDict([('Case', 'Nom'),
                                                      ('Number', 'Sing')]),
                                'head': 3,
                                'deprel': 'nsubj',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (12, 19),
               'annotations': [{'id': 3,
                                'lemma': 'jooksma',
                                'upostag': 'VERB',
                                'xpostag': 'V',
                                'feats': OrderedDict([('Mood', 'Ind'),
                                                      ('Number', 'Sing'),
                                                      ('Person', '3'),
                                                      ('Tense', 'Past'),
                                                      ('VerbForm', 'Fin'),
                                                      ('Voice', 'Act')]),
                                'head': 0,
                                'deprel': 'root',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (20, 25),
               'annotations': [{'id': 4,
                                'lemma': 'mets',
                                'upostag': 'NOUN',
                                'xpostag': 'S',
                                'feats': OrderedDict([('Case', 'Add'),
                                                      ('Number', 'Sing')]),
                                'head': 3,
                                'deprel': 'obl',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (25, 26),
               'annotations': [{'id': 5,
                                'lemma': '!',
                                'upostag': 'PUNCT',
                                'xpostag': 'Z',
                                'feats': OrderedDict(),
                                'head': 3,
                                'deprel': 'punct',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (27, 31),
               'annotations': [{'id': 1,
                                'lemma': 'mina',
                                'upostag': 'PRON',
                                'xpostag': 'P',
                                'feats': OrderedDict([('Case', 'Nom'),
                                                      ('Number', 'Sing'),
                                                      ('Person', '1'),
                                                      ('PronType', 'Prs')]),
                                'head': 3,
                                'deprel': 'nsubj',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (32, 34),
               'annotations': [{'id': 2,
                                'lemma': 'ei',
                                'upostag': 'AUX',
                                'xpostag': 'V',
                                'feats': OrderedDict([('Polarity', 'Neg')]),
                                'head': 3,
                                'deprel': 'aux',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (35, 41),
               'annotations': [{'id': 3,
                                'lemma': 'jooksma',
                                'upostag': 'VERB',
                                'xpostag': 'V',
                                'feats': OrderedDict([('Connegative', 'Yes'),
                                                      ('Mood', 'Ind'),
                                                      ('Tense', 'Pres'),
                                                      ('VerbForm', 'Fin'),
                                                      ('Voice', 'Act')]),
                                'head': 0,
                                'deprel': 'root',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (41, 42),
               'annotations': [{'id': 4,
                                'lemma': '.',
                                'upostag': 'PUNCT',
                                'xpostag': 'Z',
                                'feats': OrderedDict(),
                                'head': 3,
                                'deprel': 'punct',
                                'deps': '_',
                                'misc': '_'}]}]}

# Base: expected output_layer with "stanza_syntax_2023-01-21" models
stanza_dict_morph_analysis = {
    'name': 'stanza_ma',
    'meta': {},
    'parent': 'morph_analysis',
    'serialisation_module': None,
    'attributes': ('id',
                   'lemma',
                   'upostag',
                   'xpostag',
                   'feats',
                   'head',
                   'deprel',
                   'deps',
                   'misc'),
    'secondary_attributes': (),
    'enveloping': None,
    'ambiguous': False,
    'spans': [{'base_span': (0, 5),
               'annotations': [{'id': 1,
                                'lemma': 'väike',
                                'upostag': 'A',
                                'xpostag': 'A',
                                'feats': OrderedDict([('sg', 'sg'),
                                                      ('n', 'n')]),
                                'head': 2,
                                'deprel': 'amod',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (6, 11),
               'annotations': [{'id': 2,
                                'lemma': 'jänes',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats': OrderedDict([('sg', 'sg'),
                                                      ('n', 'n')]),
                                'head': 3,
                                'deprel': 'nsubj',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (12, 19),
               'annotations': [{'id': 3,
                                'lemma': 'jooksma',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats': OrderedDict([('s', 's')]),
                                'head': 0,
                                'deprel': 'root',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (20, 25),
               'annotations': [{'id': 4,
                                'lemma': 'mets',
                                'upostag': 'S',
                                'xpostag': 'S',
                                'feats': OrderedDict([('adt', 'adt')]),
                                'head': 3,
                                'deprel': 'obl',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (25, 26),
               'annotations': [{'id': 5,
                                'lemma': '!',
                                'upostag': 'Z',
                                'xpostag': 'Z',
                                'feats': OrderedDict(),
                                'head': 3,
                                'deprel': 'punct',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (27, 31),
               'annotations': [{'id': 1,
                                'lemma': 'mina',
                                'upostag': 'P',
                                'xpostag': 'P',
                                'feats': OrderedDict([('sg', 'sg'),
                                                      ('n', 'n')]),
                                'head': 3,
                                'deprel': 'nsubj',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (32, 34),
               'annotations': [{'id': 2,
                                'lemma': 'ei',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats': OrderedDict([('neg', 'neg')]),
                                'head': 3,
                                'deprel': 'aux',
                                'deps': '_',
                                'misc': '_'}]},
              {'base_span': (35, 41),
               'annotations': [{'id': 3,
                                'lemma': 'jooksma',
                                'upostag': 'V',
                                'xpostag': 'V',
                                'feats': OrderedDict([('o', 'o')]),
                                'head': 0,
                                'deprel': 'root',
                                'deps': '_',
                                'misc': '_'}]},

              {'base_span': (41, 42),
               'annotations': [{'id': 4,
                                'lemma': '.',
                                'upostag': 'Z',
                                'xpostag': 'Z',
                                'feats': OrderedDict(),
                                'head': 3,
                                'deprel': 'punct',
                                'deps': '_',
                                'misc': '_'}]}]}


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_syntax_tagger_smoke():
    # Test that StanzaSyntaxTagger runs OK with default options
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')
    text.tag_layer('morph_analysis')
    stanza_tagger = StanzaSyntaxTagger(random_pick_seed=4)  # default: input_morph_layer='morph_analysis'
    stanza_tagger.tag(text)
    assert stanza_tagger.output_layer in text.layers
    assert len(text[stanza_tagger.output_layer]) == len(text['morph_analysis'])


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_syntax_tagger_sentences():
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')
    text.tag_layer('sentences')
    # Apply stanza's original et pipeline (on tokenized unambigous input)
    stanza_tagger = StanzaSyntaxTagger(input_type='sentences',
                                       random_pick_seed=4,
                                       resources_path=STANZA_SYNTAX_MODELS_PATH,
                                       depparse_path=os.path.join(STANZA_SYNTAX_MODELS_PATH,
                                                                  'et', 'depparse', 'stanza_depparse.pt'))
    stanza_tagger.tag(text)
    # Note: when stanza updates the et pipeline, there can 
    # be disparencies from the original stanza's output. 
    # Therefore, use fine-grained comparsion and account for 
    # expected differences
    new_stanza_syntax_sentences = layer_to_dict(text.stanza_syntax)
    # Check attributes
    for attr in stanza_dict_sentences.keys():
        if attr != 'spans':
            assert stanza_dict_sentences[attr] == new_stanza_syntax_sentences[attr], \
                f'(!) Mismatching {attr!r} values: {stanza_dict_sentences[attr]!r} != '+\
                f'{new_stanza_syntax_sentences[attr]!r}.'
    # Check spans
    assert len(stanza_dict_sentences['spans']) == len(new_stanza_syntax_sentences['spans'])
    for span_a, span_b in zip(stanza_dict_sentences['spans'], new_stanza_syntax_sentences['spans']):
        assert span_a['base_span'] == span_b['base_span']
        if span_a['annotations'] != span_b['annotations']:
            # Known difference (as of stanza's version 1.5.1)
            if span_a['base_span'] == (6, 11) and \
               span_a['annotations'][0]['lemma'] == 'jänes' and \
               span_b['annotations'][0]['lemma'] == 'jäni':
                # Assert that other most important features match
                assert span_a['annotations'][0]['id'] == span_b['annotations'][0]['id']
                assert span_a['annotations'][0]['head'] == span_b['annotations'][0]['head']
                assert span_a['annotations'][0]['deprel'] == span_b['annotations'][0]['deprel']
                # Skip this difference (known error, from stanza's version 1.5.1)
                continue
        assert span_a['annotations'] == span_b['annotations']


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_syntax_tagger_sentences_bugfix():
    # Test bug related to missing 'xpos' in stanza partofspeech tagger's output
    text = Text("Umbes 262 000 4chani-kasutajat.")
    # Add words layer with '262' and '000' tokenized separately
    text.add_layer( \
        dict_to_layer( {'ambiguous': True,
                        'attributes': ('normalized_form',),
                        'enveloping': None,
                        'meta': {},
                        'name': 'words',
                        'parent': None,
                        'secondary_attributes': (),
                        'serialisation_module': None,
                        'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 5)},
                                  {'annotations': [{'normalized_form': None}], 'base_span': (6, 9)},
                                  {'annotations': [{'normalized_form': None}], 'base_span': (10, 13)},
                                  {'annotations': [{'normalized_form': None}], 'base_span': (14, 30)},
                                  {'annotations': [{'normalized_form': None}], 'base_span': (30, 31)}]} ) )
    text.tag_layer('sentences')
    # Apply stanza's original et pipeline (on tokenized unambigous input)
    stanza_tagger = StanzaSyntaxTagger(input_type='sentences',
                                       random_pick_seed=4,
                                       resources_path=STANZA_SYNTAX_MODELS_PATH,
                                       depparse_path=os.path.join(STANZA_SYNTAX_MODELS_PATH,
                                                                  'et', 'depparse', 'stanza_depparse.pt'))
    stanza_tagger.tag(text)
    annotations = [(w.text, w.annotations[0]) for w in text[stanza_tagger.output_layer]]
    pos_annotations = [(w, ann['upostag'], ann['xpostag']) for (w, ann) in annotations]
    # Assert that missing 'xpos' will be indicated by '_'
    assert pos_annotations == \
            [('Umbes', 'ADV', 'D'), 
             ('262', 'NUM', 'N'), 
             ('000', 'X', '_'), 
             ('4chani-kasutajat', 'NOUN', 'S'), 
             ('.', 'PUNCT', 'Z')]


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_syntax_tagger_analysis():
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')

    text.tag_layer(['sentences', 'morph_analysis'])
    stanza_tagger_ma = StanzaSyntaxTagger(output_layer='stanza_ma', input_type='morph_analysis',
                                          random_pick_seed=4,
                                          resources_path=STANZA_SYNTAX_MODELS_PATH)
    stanza_tagger_ma.tag(text)

    if STANZA_SYNTAX_MODELS_VER == '2026-08-18':
        # Make corrections according to the new model
        stanza_dict_morph_analysis['spans'][3]['annotations'][0]['deprel'] = 'obl:lmod'
    # stanza pipeline (on tokenized unambigous input)
    assert stanza_dict_morph_analysis == layer_to_dict(text.stanza_ma), text.stanza_ma.diff(
        dict_to_layer(stanza_dict_morph_analysis))


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_ambiguous():
    """Testing seed on ambigous analysis"""
    text = Text('Vaata kaotatud ja leitud asjade nurgast')

    text.tag_layer('morph_extended')
    stanza_tagger_me = StanzaSyntaxTagger(input_type='morph_extended',
                                          input_morph_layer='morph_extended',
                                          output_layer='stanza_me',
                                          random_pick_seed=4,
                                          resources_path=STANZA_SYNTAX_MODELS_PATH,
                                          depparse_path=os.path.join(STANZA_SYNTAX_MODELS_PATH, 'et', 'depparse',
                                                                     'morph_extended.pt'))

    ambiguous_spans = [i for i, span in enumerate(text.morph_extended) if len(span.annotations) > 1]

    assert ambiguous_spans is not None and len(ambiguous_spans) > 0

    ambiguous_upostags_forms = [[] for _ in range(len(ambiguous_spans))]

    # 1) Tag multiple times to check ambiguous pos-tags and feats
    # At each run, we should get a different result
    for i in range(10):
        stanza_tagger_me.tag(text)
        for idx, ambiguous_i in enumerate(ambiguous_spans):
            # concatenate postag and feats into one string
            concat_feats = '{}_{}'.format( \
                    text.stanza_me[ambiguous_i].upostag[0], \
                    '|'.join(list(text.stanza_me[ambiguous_i].feats.keys())) )
            ambiguous_upostags_forms[idx].append( concat_feats )
        text.pop_layer('stanza_me')
    
    # For all ambiguous words, we should see different random picks over the runs
    assert all([True if len(set(ambiguous)) > 1 else False for ambiguous in ambiguous_upostags_forms])

    # 2) However, we can set the seed of random generator before tagging each document
    # As a result, we get the same result at each run
    ambiguous_upostags = [[] for _ in range(len(ambiguous_spans))]

    # Tag multiple times to check ambiguous pos-tags and feats
    # At each run, we should get same result
    for i in range(10):
        stanza_tagger_me._random.seed(4)  # Set the seed before tagging
        stanza_tagger_me.tag(text)
        for idx, ambiguous_i in enumerate(ambiguous_spans):
            ambiguous_upostags[idx].append( text.stanza_me[ambiguous_i].upostag[0] )
        text.pop_layer('stanza_me')
    
    assert not any([True if len(set(ambiguous)) > 1 else False for ambiguous in ambiguous_upostags])


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
def test_stanza_syntax_tagger_on_detached_layers():
    # Test that StanzaSyntaxTagger works on detached_layers
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')
    text.tag_layer(['sentences', 'morph_analysis'])
    # detach layers from Text obj
    detached_layers = {}
    for layer in ['morph_analysis', 'sentences', 'words', 'compound_tokens', 'tokens']:
        detached_layers[layer] = text.pop_layer(layer)
    assert len(text.layers) == 0
    stanza_tagger_ma = StanzaSyntaxTagger(output_layer='stanza_ma', input_type='morph_analysis',
                                          random_pick_seed=4,
                                          resources_path=STANZA_SYNTAX_MODELS_PATH)
    # Tag with detached layers
    stanza_ma_layer = stanza_tagger_ma.make_layer(text, detached_layers)
    if STANZA_SYNTAX_MODELS_VER == '2026-08-18':
        # Make corrections according to the new model
        stanza_dict_morph_analysis['spans'][3]['annotations'][0]['deprel'] = 'obl:lmod'
    # stanza pipeline (on tokenized unambigous input)
    assert stanza_dict_morph_analysis == layer_to_dict(stanza_ma_layer), stanza_ma_layer.diff(
        dict_to_layer(stanza_dict_morph_analysis))



def check_if_transformers_is_available():
    return find_spec("transformers") is not None

def check_if_pytorch_is_available():
    return find_spec("torch") is not None

# Try to get the resources path for BertMorphTagger's model v2. If missing, do nothing. It's up for the user to download the missing resources
BERTMORPH_V2_PATH = get_resource_paths("bert_morph_v2", only_latest=True, download_missing=False)

@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason=skip_message_missing_models)
@unittest.skipIf(not check_if_transformers_is_available(),
                 reason="package tranformers is required for this test")
@unittest.skipIf(not check_if_pytorch_is_available(),
                 reason="package pytorch is required for this test")
@unittest.skipIf(BERTMORPH_V2_PATH is None,
                 reason="BertMorphTagger's model v2 location not known. "+\
                        "Use estnltk.download('bert_morph_v2') to get the missing resources.")
@unittest.skipIf(len(STANZA_SYNTAX_MODELS_VER) == 0 or not STANZA_SYNTAX_MODELS_VER >= '2026-08-18',
                 reason="StanzaSyntaxTagger's model version >= 2026-08-18 is required for this test.")
def test_stanza_syntax_tagger_on_morph_with_bert():
    # Test that StanzaSyntaxTagger's model that has been 
    # trained on VabamorfWithBertTagger's output layer
    from estnltk_neural.taggers import VabamorfWithBertTagger
    text = Text('Muna otsis kana, kass tahtis osa.')
    vm_bert_morph_tagger = VabamorfWithBertTagger()
    text.tag_layer( vm_bert_morph_tagger.input_layers )
    assert vm_bert_morph_tagger.output_layer not in text.layers
    vm_bert_morph_tagger.tag( text )
    assert vm_bert_morph_tagger.output_layer in text.layers
    # Construct model path
    model_path = os.path.join(STANZA_SYNTAX_MODELS_PATH, 'et', 'depparse', 'morph_with_bert.pt')
    assert os.path.exists( model_path ), \
        f'(!) Missing morph_with_bert stanza model ({model_path!r}).'
    stanza_tagger_morph_with_bert = \
        StanzaSyntaxTagger(output_layer='stanza_bert_morph', 
                           input_morph_layer=vm_bert_morph_tagger.output_layer, 
                           input_type='morph_analysis', 
                           depparse_path=model_path, 
                           random_pick_seed=4)
    stanza_tagger_morph_with_bert.tag( text )
    assert stanza_tagger_morph_with_bert.output_layer in text.layers
    assert len(text[stanza_tagger_morph_with_bert.output_layer]) == \
           len(text[vm_bert_morph_tagger.output_layer])
    #from pprint import pprint
    #pprint( layer_to_dict(text[stanza_tagger_morph_with_bert.output_layer]) )
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
         'name': 'stanza_bert_morph',
         'parent': 'morph_analysis',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'nsubj',
                                     'deps': '_',
                                     'feats': OrderedDict({'sg': 'sg', 'n': 'n'}),
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'muna',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (0, 4)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': OrderedDict({'s': 's'}),
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'otsima',
                                     'misc': '_',
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (5, 10)},
                   {'annotations': [{'deprel': 'obj',
                                     'deps': '_',
                                     'feats': OrderedDict({'sg': 'sg', 'p': 'p'}),
                                     'head': 2,
                                     'id': 3,
                                     'lemma': 'kana',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (11, 15)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': OrderedDict(),
                                     'head': 6,
                                     'id': 4,
                                     'lemma': ',',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (15, 16)},
                   {'annotations': [{'deprel': 'nsubj',
                                     'deps': '_',
                                     'feats': OrderedDict({'sg': 'sg', 'n': 'n'}),
                                     'head': 6,
                                     'id': 5,
                                     'lemma': 'kass',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (17, 21)},
                   {'annotations': [{'deprel': 'conj',
                                     'deps': '_',
                                     'feats': OrderedDict({'s': 's'}),
                                     'head': 2,
                                     'id': 6,
                                     'lemma': 'tahtma',
                                     'misc': '_',
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (22, 28)},
                   {'annotations': [{'deprel': 'obj',
                                     'deps': '_',
                                     'feats': OrderedDict({'sg': 'sg', 'p': 'p'}),
                                     'head': 6,
                                     'id': 7,
                                     'lemma': 'osa',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (29, 32)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': OrderedDict(),
                                     'head': 2,
                                     'id': 8,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (32, 33)}]}
    assert layer_to_dict(text[stanza_tagger_morph_with_bert.output_layer]) == expected_output_layer_dict