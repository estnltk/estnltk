from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers.system.dict_tagger_2 import SpanTagger
from estnltk.common import abs_path
from estnltk.taggers.system.dict_tagger_2 import Ruleset
import pytest

@pytest.mark.skip(reason="work in progress")
def test_tagger():
    vocabulary_file = abs_path('tests/taggers/system/dict_tagger_2/span_tagger/span_vocabulary.csv')
    ruleset = Ruleset()
    ruleset.load(file_name=vocabulary_file, key_column='_token_')
    tagger = SpanTagger(output_layer='tagged_tokens',
                        input_layer='morph_analysis',
                        input_attribute='lemma',
                        ruleset=ruleset,
                        output_attributes=['value', '_priority_'],  # default: None
                        key='_token_',  # default: '_token_'
                        validator_attribute=None,  # the default:
                        ambiguous=True  # default: False
                        )
    input_file = abs_path('tests/taggers/system/dict_tagger_2/span_tagger/span_tagger_input.json')
    target_file = abs_path('tests/taggers/system/dict_tagger_2/span_tagger/span_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()