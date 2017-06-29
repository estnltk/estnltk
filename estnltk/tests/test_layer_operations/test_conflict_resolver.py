from estnltk.text import Layer
from estnltk.layer_operations import resolve_conflicts

def test_resolve_conflicts_MAX():    
    # empty span list
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [] == [(span.start, span.end) for span in layer]

    # one span
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # equal spans
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                                {'start': 1, 'end':  4, '_priority_': 0},
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common start
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                                {'start': 1, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(1, 6)] == [(span.start, span.end) for span in layer]

    # common end
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 3, 'end':  6, '_priority_': 0},
                                {'start': 1, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(1, 6)] == [(span.start, span.end) for span in layer]

    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 0},
                                {'start': 2, 'end':  4, '_priority_': 0},
                                {'start': 3, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(1, 8)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 1},
                                {'start': 2, 'end':  4, '_priority_': 0},
                                {'start': 3, 'end':  6, '_priority_': 1}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MAX')
    assert [(2, 4)] == [(span.start, span.end) for span in layer]


def test_resolve_conflicts_MIN():    
    # empty span list
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [] == [(span.start, span.end) for span in layer]

    # one span
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # equal spans
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                                {'start': 1, 'end':  4, '_priority_': 0},
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common start
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  4, '_priority_': 0},
                                {'start': 1, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(1, 4)] == [(span.start, span.end) for span in layer]

    # common end
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 3, 'end':  6, '_priority_': 0},
                                {'start': 1, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]

    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 0},
                                {'start': 2, 'end':  4, '_priority_': 0},
                                {'start': 3, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(2, 4)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 1},
                                {'start': 2, 'end':  4, '_priority_': 1},
                                {'start': 3, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='MIN')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]

def test_resolve_conflicts_ALL():
    # complex
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 0},
                                {'start': 2, 'end':  4, '_priority_': 0},
                                {'start': 3, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL')
    assert [(1, 8), (2, 4), (3, 6)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  8, '_priority_': 1},
                                {'start': 2, 'end':  4, '_priority_': 1},
                                {'start': 3, 'end':  6, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL')
    assert [(3, 6)] == [(span.start, span.end) for span in layer]

    # complex, different priorities
    layer = Layer(name='test_layer', attributes=['_priority_'])
    layer = layer.from_records([{'start': 1, 'end':  3, '_priority_': 2},
                                {'start': 2, 'end':  7, '_priority_': 1},
                                {'start': 4, 'end':  8, '_priority_': 0}
                               ])
    layer = resolve_conflicts(layer, conflict_resolving_strategy='ALL')
    assert [(1, 3), (4, 8)] == [(span.start, span.end) for span in layer]
