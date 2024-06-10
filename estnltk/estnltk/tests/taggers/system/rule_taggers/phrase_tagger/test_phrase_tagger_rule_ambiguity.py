from estnltk import Text

from estnltk.converters import text_to_dict, dict_to_text
#from estnltk.converters import dict_to_layer, layer_to_dict

from estnltk.taggers.system.rule_taggers import AmbiguousRuleset
from estnltk.taggers.system.rule_taggers import StaticExtractionRule 
from estnltk.taggers.system.rule_taggers import PhraseTagger

#
#  Problem statement: Although left-hand sides of rules are guaranteed to be distinct by 
#  construction, this does not guarantee that different rules cannot match the same spans. 
#  As a result, the assumptions of standard conflict resolving strategies:
#    * keep_maximal_matches
#    * keep_minimal_matches
#  are not satisfied. Such cases must be tested to achieve correct behaviour.
#

# Input sentence with ambiguous 'morph_analysis'
input_sentence_with_ambiguous_morph = \
        {'text': 'Varsti tuleb Euroopa Liidust lahkumine.',
         'layers': [{'ambiguous': False,
                     'attributes': (),
                     'enveloping': None,
                     'meta': {},
                     'name': 'tokens',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{}], 'base_span': (0, 6)},
                               {'annotations': [{}], 'base_span': (7, 12)},
                               {'annotations': [{}], 'base_span': (13, 20)},
                               {'annotations': [{}], 'base_span': (21, 28)},
                               {'annotations': [{}], 'base_span': (29, 38)},
                               {'annotations': [{}], 'base_span': (38, 39)}]},
                    {'ambiguous': False,
                     'attributes': ('type', 'normalized'),
                     'enveloping': 'tokens',
                     'meta': {},
                     'name': 'compound_tokens',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': []},
                    {'ambiguous': True,
                     'attributes': ('normalized_form',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'words',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'normalized_form': None}],
                                'base_span': (0, 6)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (7, 12)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (13, 20)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (21, 28)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (29, 38)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (38, 39)}]},
                    {'ambiguous': True,
                     'attributes': ('normalized_text',
                                    'lemma',
                                    'root',
                                    'root_tokens',
                                    'ending',
                                    'clitic',
                                    'form',
                                    'partofspeech'),
                     'enveloping': None,
                     'meta': {},
                     'name': 'morph_analysis',
                     'parent': 'words',
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': '',
                                                 'lemma': 'varsti',
                                                 'normalized_text': 'Varsti',
                                                 'partofspeech': 'D',
                                                 'root': 'varsti',
                                                 'root_tokens': ['varsti']}],
                                'base_span': (0, 6)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'b',
                                                 'form': 'b',
                                                 'lemma': 'tulema',
                                                 'normalized_text': 'tuleb',
                                                 'partofspeech': 'V',
                                                 'root': 'tule',
                                                 'root_tokens': ['tule']}],
                                'base_span': (7, 12)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': 'sg g',
                                                 'lemma': 'Euroopa',
                                                 'normalized_text': 'Euroopa',
                                                 'partofspeech': 'H',
                                                 'root': 'Euroopa',
                                                 'root_tokens': ['Euroopa']}],
                                'base_span': (13, 20)},
                               {'annotations': [{'clitic': '',
                                                 'ending': 'st',
                                                 'form': 'sg el',
                                                 'lemma': 'Liidu',
                                                 'normalized_text': 'Liidust',
                                                 'partofspeech': 'H',
                                                 'root': 'Liidu',
                                                 'root_tokens': ['Liidu']},
                                                {'clitic': '',
                                                 'ending': 'st',
                                                 'form': 'sg el',
                                                 'lemma': 'Liidud',
                                                 'normalized_text': 'Liidust',
                                                 'partofspeech': 'H',
                                                 'root': 'Liidud',
                                                 'root_tokens': ['Liidud']},
                                                {'clitic': '',
                                                 'ending': 'st',
                                                 'form': 'sg el',
                                                 'lemma': 'Liit',
                                                 'normalized_text': 'Liidust',
                                                 'partofspeech': 'H',
                                                 'root': 'Liit',
                                                 'root_tokens': ['Liit']}],
                                'base_span': (21, 28)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '0',
                                                 'form': 'sg n',
                                                 'lemma': 'lahkumine',
                                                 'normalized_text': 'lahkumine',
                                                 'partofspeech': 'S',
                                                 'root': 'lahkumine',
                                                 'root_tokens': ['lahkumine']}],
                                'base_span': (29, 38)},
                               {'annotations': [{'clitic': '',
                                                 'ending': '',
                                                 'form': '',
                                                 'lemma': '.',
                                                 'normalized_text': '.',
                                                 'partofspeech': 'Z',
                                                 'root': '.',
                                                 'root_tokens': ['.']}],
                                'base_span': (38, 39)}]},
                    {'ambiguous': False,
                     'attributes': (),
                     'enveloping': 'words',
                     'meta': {},
                     'name': 'sentences',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{}],
                                'base_span': ((0, 6),
                                              (7, 12),
                                              (13, 20),
                                              (21, 28),
                                              (29, 38),
                                              (38, 39))}]}],
         'meta': {},
         'relation_layers': [] }


def test_phrase_tagger_rule_ambiguity_with_keep_maximal():
    # I. Initial test case (KEEP_MAXIMAL)
    # Create input sentence Text obj
    sent_obj = dict_to_text( input_sentence_with_ambiguous_morph )
    # A) Create ambiguous rules (long pattern)
    ruleset = AmbiguousRuleset()
    ruleset.add_rules([
        StaticExtractionRule(pattern=('euroopa', 'liidu'), attributes={'value': 'ORG'}),
        StaticExtractionRule(pattern=('euroopa', 'liit'), attributes={'value': 'ORG'})])
    phrasetagger = PhraseTagger(
        output_layer='entity_phrases',
        input_layer='morph_analysis',
        input_attribute='lemma',
        ruleset=ruleset,
        output_attributes=['value'],
        conflict_resolver='KEEP_MAXIMAL',
        ignore_case=True)
    phrasetagger.tag(sent_obj)
    extracted_phrases = [(ph.text, [a['value'] for a in ph.annotations]) for ph in sent_obj['entity_phrases']]
    assert extracted_phrases == [(['Euroopa', 'Liidust'], ['ORG'])]

    # B) Create ambiguous rules (short pattern)
    ruleset = AmbiguousRuleset()
    ruleset.add_rules([
        StaticExtractionRule(pattern=('liidu',), attributes={'value': 'ORG'}),
        StaticExtractionRule(pattern=('liit',), attributes={'value': 'ORG'})])
    phrasetagger2 = PhraseTagger(
        output_layer='entity_phrases_2',
        input_layer='morph_analysis',
        input_attribute='lemma',
        ruleset=ruleset,
        output_attributes=['value'],
        conflict_resolver='KEEP_MAXIMAL',
        ignore_case=True)
    phrasetagger2.tag(sent_obj)
    extracted_phrases = [(ph.text, [a['value'] for a in ph.annotations]) for ph in sent_obj['entity_phrases_2']]
    assert extracted_phrases == [(['Liidust'], ['ORG'])]


def test_phrase_tagger_rule_ambiguity_with_keep_minimal():
    # II. Test case (KEEP_MINIMAL)
    # Create input sentence Text obj
    sent_obj = dict_to_text( input_sentence_with_ambiguous_morph )
    # A) Create ambiguous rules (long pattern)
    ruleset = AmbiguousRuleset()
    ruleset.add_rules([
        StaticExtractionRule(pattern=('euroopa', 'liidu'), attributes={'value': 'ORG'}),
        StaticExtractionRule(pattern=('euroopa', 'liit'), attributes={'value': 'ORG'})])
    phrasetagger = PhraseTagger(
        output_layer='entity_phrases',
        input_layer='morph_analysis',
        input_attribute='lemma',
        ruleset=ruleset,
        output_attributes=['value'],
        conflict_resolver='KEEP_MINIMAL',
        ignore_case=True)
    phrasetagger.tag(sent_obj)
    extracted_phrases = [(ph.text, [a['value'] for a in ph.annotations]) for ph in sent_obj['entity_phrases']]
    assert extracted_phrases == [(['Euroopa', 'Liidust'], ['ORG'])]
    
    # B) Create ambiguous rules (short pattern)
    ruleset = AmbiguousRuleset()
    ruleset.add_rules([
        StaticExtractionRule(pattern=('liidu',), attributes={'value': 'ORG'}),
        StaticExtractionRule(pattern=('liit',), attributes={'value': 'ORG'})])
    phrasetagger2 = PhraseTagger(
        output_layer='entity_phrases_2',
        input_layer='morph_analysis',
        input_attribute='lemma',
        ruleset=ruleset,
        output_attributes=['value'],
        conflict_resolver='KEEP_MINIMAL',
        ignore_case=True)
    phrasetagger2.tag(sent_obj)
    extracted_phrases = [(ph.text, [a['value'] for a in ph.annotations]) for ph in sent_obj['entity_phrases_2']]
    assert extracted_phrases == [(['Liidust'], ['ORG'])]
