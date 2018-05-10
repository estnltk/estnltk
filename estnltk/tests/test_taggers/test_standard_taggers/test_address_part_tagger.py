from estnltk.core import rel_path
from estnltk.taggers import TaggerTester
from estnltk.taggers import AddressPartTagger

# test data created by estnltk/dev_documentation/testing/create_tests_for_address_taggers.ipynb


def test_tagger():
    tagger = AddressPartTagger()
    input_file = rel_path('tests/test_taggers/test_standard_taggers/address_part_tagger_input.json')
    target_file = rel_path('tests/test_taggers/test_standard_taggers/address_part_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file).load()
    tester.run_tests()
