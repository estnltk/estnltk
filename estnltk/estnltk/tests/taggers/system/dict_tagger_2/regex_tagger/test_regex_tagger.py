from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers.system.dict_tagger_2 import RegexTagger, Ruleset
from estnltk.common import abs_path

import pytest

@pytest.mark.xfail(reason="work in progress")
def test_tagger():
    vocabulary_file = abs_path('tests/taggers/system/dict_tagger_2/regex_tagger/regex_vocabulary.csv')
    ruleset = Ruleset()
    ruleset.load(file_name=vocabulary_file, key_column='_regex_pattern_')
    tokenization_hints_tagger = RegexTagger(ruleset=ruleset,
                                            output_layer='tokenization_hints',  # default 'regexes'
                                            output_attributes=['normalized', '_priority_'],  # default: None
                                            conflict_resolving_strategy='MAX',  # default 'MAX'
                                            overlapped=False,  # default False
                                            priority_attribute=None,  # default None
                                            ignore_case=False  # default False
                                            )
    input_file = abs_path('tests/taggers/system/dict_tagger_2/regex_tagger/regex_tagger_input.json')
    target_file = abs_path('tests/taggers/system/dict_tagger_2/regex_tagger/regex_tagger_target.json')

    tester = TaggerTester(tokenization_hints_tagger, input_file, target_file)
    tester.load()
    tester.run_tests()