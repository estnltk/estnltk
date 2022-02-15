from estnltk import Text
from estnltk import Layer
from estnltk.taggers import HeaderBasedSegmenter


def test_segments_tagger_exclude_headers():
    text = Text('Üks kaks kolm neli viis kuus seitse.')
    layer = Layer('headers', text_object=text)

    tagger = HeaderBasedSegmenter(input_layer='headers', output_layer='segments')

    result = tagger.make_layer(text, layers={'headers': layer})
    assert len(result) == 1
    assert result[0].start == 0
    assert result[0].end == 36

    layer.add_annotation((4, 8))
    layer.add_annotation((9, 13))
    layer.add_annotation((24, 28))

    result = tagger.make_layer(text, layers={'headers': layer})
    assert [(span.start, span.end) for span in result] == [(0, 4), (8, 9), (13, 24), (28, 36)]
    assert result.meta['conflicts_in_input_layer'] == 0

    layer.add_annotation((0, 11))
    layer.add_annotation((26, 28))
    layer.add_annotation((27, 28))

    result = tagger.make_layer(text, layers={'headers': layer})
    assert [(span.start, span.end) for span in result] == [(11, 11), (13, 24), (28, 36)]
    assert result.meta['conflicts_in_input_layer'] == 4


def test_segments_tagger_include_headers():
    text = Text('Üks kaks kolm neli viis kuus seitse.')
    layer = Layer('headers', text_object=text)

    tagger = HeaderBasedSegmenter(input_layer='headers', output_layer='segments', include_header=True)

    result = tagger.make_layer(text, layers={'headers': layer})
    assert len(result) == 1
    assert result[0].start == 0
    assert result[0].end == 36

    layer.add_annotation((4, 8))
    layer.add_annotation((9, 13))
    layer.add_annotation((24, 28))

    result = tagger.make_layer(text, layers={'headers': layer})
    assert [(span.start, span.end) for span in result] == [(0, 4), (4, 9), (9, 24), (24, 36)]
    assert result.meta['conflicts_in_input_layer'] == 0

    layer.add_annotation((0, 11))
    layer.add_annotation((26, 28))
    layer.add_annotation((27, 28))

    result = tagger.make_layer(text, layers={'headers': layer})
    assert [(span.start, span.end) for span in result] == [(0, 11), (9, 24), (24, 36)]
    assert result.meta['conflicts_in_input_layer'] == 4


def test_segments_tagger_decorator():

    def decorator(span):
        return {'attr_1': span.attr,
                'attr_2': span.end - span.start}

    text = Text('Üks kaks kolm neli viis kuus seitse.')
    layer = Layer('headers', attributes=['attr'], text_object=text)

    tagger = HeaderBasedSegmenter(input_layer='headers', output_layer='segments', output_attributes=['attr_1', 'attr_2'],
                                  decorator=decorator)

    result = tagger.make_layer(text, layers={'headers': layer})
    assert len(result) == 1
    assert result[0].start == 0
    assert result[0].end == 36

    layer.add_annotation((4, 8), attr='a')
    layer.add_annotation((9, 13), attr='b')
    layer.add_annotation((24, 28), attr='c')

    result = tagger.make_layer(text, layers={'headers': layer})
    assert [(span.attr_1, span.attr_2) for span in result] == [(None, None), ('a', 4), ('b', 4), ('c', 4)]
