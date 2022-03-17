from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers.system.rule_taggers import SpanTagger
from estnltk.common import abs_path
from estnltk.taggers.system.rule_taggers import Ruleset

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