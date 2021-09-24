import pytest

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import GapTagger
from estnltk.core import abs_path
from estnltk.taggers import TaggerTester

text = Text('Üks kaks kolm neli viis kuus seitse.')
layer_1 = Layer('test_1')
layer_1.add_annotation((4, 8))
layer_1.add_annotation((9, 13))
layer_1.add_annotation((24, 28))
text.add_layer(layer_1)

layer_2 = Layer('test_2')
layer_2.add_annotation((4, 8))
layer_2.add_annotation((9, 18))
layer_2.add_annotation((35, 36))
text.add_layer(layer_2)

text.add_layer(Layer('test_3'))


def test_gaps_trim():
    def trim(t):
        return t.strip()

    def decorator(t):
        return {'gap_length':len(t)}

    gap_tagger = GapTagger(output_layer='gaps',
                           input_layers=['test_1', 'test_2'],
                           trim=trim,
                           decorator=decorator,
                           output_attributes=['gap_length'])
    gap_tagger.tag(text)

    records = [{'end': 3, 'gap_length': 3, 'start': 0},
               {'end': 23, 'gap_length': 4, 'start': 19},
               {'end': 35, 'gap_length': 6, 'start': 29}]
    assert text['gaps'].to_records() == records


def test_bad_trim():
    def trim(t):
        return 'bla'

    gap_tagger = GapTagger(output_layer='bad_trim',
                           input_layers=['test_1'],
                           trim=trim)
    with pytest.raises(ValueError):
        gap_tagger.tag(text)


# test data created by estnltk/dev_documentation/testing/gap_tagger_testing.ipynb


def test_tagger():
    tagger = GapTagger(input_layers=['test_1', 'test_2', 'test_3'], output_layer='gaps')
    input_file = abs_path('tests/test_taggers/test_standard_taggers/gap_tagger_input.json')
    target_file = abs_path('tests/test_taggers/test_standard_taggers/gap_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()
