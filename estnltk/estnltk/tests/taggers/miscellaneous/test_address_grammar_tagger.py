from estnltk.common import abs_path
from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers import AddressGrammarTagger

# test data created by estnltk/dev_documentation/testing/test_data_for_address_taggers.ipynb


def test_tagger():
    tagger = AddressGrammarTagger()
    input_file = abs_path('tests/taggers/miscellaneous/address_grammar_tagger_input.json')
    target_file = abs_path('tests/taggers/miscellaneous/address_grammar_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()
