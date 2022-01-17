from estnltk.taggers.system.dict_tagger_2 import Ruleset, AmbiguousRuleset
import pytest
from estnltk.common import abs_path

@pytest.mark.skip(reason="work in progress")
def test_ambiguous_rules():
    vocabulary_file = abs_path('tests/taggers/system/dict_tagger_2/span_tagger/ambiguous_span_vocabulary.csv')
    ruleset = AmbiguousRuleset()
    ruleset.load(file_name=vocabulary_file, key_column='_token_')

    assert len(ruleset.static_rules) == 4

    ruleset = Ruleset()

    with pytest.raises(Exception):
        ruleset.load(file_name=vocabulary_file, key_column='_token_')

