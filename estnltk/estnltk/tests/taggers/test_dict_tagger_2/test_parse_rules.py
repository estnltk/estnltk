from estnltk.taggers.system.dict_tagger_2 import Ruleset
import pytest
from estnltk.taggers.system.dict_tagger_2.extraction_rules.static_extraction_rule import StaticExtractionRule

@pytest.mark.skip(reason="data file is missing")
def test_parse_rules():
    rules = Ruleset()
    rules.load('data/short.csv')
    assert len(rules.static_rules) == 8
    for rule in rules.static_rules:
        assert type(rule) == StaticExtractionRule

    rules.load('data/short.csv', group_column='_group_', mode='overwrite')
    assert len(rules.static_rules) == 8
    for rule in rules.static_rules:
        assert type(rule) == StaticExtractionRule

    rules.load('data/short.csv', group_column='_group_', priority_column='_priority_', mode='append')
    assert len(rules.static_rules) == 16
    for i in range(8):
        assert rules.static_rules[i] == rules.static_rules[i + 8]

    with pytest.raises(FileNotFoundError):
        rules = Ruleset()
        rules.load('data/missing.csv')
