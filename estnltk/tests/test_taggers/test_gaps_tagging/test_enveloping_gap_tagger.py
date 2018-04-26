from estnltk.taggers import EnvelopingGapTagger
from estnltk import Text
from estnltk.layer.layer import Layer
from estnltk import EnvelopingSpan


def test_enveloping_gaps_tagger():
    text = Text('Üks kaks kolm neli viis kuus seitse.')
    text.tag_layer(['words'])

    layer = Layer('test_3', enveloping='words')
    spl = EnvelopingSpan(spans=text.words[0:2])
    layer.add_span(spl)

    spl = EnvelopingSpan(spans=text.words[3:4])
    layer.add_span(spl)
    text['test_3'] = layer

    layer = Layer('test_4', enveloping='words', ambiguous=True)
    spl = EnvelopingSpan(spans=text.words[3:5])
    layer.add_span(spl)

    spl = EnvelopingSpan(spans=text.words[3:5])
    layer.add_span(spl)
    text['test_4'] = layer

    text['test_5'] = Layer('test_5', enveloping='words')

    def decorator(spans):
        return {'gap_word_count': len(spans)}

    gaps_tagger = EnvelopingGapTagger(output_layer='gaps',
                                      layers_with_gaps=['test_3', 'test_4', 'test_5'],
                                      enveloped_layer='words',
                                      decorator=decorator,
                                      output_attributes=['gap_word_count'])

    gaps_tagger.tag(text)
    assert text.gaps.text == ['kolm', 'kuus', 'seitse', '.']
    assert list(text.gaps.gap_word_count) == [1, 3]

    # gaps in empty layer
    gaps_tagger_2 = EnvelopingGapTagger(output_layer='gaps_2',
                                        layers_with_gaps=['test_5'],
                                        enveloped_layer='words',
                                        decorator=decorator,
                                        output_attributes=['gap_word_count'])
    gaps_tagger_2.tag(text)
    assert text.gaps_2.text == ['Üks', 'kaks', 'kolm', 'neli', 'viis', 'kuus', 'seitse', '.']
    assert list(text.gaps_2.gap_word_count) == [8]
