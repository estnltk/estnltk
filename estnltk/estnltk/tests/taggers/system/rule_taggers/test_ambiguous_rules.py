from estnltk.taggers.system.rule_taggers import Ruleset, AmbiguousRuleset
import pytest
from estnltk.common import abs_path

def test_ambiguous_rules():
    vocabulary_file = abs_path('tests/taggers/system/rule_taggers/span_tagger/ambiguous_span_vocabulary.csv')
    ruleset = AmbiguousRuleset()
    ruleset.load(file_name=vocabulary_file, key_column='_token_')

    assert len(ruleset.static_rules) == 4

    ruleset = Ruleset()

    with pytest.raises(Exception):
        ruleset.load(file_name=vocabulary_file, key_column='_token_')

