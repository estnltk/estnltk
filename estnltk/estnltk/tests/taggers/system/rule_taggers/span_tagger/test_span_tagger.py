import pytest

from estnltk_core.taggers.tagger_tester import TaggerTester

from estnltk import Text
from estnltk.common import abs_path

from estnltk.taggers.system.rule_taggers import SpanTagger
from estnltk.taggers.system.rule_taggers import Ruleset, StaticExtractionRule
from estnltk.converters import layer_to_dict, dict_to_layer

def test_tagger():
    vocabulary_file = abs_path('tests/taggers/system/rule_taggers/span_tagger/span_vocabulary.csv')
    ruleset = Ruleset()
    ruleset.load(file_name=vocabulary_file, key_column='_token_')
    tagger = SpanTagger(output_layer='tagged_tokens',
                        input_layer='morph_analysis',
                        input_attribute='lemma',
                        ruleset=ruleset,
                        output_attributes=['value', '_priority_'],  # default: None
                        )
    input_file = abs_path('tests/taggers/system/rule_taggers/span_tagger/span_tagger_input.json')
    target_file = abs_path('tests/taggers/system/rule_taggers/span_tagger/span_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()


def test_span_tagger_output_attributes():
    # Test changing SpanTagger's output_attributes
    text = Text('Suur ja väike.')
    text.add_layer( \
        dict_to_layer( \
            {'ambiguous': True,
             'attributes': ('normalized_form',),
             'enveloping': None,
             'meta': {},
             'name': 'words',
             'parent': None,
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                       {'annotations': [{'normalized_form': None}], 'base_span': (5, 7)},
                       {'annotations': [{'normalized_form': None}], 'base_span': (8, 13)},
                       {'annotations': [{'normalized_form': None}], 'base_span': (13, 14)}]}
        )
    )
    # Case 1: output layer without attributes
    ruleset = Ruleset()
    ruleset.add_rules([StaticExtractionRule(pattern='SUUR'), \
                       StaticExtractionRule(pattern='väike')])
    span_tagger = SpanTagger(input_layer='words',
                             output_layer='test_spans_1',
                             input_attribute='text',
                             output_attributes=[],
                             ruleset=ruleset)
    span_tagger.tag(text)
    assert layer_to_dict(text['test_spans_1']) == \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'test_spans_1',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{}], 'base_span': (8, 13)}]}
    # Case 2: output layer with attributes
    ruleset = Ruleset()
    ruleset.add_rules([StaticExtractionRule(pattern='SUUR',  attributes={'attrib_a':1, 'attrib_b': 'X'}), \
                       StaticExtractionRule(pattern='väike', attributes={'attrib_a':2, 'attrib_b': 'Y'})])
    span_tagger = SpanTagger(input_layer='words',
                             output_layer='test_spans_2',
                             input_attribute='text',
                             output_attributes=['attrib_a', 'attrib_b'],
                             ruleset=ruleset)
    span_tagger.tag(text)
    assert layer_to_dict(text['test_spans_2']) == \
        {'ambiguous': False,
         'attributes': ('attrib_a', 'attrib_b'),
         'enveloping': None,
         'meta': {},
         'name': 'test_spans_2',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'attrib_a': 2, 'attrib_b': 'Y'}],
                    'base_span': (8, 13)}]}
    # Case 3: output layer with undeclared output_attributes (error)
    span_tagger = SpanTagger(input_layer='words',
                             output_layer='test_spans_3',
                             input_attribute='text',
                             output_attributes=[],
                             ruleset=ruleset)
    with pytest.raises(ValueError):
        #  ValueError: ("the annotation has unexpected or missing attributes 
        #  {'attrib_a', 'attrib_b'}!=set()", "in the 'SpanTagger'")
        span_tagger.tag(text)
