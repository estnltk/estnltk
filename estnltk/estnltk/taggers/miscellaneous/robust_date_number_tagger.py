from typing import Sequence

import regex

from estnltk.taggers import Tagger

from estnltk.taggers.system.rule_taggers import RegexTagger, Ruleset
from estnltk.taggers.system.rule_taggers import StaticExtractionRule, DynamicExtractionRule

from estnltk_core.layer_operations import resolve_conflicts

from .robust_date_number_vocabulary import vocabulary as VOCABULARY


class RobustDateNumberTagger(Tagger):
    """
    Tags dates and numbers.
    """
    conf_param = ['tagger']

    def __init__(self,
                 output_attributes: Sequence=('grammar_symbol', 'regex_type', 'value', '_priority_'),
                 conflict_resolver: str='KEEP_MAXIMAL',
                 overlapped: bool=True,
                 output_layer: str='dates_numbers',
                 ):
        self.output_attributes = output_attributes
        self.output_layer = output_layer
        self.input_layers = []
        ruleset = RobustDateNumberTagger._create_extraction_rules( VOCABULARY )
        self.tagger = RegexTagger(ruleset=ruleset, 
                                  conflict_resolver=conflict_resolver, 
                                  output_attributes=output_attributes, 
                                  overlapped=overlapped,
                                  output_layer=output_layer)

    @staticmethod
    def _create_extraction_rules(vocabulary):
        rules = []
        for voc_item in vocabulary:
            if callable( voc_item['value'] ):
                dynamic_rule = DynamicExtractionRule(pattern=regex.Regex( voc_item['_regex_pattern_']),
                                                     group=voc_item['_group_'],
                                                     decorator = voc_item['value'])
                rules.append(dynamic_rule)
                static_rule = StaticExtractionRule( pattern=regex.Regex( voc_item['_regex_pattern_'] ),
                                         group=voc_item['_group_'],
                                         attributes={ 'grammar_symbol':voc_item['grammar_symbol'],
                                                      'regex_type': voc_item['regex_type'],
                                                      '_priority_': voc_item['_priority_']} )
                rules.append(static_rule)
            else:
                rule = StaticExtractionRule( pattern=regex.Regex( voc_item['_regex_pattern_'] ),
                                             group=voc_item['_group_'],
                                             attributes={ 'grammar_symbol':voc_item['grammar_symbol'],
                                                          'regex_type': voc_item['regex_type'],
                                                          'value': voc_item['value'],
                                                          '_priority_': voc_item['_priority_']} )
                rules.append(rule)
        ruleset = Ruleset()
        ruleset.add_rules(rules)
        return ruleset

    def _make_layer_template(self):
        return self.tagger._make_layer_template()

    def _make_layer(self, text, layers, status):
        new_layer = self.tagger.make_layer(text=text, layers=layers, status=status)
        # TODO: in future, RegexTagger should be able to resolve_conflicts by itself
        return resolve_conflicts(new_layer, priority_attribute='_priority_')

