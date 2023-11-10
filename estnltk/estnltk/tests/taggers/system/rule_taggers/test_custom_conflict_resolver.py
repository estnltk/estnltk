# Test applying custom conflict_resolver in rule_taggers

import regex

from estnltk import Text
from estnltk.converters import layer_to_dict, dict_to_layer

from estnltk.taggers.system.rule_taggers import StaticExtractionRule
from estnltk.taggers.system.rule_taggers import Ruleset
from estnltk.taggers.system.rule_taggers import AmbiguousRuleset

from estnltk.taggers.system.rule_taggers import SpanTagger
from estnltk.taggers.system.rule_taggers import PhraseTagger
from estnltk.taggers.system.rule_taggers import SubstringTagger
from estnltk.taggers.system.rule_taggers import RegexTagger

# Dummy conflict resolver that always keeps the first annotation and 
# discards others
def _conflict_resolver_keep_first(layer, triples):
    # * layer: a layer to which spans must be added
    # * triples: a list of (annotation, group, priority) triples
    #
    # TODO: what happens if multiple annotations share same span?
    # Revise rule_tagger's iterate_over_decorated_annotations !
    for (annotation, group, priority) in triples:
        # TODO: it's awkward to make a new annotation_dict here
        annotation_dict = {a:annotation[a] for a in layer.attributes}
        layer.add_annotation(annotation.span, annotation_dict)
        break
    return layer

# Decorator that adds explicit phrase text to annotation
def add_span_text_decorator(text, base_span, annotation):
    annotation['text_str'] = text.text[base_span.start:base_span.end]
    return annotation


def test_substring_tagger_with_custom_conflict_resolver():
    # Example text
    text = Text('Muna ja kana.').tag_layer('words')
    # Ambiguous/overlapping rules
    ruleset = Ruleset()
    rules = [StaticExtractionRule(pattern='muna ja', attributes={'_priority_': 0}), 
             StaticExtractionRule(pattern='ja', attributes={'_priority_': 0}),
             StaticExtractionRule(pattern='ja kana', attributes={'_priority_': 0})]
    ruleset.add_rules(rules)
    # Tagger 1: keep all conflicts
    substring_tagger_keep_all = SubstringTagger(output_layer='extracted_all',
                                                output_attributes=['_priority_', 'text_str'],
                                                ambiguous_output_layer=False,
                                                global_decorator=add_span_text_decorator,
                                                conflict_resolver='KEEP_ALL',
                                                ruleset=ruleset,
                                                ignore_case=True)
    substring_tagger_keep_all.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted_all'] ) )
    # assert that the layer has conflicts
    assert layer_to_dict( text['extracted_all'] ) == \
        {'ambiguous': False,
         'attributes': ('_priority_', 'text_str'),
         'enveloping': None,
         'meta': {},
         'name': 'extracted_all',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                    'base_span': (0, 7)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja'}],
                    'base_span': (5, 7)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja kana'}],
                    'base_span': (5, 12)}]}
    # Tagger 2: remove conflicts
    substring_tagger = SubstringTagger(output_layer='extracted',
                                       output_attributes=['_priority_', 'text_str'],
                                       ambiguous_output_layer=False,
                                       global_decorator=add_span_text_decorator,
                                       conflict_resolver=_conflict_resolver_keep_first,
                                       ruleset=ruleset,
                                       ignore_case=True)
    substring_tagger.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted'] ) )
    # assert that conflicts were resolved
    assert layer_to_dict( text['extracted'] ) == \
            {'ambiguous': False,
             'attributes': ('_priority_', 'text_str'),
             'enveloping': None,
             'meta': {},
             'name': 'extracted',
             'parent': None,
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                        'base_span': (0, 7)}]}


def test_regex_tagger_with_custom_conflict_resolver():
    # Example text
    text = Text('Muna ja kana.').tag_layer('words')
    # Ambiguous/overlapping rules
    ruleset = Ruleset()
    rules = [StaticExtractionRule(pattern=regex.Regex('m..a.ja'), attributes={'_priority_': 0}), 
             StaticExtractionRule(pattern=regex.Regex('ja'), attributes={'_priority_': 0}),
             StaticExtractionRule(pattern=regex.Regex('ja.k..a'), attributes={'_priority_': 0})]
    ruleset.add_rules(rules)
    # Tagger 1: keep all conflicts
    regex_tagger_keep_all = RegexTagger(output_layer='extracted_all',
                                        output_attributes=['_priority_', 'text_str'],
                                        decorator=add_span_text_decorator,
                                        conflict_resolver='KEEP_ALL',
                                        ruleset=ruleset,
                                        lowercase_text=True)
    regex_tagger_keep_all.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted_all'] ) )
    # assert that the layer has conflicts
    assert layer_to_dict( text['extracted_all'] ) == \
        {'ambiguous': True,
         'attributes': ('_priority_', 'text_str'),
         'enveloping': None,
         'meta': {},
         'name': 'extracted_all',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                    'base_span': (0, 7)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja'}],
                    'base_span': (5, 7)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja kana'}],
                    'base_span': (5, 12)}]}
    # Tagger 2: remove conflicts
    regex_tagger = RegexTagger(output_layer='extracted',
                               output_attributes=['_priority_', 'text_str'],
                               decorator=add_span_text_decorator,
                               conflict_resolver=_conflict_resolver_keep_first,
                               ruleset=ruleset,
                               lowercase_text=True)
    regex_tagger.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted'] ) )
    # assert that conflicts were resolved
    assert layer_to_dict( text['extracted'] ) == \
            {'ambiguous': True,
             'attributes': ('_priority_', 'text_str'),
             'enveloping': None,
             'meta': {},
             'name': 'extracted',
             'parent': None,
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                        'base_span': (0, 7)}]}


def test_span_tagger_with_custom_conflict_resolver():
    # Example text
    text = Text('Muna ja kana.').tag_layer('words')
    # Ambiguous/overlapping rules
    ruleset = AmbiguousRuleset()
    rules = [StaticExtractionRule(pattern='muna', attributes={'_priority_': 0}), 
             StaticExtractionRule(pattern='ja',   attributes={'_priority_': 0}),
             StaticExtractionRule(pattern='muna', attributes={'_priority_': 1}),
             StaticExtractionRule(pattern='kana', attributes={'_priority_': 0})]
    ruleset.add_rules(rules)
    # Tagger 1: keep all conflicts
    span_tagger_keep_all = SpanTagger(output_layer='extracted_all',
                                      input_layer='words',
                                      input_attribute='text',
                                      ruleset=ruleset,
                                      output_attributes=['_priority_', 'text_str'],
                                      decorator=add_span_text_decorator,
                                      conflict_resolver='KEEP_ALL',
                                      ignore_case=True)
    span_tagger_keep_all.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted_all'] ) )
    # assert that the layer has conflicts
    assert layer_to_dict( text['extracted_all'] ) == \
        {'ambiguous': True,
         'attributes': ('_priority_', 'text_str'),
         'enveloping': None,
         'meta': {},
         'name': 'extracted_all',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna'},
                                    {'_priority_': 1, 'text_str': 'Muna'}],
                    'base_span': (0, 4)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja'}],
                    'base_span': (5, 7)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'kana'}],
                    'base_span': (8, 12)}]}
    # Tagger 2: remove conflicts
    span_tagger = SpanTagger(output_layer='extracted',
                             input_layer='words',
                             input_attribute='text',
                             ruleset=ruleset,
                             output_attributes=['_priority_', 'text_str'],
                             decorator=add_span_text_decorator,
                             conflict_resolver=_conflict_resolver_keep_first,
                             ignore_case=True)
    span_tagger.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted'] ) )
    # assert that conflicts were resolved
    assert layer_to_dict( text['extracted'] ) == \
            {'ambiguous': True,
             'attributes': ('_priority_', 'text_str'),
             'enveloping': None,
             'meta': {},
             'name': 'extracted',
             'parent': 'words',
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna'}],
                        'base_span': (0, 4)}]}


def test_phrase_tagger_with_custom_conflict_resolver():
    # Example text
    text = Text('Muna ja kana.').tag_layer('words')
    # Ambiguous/overlapping rules
    ruleset = Ruleset()
    rules = [StaticExtractionRule(pattern=('muna', 'ja'), attributes={'_priority_': 0}), 
             StaticExtractionRule(pattern=('ja', ), attributes={'_priority_': 0}),
             StaticExtractionRule(pattern=('ja', 'kana'), attributes={'_priority_': 0})]
    ruleset.add_rules(rules)
    # Tagger 1: keep all conflicts
    phrase_tagger_keep_all = PhraseTagger(input_layer='words',
                                          output_layer='extracted_all',
                                          input_attribute='text',
                                          output_attributes=['_priority_', 'text_str'],
                                          decorator=add_span_text_decorator,
                                          conflict_resolver='KEEP_ALL',
                                          ruleset=ruleset,
                                          ignore_case=True)
    phrase_tagger_keep_all.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted_all'] ) )
    # assert that the layer has conflicts
    assert layer_to_dict( text['extracted_all'] ) == \
        {'ambiguous': False,
         'attributes': ('_priority_', 'text_str'),
         'enveloping': 'words',
         'meta': {},
         'name': 'extracted_all',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                    'base_span': ((0, 4), (5, 7))},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja'}],
                    'base_span': ((5, 7),)},
                   {'annotations': [{'_priority_': 0, 'text_str': 'ja kana'}],
                    'base_span': ((5, 7), (8, 12))}]}
    # Tagger 2: remove conflicts
    phrase_tagger = PhraseTagger(input_layer='words',
                                 output_layer='extracted',
                                 input_attribute='text',
                                 output_attributes=['_priority_', 'text_str'],
                                 decorator=add_span_text_decorator,
                                 conflict_resolver=_conflict_resolver_keep_first,
                                 ruleset=ruleset,
                                 ignore_case=True)
    phrase_tagger.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict( text['extracted'] ) )
    # assert that conflicts were resolved
    assert layer_to_dict( text['extracted'] ) == \
            {'ambiguous': False,
             'attributes': ('_priority_', 'text_str'),
             'enveloping': 'words',
             'meta': {},
             'name': 'extracted',
             'parent': None,
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'_priority_': 0, 'text_str': 'Muna ja'}],
                        'base_span': ((0, 4), (5, 7))}]}