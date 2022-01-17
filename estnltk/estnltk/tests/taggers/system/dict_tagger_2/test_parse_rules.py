from estnltk.taggers.system.dict_tagger_2 import Ruleset, AmbiguousRuleset
import pytest
from estnltk.taggers.system.dict_tagger_2.extraction_rules.static_extraction_rule import StaticExtractionRule
from estnltk.common import abs_path

@pytest.mark.skip(reason="work in progress")
def test_parse_rules():
    rules = AmbiguousRuleset()
    rules.load(abs_path('tests/taggers/system/dict_tagger_2/data/short.csv'))
    assert len(rules.static_rules) == 8
    for rule in rules.static_rules:
        assert type(rule) == StaticExtractionRule

    rules.load(abs_path('tests/taggers/system/dict_tagger_2/data/short.csv'), group_column='_group_', mode='overwrite')
    assert len(rules.static_rules) == 8
    for rule in rules.static_rules:
        assert type(rule) == StaticExtractionRule

    rules.load(abs_path('tests/taggers/system/dict_tagger_2/data/short.csv'), group_column='_group_', mode='append')
    assert len(rules.static_rules) == 16
    for i in range(8):
        assert rules.static_rules[i] == rules.static_rules[i + 8]

    with pytest.raises(ValueError):
        rules = Ruleset()
        rules.load(abs_path('tests/taggers/system/dict_tagger_2/data/missing.csv'))
