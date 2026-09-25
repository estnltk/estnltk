#!/usr/bin/env python
# coding: utf-8

# python -m pytest -v test_basic_consistency_checker.py

from estnltk import Text, Layer, Span, ElementaryBaseSpan
from estnltk.converters import json_to_text, text_to_json, dict_to_layer, layer_to_dict
import os
import unittest
from importlib.util import find_spec

from estnltk_neural.common import neural_abs_path

def check_if_estnltk_neural_is_available():
    return find_spec("estnltk_neural") is not None

json_folder = "tests/taggers/morphosyntax/test_files_basic_consistency/"

### Example inputs

# no problems
s510950 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_510950.json"))) 
s510950_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': []}

# nsubj aga pole nom/part
s3 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_3.json")))
s3_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (39, 43),
   'annotations': [{'id': 5,
     'lemma': 'Türi',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'S',
     'feats': {'sg': 'sg', 'gen': 'gen', 'prop': 'prop'},
     'extended_feats': None,
     'head': 4,
     'deprel': 'nsubj',
     'error_type': 'basic'}]}]}

# obj aga pole nom/part/gen
# xcomp ja feats pole tühi
s5 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_5.json")))
s5_expected_dict = {'name': 'morphosyntax_consistency',
                     'attributes': ('id',
                      'lemma',
                      'root_tokens',
                      'clitic',
                      'xpostag',
                      'feats',
                      'extended_feats',
                      'head',
                      'deprel',
                      'error_type'),
                     'secondary_attributes': (),
                     'parent': 'v172_stanza_syntax',
                     'enveloping': None,
                     'ambiguous': True,
                     'serialisation_module': None,
                     'meta': {},
                     'spans': [{'base_span': (0, 5),
                       'annotations': [{'id': 1,
                         'lemma': 'bänd',
                         'root_tokens': None,
                         'clitic': None,
                         'xpostag': 'S',
                         'feats': {'sg': 'sg', 'com': 'com', 'adit': 'adit'},
                         'extended_feats': None,
                         'head': 11,
                         'deprel': 'obj',
                         'error_type': 'basic'}]},
                      {'base_span': (31, 37),
                       'annotations': [{'id': 7,
                         'lemma': 'laulma',
                         'root_tokens': None,
                         'clitic': None,
                         'xpostag': 'V',
                         'feats': {'aux': 'aux', 'inf': 'inf'},
                         'extended_feats': None,
                         'head': 6,
                         'deprel': 'xcomp',
                         'error_type': 'basic'}]}]}

# advcl ja feats pole tühi
s16 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_16.json")))
s16_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (38, 44),
   'annotations': [{'id': 6,
     'lemma': 'tegema',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'V',
     'feats': {'ps': 'ps', 'ill': 'ill', 'mod': 'mod', 'sup': 'sup'},
     'extended_feats': None,
     'head': 1,
     'deprel': 'xcomp',
     'error_type': 'basic'}]},
  {'base_span': (60, 65),
   'annotations': [{'id': 11,
     'lemma': 'viis',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'N',
     'feats': {'l': 'l', 'sg': 'sg', 'gen': 'gen', 'card': 'card'},
     'extended_feats': None,
     'head': 1,
     'deprel': 'advcl',
     'error_type': 'basic'}]}]}

# advmod ja feats pole tühi
s21424517 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_21424517.json")))
s21424517_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (23, 26),
   'annotations': [{'id': 4,
     'lemma': 'aga',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'J',
     'feats': {'crd': 'crd', 'sub': 'sub'},
     'extended_feats': None,
     'head': 6,
     'deprel': 'advmod',
     'error_type': 'basic'}]}]}

# nsubj:cop aga pole nom/part
s209696 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_209696.json")))
s209696_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (85, 95),
   'annotations': [{'id': 12,
     'lemma': 'kategooria',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'S',
     'feats': {'sg': 'sg', 'com': 'com', 'gen': 'gen'},
     'extended_feats': None,
     'head': 17,
     'deprel': 'nsubj:cop',
     'error_type': 'basic'}]}]}

# obl ja nom on feats-is
s84 = json_to_text(file = neural_abs_path(os.path.join(json_folder, "sentence_84.json")))
s84_expected_dict = {'name': 'morphosyntax_consistency',
 'attributes': ('id',
  'lemma',
  'root_tokens',
  'clitic',
  'xpostag',
  'feats',
  'extended_feats',
  'head',
  'deprel',
  'error_type'),
 'secondary_attributes': (),
 'parent': 'v172_stanza_syntax',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (30, 37),
   'annotations': [{'id': 5,
     'lemma': 'tüütu',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'A',
     'feats': {'sg': 'sg', 'tr': 'tr', 'pos': 'pos'},
     'extended_feats': None,
     'head': 3,
     'deprel': 'xcomp',
     'error_type': 'basic'}]},
  {'base_span': (87, 91),
   'annotations': [{'id': 13,
     'lemma': 'päev',
     'root_tokens': None,
     'clitic': None,
     'xpostag': 'S',
     'feats': {'sg': 'sg', 'com': 'com', 'nom': 'nom'},
     'extended_feats': None,
     'head': 11,
     'deprel': 'obl',
     'error_type': 'basic'}]}]}


def check_basic_tagger(input_text, expected_dict, num_expected_spans):
    assert 'morphosyntax_consistency' in input_text.layers, "Missing 'morphosyntax_consistency' layer."
    layer = input_text["morphosyntax_consistency"]
    assert len(layer) == num_expected_spans, "'morphosyntax_consistency' layer has more spans than expected."
    assert layer == dict_to_layer(expected_dict), layer.diff(dict_to_layer(expected_dict))


@unittest.skipIf(not check_if_estnltk_neural_is_available(), reason="estnltk_neural is not installed. You'll need estnltk_neural for running this test.")
def test_all_examples():
    from estnltk_neural.taggers import BasicConsistencyChecker

    tagger = BasicConsistencyChecker(
                        morphosyntax_layer = "v172_stanza_syntax",
                         output_layer="morphosyntax_consistency"
                        )

    tagger.tag(s510950)
    tagger.tag(s3)
    tagger.tag(s5)
    tagger.tag(s16)
    tagger.tag(s21424517)
    tagger.tag(s209696)
    tagger.tag(s84)

    check_basic_tagger(s510950, s510950_expected_dict, 0)
    check_basic_tagger(s3, s3_expected_dict, 1)
    check_basic_tagger(s5, s5_expected_dict, 2)
    check_basic_tagger(s16, s16_expected_dict, 2)
    check_basic_tagger(s21424517, s21424517_expected_dict, 1)
    check_basic_tagger(s209696, s209696_expected_dict, 1)
    check_basic_tagger(s84, s84_expected_dict, 2)
    #print("All examples are tested.")



