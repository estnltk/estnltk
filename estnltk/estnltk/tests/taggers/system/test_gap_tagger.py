import pytest

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import GapTagger
from estnltk.common import abs_path
from estnltk_core.converters import layer_to_records
from estnltk_core.taggers.tagger_tester import TaggerTester

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

# ============================================
#     Test GapTagger's default mode
# ============================================

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
    assert layer_to_records( text['gaps'] ) == records


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
    input_file = abs_path('tests/taggers/system/gap_tagger_input.json')
    target_file = abs_path('tests/taggers/system/gap_tagger_target.json')

    tester = TaggerTester(tagger, input_file, target_file)
    tester.load()
    tester.run_tests()


# ============================================
#     Test GapTagger's EnvelopingGap mode
# ============================================

def test_gaps_tagger_enveloping_mode():
    text = Text('Üks kaks kolm neli viis kuus seitse.')
    text.tag_layer(['words'])

    layer = Layer('test_3', enveloping='words')
    layer.add_annotation(text.words[0:2])

    layer.add_annotation(text.words[3:4])
    text.add_layer(layer)

    layer = Layer('test_4', enveloping='words', ambiguous=True)
    layer.add_annotation(text.words[3:5])

    layer.add_annotation(text.words[3:5])
    text.add_layer(layer)

    text.add_layer(Layer('test_5', enveloping='words'))

    def decorator(spans):
        return {'gap_word_count': len(spans)}

    gaps_tagger = GapTagger(output_layer='gaps',
                            input_layers=['test_3', 'test_4', 'test_5'],
                            enveloped_layer='words',
                            enveloping_mode=True,
                            decorator=decorator,
                            output_attributes=['gap_word_count'])

    gaps_tagger.tag(text)
    assert text.gaps.text == ['kolm', 'kuus', 'seitse', '.']
    assert list(text.gaps.gap_word_count) == [1, 3]

    # gaps in empty layer
    gaps_tagger_2 = GapTagger(output_layer='gaps_2',
                              input_layers=['test_5'],
                              enveloped_layer='words',
                              enveloping_mode=True,
                              decorator=decorator,
                              output_attributes=['gap_word_count'])
    gaps_tagger_2.tag(text)
    assert text.gaps_2.text == ['Üks', 'kaks', 'kolm', 'neli', 'viis', 'kuus', 'seitse', '.']
    assert list(text.gaps_2.gap_word_count) == [8]
