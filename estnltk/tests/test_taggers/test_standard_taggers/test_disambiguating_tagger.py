from estnltk import Text, Layer
from estnltk.taggers import DisambiguatingTagger


def test_1():
    text = Text('Tere, maailm!')

    layer_1 = Layer(name='simple_ambiguous', attributes=['attr_1', 'attr_2'], ambiguous=True, text_object=text)
    layer_1.add_annotation((0, 4), attr_1=1, attr_2=2)
    layer_1.add_annotation((0, 4), attr_1=3, attr_2=4)
    layer_1.add_annotation((0, 4), attr_1=5, attr_2=6)
    layer_1.add_annotation((4, 5), attr_1=7, attr_2=8)
    layer_1.add_annotation((4, 5), attr_1=9, attr_2=10)
    layer_1.add_annotation((0, 4), attr_1=11, attr_2=12)
    layer_1.add_annotation((6, 12), attr_1=13, attr_2=14)
    layer_1.add_annotation((6, 12), attr_1=15, attr_2=16)
    layer_1.add_annotation((12, 13), attr_1=17, attr_2=18)
    text['simple_ambiguous'] = layer_1

    def decorator(ambiguous_span, raw_text):
        attr_1 = 0
        for annotation in ambiguous_span.annotations:
            attr_1 += annotation.attr_1
        return {'attr_1': attr_1}

    tagger_1 = DisambiguatingTagger(output_layer='simple',
                                    input_layer='simple_ambiguous',
                                    output_attributes=['attr_1'],
                                    decorator=decorator)
    tagger_1.tag(text)

    assert text.simple.to_records() == [
        {'attr_1': 20, 'start': 0, 'end': 4},
        {'attr_1': 16, 'start': 4, 'end': 5},
        {'attr_1': 28, 'start': 6, 'end': 12},
        {'attr_1': 17, 'start': 12, 'end': 13}]

    layer_2 = Layer(name='enveloping_ambiguous',
                    attributes=['attr_3'],
                    enveloping='simple_ambiguous',
                    ambiguous=True)

    spans = text.simple_ambiguous[0:2]
    layer_2.add_annotation(spans, attr_3=30)
    layer_2.add_annotation(spans, attr_3=31)

    spans = text.simple_ambiguous[2:4]
    layer_2.add_annotation(spans, attr_3=32)

    text['enveloping_ambiguous'] = layer_2

    def decorator(ambiguous_span, raw_text):
        return {'attr_1': len(ambiguous_span)}

    tagger_2 = DisambiguatingTagger(output_layer='enveloping',
                                    input_layer='enveloping_ambiguous',
                                    output_attributes=['attr_1', ],
                                    decorator=decorator
                                    )
    tagger_2.tag(text)

    assert text.enveloping.to_records() == [
        [[{'attr_2': 2, 'attr_1': 1, 'start': 0, 'end': 4},
          {'attr_2': 4, 'attr_1': 3, 'start': 0, 'end': 4},
          {'attr_2': 6, 'attr_1': 5, 'start': 0, 'end': 4},
          {'attr_2': 12, 'attr_1': 11, 'start': 0, 'end': 4}],
         [{'attr_2': 8, 'attr_1': 7, 'start': 4, 'end': 5},
          {'attr_2': 10, 'attr_1': 9, 'start': 4, 'end': 5}]],
        [[{'attr_2': 14, 'attr_1': 13, 'start': 6, 'end': 12},
          {'attr_2': 16, 'attr_1': 15, 'start': 6, 'end': 12}],
         [{'attr_2': 18, 'attr_1': 17, 'start': 12, 'end': 13}]]]