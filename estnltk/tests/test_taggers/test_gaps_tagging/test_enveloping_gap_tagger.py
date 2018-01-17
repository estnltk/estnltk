from estnltk.taggers import EnvelopingGapTagger
from estnltk import Text
from estnltk.spans import SpanList
from estnltk.layer import Layer

text = Text('Üks kaks kolm neli viis kuus seitse.')
text.tag_layer(['words'])

layer = Layer('test_3', enveloping='words')
spl = SpanList()
spl.spans = text.words[0:2]
layer.add_span(spl)
spl = SpanList()
spl.spans = text.words[3:4]
layer.add_span(spl)
text['test_3'] = layer


layer = Layer('test_4', enveloping='words', ambiguous=True)
spl = SpanList()
spl.spans = text.words[3:5]
layer.add_span(spl)
spl = SpanList()
spl.spans = text.words[3:5]
layer.add_span(spl)
text['test_4'] = layer


def test_enveloping_gaps_tagger():
    def decorator(spans):
        return {'gap_word_count': len(spans)}

    gaps_tagger = EnvelopingGapTagger(layer_name='gaps',
                                       input_layers=['test_3', 'test_4'],
                                       enveloped_layer='words',
                                       decorator=decorator,
                                       attributes=['gap_word_count'])

    gaps_tagger.tag(text)
    assert text.gaps.text == [['kolm'], ['kuus', 'seitse', '.']]
    assert text.gaps.gap_word_count == [1, 3]
