from estnltk.common import abs_path
from estnltk_core.taggers.tagger_tester import TaggerTester
from estnltk.taggers import AddressPartTagger

# test data created by estnltk/dev_documentation/testing/test_data_for_address_taggers.ipynb


def test_tagger():
    tagger = AddressPartTagger()
    input_file = abs_path('tests/taggers/miscellaneous/address_part_tagger_input.json')
    target_file = abs_path('tests/taggers/miscellaneous/address_part_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file).load()
    tester.run_tests()
