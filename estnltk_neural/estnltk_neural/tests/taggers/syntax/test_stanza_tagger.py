import os
import unittest
from collections import OrderedDict

from estnltk import Text
from estnltk.converters import dict_to_layer, layer_to_dict
from estnltk.common import PACKAGE_PATH
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger


RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', '', 'stanza_tagger', 'stanza_resources')

# Variable must follow the structure of stanza_resources as in here:
STANZA_SYNTAX_MODELS_PATH = os.environ.get('STANZA_SYNTAX_MODELS_PATH')

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
                   "Environment variable STANZA_SYNTAX_MODELS_PATH is not defined. .")
def test_stanza_syntax_tagger_sentences():
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')

    text.tag_layer('sentences')
    stanza_tagger = StanzaSyntaxTagger(input_type='sentences',
                                       resources_path=STANZA_SYNTAX_MODELS_PATH,
                                       depparse_path=os.path.join(STANZA_SYNTAX_MODELS_PATH,
                                                                  'et', 'depparse', 'stanza_depparse.pt'))
    stanza_tagger.tag(text)

    # stanza pipeline (on tokenized unambigous input)
    assert stanza_dict_sentences == layer_to_dict(text.stanza_syntax), text.stanza_syntax.diff(
        dict_to_layer(stanza_dict_sentences))


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                   "Environment variable STANZA_SYNTAX_MODELS_PATH is not defined. .")
def test_stanza_syntax_tagger_analysis():
    text = Text('Väike jänes jooksis metsa! Mina ei jookse.')

    text.tag_layer(['sentences', 'morph_analysis'])
    stanza_tagger_ma = StanzaSyntaxTagger(output_layer='stanza_ma', input_type='morph_analysis',
                                          resources_path=STANZA_SYNTAX_MODELS_PATH)
    stanza_tagger_ma.tag(text)

    # stanza pipeline (on tokenized unambigous input)
    assert stanza_dict_morph_analysis == layer_to_dict(text.stanza_ma), text.stanza_ma.diff(
        dict_to_layer(stanza_dict_morph_analysis))


@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                   reason="Environment variable STANZA_SYNTAX_MODELS_PATH is not defined.")
def test_stanza_ambiguous():
    """Testing seed on ambigous analysis"""
    text = Text('Vaata kaotatud ja leitud asjade nurgast')

    text.tag_layer('morph_extended')
    stanza_tagger_me = StanzaSyntaxTagger(input_type='morph_extended',
                                          input_morph_layer='morph_extended',
                                          output_layer='stanza_me',
                                          resources_path=STANZA_SYNTAX_MODELS_PATH,
                                          depparse_path=os.path.join(STANZA_SYNTAX_MODELS_PATH, 'et', 'depparse',
                                                                     'morph_extended.pt'))

    ambiguous_spans = [i for i, span in enumerate(text.morph_extended) if len(span.annotations) > 1]

    assert ambiguous_spans is not None

    ambiguous_deprels = [[] for _ in range(len(ambiguous_spans))]

    # Tag multiple times to check ambiguous pos-tags
    for i in range(10):
        stanza_tagger_me.tag(text)
        for idx, ambiguous_i in enumerate(ambiguous_spans):
            ambiguous_deprels[idx].append(text.stanza_me[ambiguous_i].upostag)
        text.pop_layer('stanza_me')

    assert not any([True if len(set(ambiguous)) > 1 else False for ambiguous in ambiguous_deprels])
