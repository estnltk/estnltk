from estnltk import Text
from estnltk.layer import Layer
from estnltk.spans import Span
from estnltk.taggers.gaps_tagging.gaps_tagger import GapsTagger

text = Text('Üks kaks kolm neli viis kuus seitse.')
layer_1 = Layer('test_1')
layer_1.add_span(Span(4, 8))
layer_1.add_span(Span(9, 13))
layer_1.add_span(Span(24, 28))
text['test_1'] = layer_1

layer_2 = Layer('test_2')
layer_2.add_span(Span(4, 8))
layer_2.add_span(Span(9, 18))
layer_2.add_span(Span(35, 36))
text['test_2'] = layer_2


def test_gaps():
    gaps_tagger = GapsTagger('simple_gaps', ['test_1', 'test_2'])
    gaps_tagger.tag(text)

    records = [{'end': 4, 'start': 0},
               {'end': 9, 'start': 8},
               {'end': 24, 'start': 18},
               {'end': 35, 'start': 28}]
    assert text['simple_gaps'].to_records() == records


def test_gaps_trim():
    def trim(t:str) -> str:
        return t.strip()

    def decorator(text:str):
        return {'gap_length':len(text)}

    gaps_tagger = GapsTagger(layer_name='gaps',
                             input_layers=['test_1', 'test_2'],
                             trim=trim,
                             decorator=decorator,
                             attributes=['gap_length'])
    gaps_tagger.tag(text)

    records = [{'end': 3, 'gap_length': 3, 'start': 0},
               {'end': 23, 'gap_length': 4, 'start': 19},
               {'end': 35, 'gap_length': 6, 'start': 29}]
    assert text['gaps'].to_records() == records
