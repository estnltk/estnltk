import pytest
from estnltk_core.layer.layer import Layer
from estnltk_core.layer_operations import resolve_conflicts
from estnltk_core.converters import records_to_layer

def test_conflict_resolving_strategy_type():
    with pytest.raises(ValueError):
        resolve_conflicts(layer=Layer(name='test_layer', attributes=['_priority_']),
                          conflict_resolving_strategy='unexpected value')


def test_no_conflict_resolving():
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 0},
                                     {'start': 2, 'end':  4, '_priority_': 1},
                                     {'start': 3, 'end':  6, '_priority_': 2}])
    result = resolve_conflicts(layer=layer,
                               conflict_resolving_strategy='ALL',
                               priority_attribute=None)
    assert result is layer
    assert len(result) == 3


def test_status():
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 0},
                                     {'start': 2, 'end':  4, '_priority_': 1},
                                     {'start': 3, 'end':  6, '_priority_': 2}])

    status = {}
    result = resolve_conflicts(layer=layer,
                               conflict_resolving_strategy='ALL',
                               status=status,
                               priority_attribute='_priority_')

    assert status == {'number_of_conflicts': 3}
    assert result is layer
    assert len(result) == 1


def test_resolve_conflicts_MAX():
    # empty span list
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [] == [(span.start, span.end) for span in layer]

    # one span
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  4, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # equal spans
    layer = Layer(name='test_layer', attributes=['_priority_'], ambiguous=True)
    layer = records_to_layer(layer, [[{'start': 1, 'end':  4, '_priority_': 0},
                                      {'start': 1, 'end':  4, '_priority_': 0} ]])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert len(layer[0].annotations) == 1
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common start
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  4, '_priority_': 0},
                                     {'start': 1, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [(1, 6)] == [(span.start, span.end) for span in layer]

    # common end
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 3, 'end':  6, '_priority_': 0},
                                     {'start': 1, 'end':  6, '_priority_': 0} ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [(1, 6)] == [(span.start, span.end) for span in layer]

    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 0},
                                     {'start': 2, 'end':  4, '_priority_': 0},
                                     {'start': 3, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [(1, 8)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 1},
                                     {'start': 2, 'end':  4, '_priority_': 0},
                                     {'start': 3, 'end':  6, '_priority_': 1}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute='_priority_')
    assert [(2, 4)] == [(span.start, span.end) for span in layer]

    # complex, no priority attribute
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 1},
                                     {'start': 2, 'end':  4, '_priority_': 0},
                                     {'start': 3, 'end':  6, '_priority_': 1}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX', priority_attribute=None)
    assert [(1, 8)] == [(span.start, span.end) for span in layer]


def test_resolve_conflicts_MIN():    
    # empty span list
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [] == [(span.start, span.end) for span in layer]

    # one span
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  4, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # equal spans
    layer = Layer(name='test_layer', attributes=['_priority_'], ambiguous=True)
    layer = records_to_layer(layer, [[{'start': 1, 'end':  4, '_priority_': 0},
                                      {'start': 1, 'end':  4, '_priority_': 0}]])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert len(layer[0].annotations) == 1
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common start
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  4, '_priority_': 0},
                                     {'start': 1, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common end
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 3, 'end':  6, '_priority_': 0},
                                     {'start': 1, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]

    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 0},
                                     {'start': 2, 'end':  4, '_priority_': 0},
                                     {'start': 3, 'end':  6, '_priority_': 0} ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [(2, 4)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 1},
                                     {'start': 2, 'end':  4, '_priority_': 1},
                                     {'start': 3, 'end':  6, '_priority_': 0} ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN', priority_attribute='_priority_')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]


def test_resolve_conflicts_ALL():
    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 0},
                                     {'start': 2, 'end':  4, '_priority_': 0},
                                     {'start': 3, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL', priority_attribute='_priority_')
    assert [(1, 8), (2, 4), (3, 6)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  8, '_priority_': 1},
                                     {'start': 2, 'end':  4, '_priority_': 1},
                                     {'start': 3, 'end':  6, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL', priority_attribute='_priority_')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = records_to_layer(layer, [{'start': 1, 'end':  3, '_priority_': 2},
                                     {'start': 2, 'end':  7, '_priority_': 1},
                                     {'start': 4, 'end':  8, '_priority_': 0}])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL', priority_attribute='_priority_')
    assert [(1, 3), (4, 8)] == [(span.start, span.end) for span in layer]


def test_resolve_conflicts_ambiguous_layer():
    # keep_equal=True
    layer = Layer(name='test_layer', attributes=['attr_1', '_priority_'], ambiguous=True)
    layer = records_to_layer(layer, [ \
        [{'start': 1, 'end': 2, 'attr_1': 1, '_priority_': 0}],
        [{'start': 2, 'end': 3, 'attr_1': 1, '_priority_': 1},
         {'start': 2, 'end': 3, 'attr_1': 2, '_priority_': 2},
         {'start': 2, 'end': 3, 'attr_1': 3, '_priority_': 3},
         {'start': 2, 'end': 3, 'attr_1': 4, '_priority_': 4}],
        [{'start': 4, 'end': 5, 'attr_1': 1, '_priority_': 1},
         {'start': 4, 'end': 5, 'attr_1': 2, '_priority_': 1},
         {'start': 4, 'end': 5, 'attr_1': 3, '_priority_': 0},
         {'start': 4, 'end': 5, 'attr_1': 4, '_priority_': 0}],
        [{'start': 6, 'end': 7, 'attr_1': 1, '_priority_': 2},
         {'start': 6, 'end': 7, 'attr_1': 2, '_priority_': 1},
         {'start': 6, 'end': 7, 'attr_1': 3, '_priority_': 2},
         {'start': 6, 'end': 7, 'attr_1': 4, '_priority_': 3}],
    ])
    layer = resolve_conflicts(layer,
                              conflict_resolving_strategy='ALL',
                              priority_attribute='_priority_',
                              keep_equal=True)

    result = [(annotation.start, annotation.end) for span in layer for annotation in span.annotations]
    assert [(1, 2), (2, 3), (4, 5), (4, 5), (6, 7)] == result, result

    # keep_equal=False
    layer = Layer(name='test_layer', attributes=['attr_1', '_priority_'], ambiguous=True)
    layer = records_to_layer(layer, [ \
        [{'start': 1, 'end': 4, 'attr_1': 1, '_priority_': 0}],
        [{'start': 3, 'end': 6, 'attr_1': 1, '_priority_': 1},
         {'start': 3, 'end': 6, 'attr_1': 2, '_priority_': 2},
         {'start': 3, 'end': 6, 'attr_1': 3, '_priority_': 3},
         {'start': 3, 'end': 6, 'attr_1': 4, '_priority_': 4}],
        [{'start': 5, 'end': 7, 'attr_1': 1, '_priority_': 1},
         {'start': 5, 'end': 7, 'attr_1': 2, '_priority_': 1},
         {'start': 5, 'end': 7, 'attr_1': 3, '_priority_': 0},
         {'start': 5, 'end': 7, 'attr_1': 4, '_priority_': 0}],
    ])
    layer = resolve_conflicts(layer,
                              conflict_resolving_strategy='ALL',
                              priority_attribute='_priority_',
                              keep_equal=False)
    assert [(1, 4), (5, 7)] == [(annotation.start, annotation.end) for span in layer for annotation in span.annotations]
