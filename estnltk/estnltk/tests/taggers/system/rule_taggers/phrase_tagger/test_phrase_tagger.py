from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers.system.rule_taggers import PhraseTagger
from estnltk.taggers.system.rule_taggers import Ruleset
from estnltk.common import abs_path
import pytest

@pytest.mark.xfail(reason="fails because of json converter")
def test_tagger():

    vocabulary_file = 'phrase_vocabulary.csv'
    ruleset = Ruleset()
    ruleset.load(file_name=vocabulary_file, key_column='_phrase_')

    def decorator(span, annotation):
        assert span is annotation.span
        annotation['attr_1'] = 'default_1'
        annotation['attr_2'] = len(span)
        annotation['_priority_'] = 1
        return True

    tagger = PhraseTagger(output_layer='phrases',
                          input_layer='morph_analysis',
                          input_attribute='lemma',
                          ruleset=ruleset,
                          key='_phrase_',
                          output_attributes=['value', '_priority_', 'attr_1', 'attr_2', '_phrase_'],
                          decorator=decorator,
                          conflict_resolving_strategy='ALL',
                          priority_attribute='_priority_',
                          output_ambiguous=True)
    input_file = abs_path('tests/taggers/system/dict_tagger_2/phrase_tagger/phrase_tagger_input.json')
    target_file = abs_path('tests/taggers/system/dict_tagger_2/phrase_tagger/phrase_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()