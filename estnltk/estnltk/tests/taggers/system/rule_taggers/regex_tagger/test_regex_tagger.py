from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers.system.rule_taggers import RegexTagger, Ruleset
from estnltk.common import abs_path


def test_tagger():
    vocabulary_file = abs_path('tests/taggers/system/rule_taggers/regex_tagger/regex_vocabulary.csv')
    ruleset = Ruleset()
    ruleset.load(file_name=vocabulary_file, key_column='_regex_pattern_')
    tokenization_hints_tagger = RegexTagger(ruleset=ruleset,
                                            output_layer='tokenization_hints',  # default 'regexes'
                                            output_attributes=['normalized', '_priority_'],  # default: None
                                            overlapped=False,  # default False
                                            )
    input_file = abs_path('tests/taggers/system/rule_taggers/regex_tagger/regex_tagger_input.json')
    target_file = abs_path('tests/taggers/system/rule_taggers/regex_tagger/regex_tagger_target.json')

    tester = TaggerTester(tokenization_hints_tagger, input_file, target_file)
    tester.load()
    tester.run_tests()