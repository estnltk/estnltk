from estnltk import Layer, Text
from estnltk.taggers import DiffTagger
from estnltk.taggers.system.diff_tagger import iterate_modified
from estnltk.taggers.system.diff_tagger import iterate_missing
from estnltk.taggers.system.diff_tagger import iterate_extra
from estnltk.taggers.system.diff_tagger import iterate_diff_conflicts
from estnltk.taggers.system.diff_tagger import iterate_overlapped
from estnltk.taggers.system.diff_tagger import iterate_prolonged
from estnltk.taggers.system.diff_tagger import iterate_shortened

from estnltk.converters import layer_to_dict

def test_diff_tagger_init():
    def fun(x, y):
        return x == y

    tagger = DiffTagger(layer_a='first_layer',
                        layer_b='second_layer',
                        output_layer='diff_first_second',
                        output_attributes=['attr', 'name_of_input_layer', 'attr_5'],
                        compare_function=fun,
                        input_layer_attribute='name_of_input_layer',
                        span_status_attribute='span_status_attribute_name')
    assert tagger.input_layer_attribute == 'name_of_input_layer'
    assert tagger.span_status_attribute == 'span_status_attribute_name'
    assert tagger.compare_function == fun
    assert tagger.output_attributes == ('span_status_attribute_name', 'attr', 'name_of_input_layer', 'attr_5')


def test_simple_ambiguous():
    text_5 = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text_5, ambiguous=True)
    layer_1.add_annotation((0, 4), attr='L1-0', attr_1='SADA')
    layer_1.add_annotation((5, 9), attr='L1-1', attr_1='KAKS')
    layer_1.add_annotation((5, 16), attr='L1-2', attr_1='KAKS')
    layer_1.add_annotation((5, 16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_1.add_annotation((17, 21), attr='L1-5', attr_1='KOLM')

    layer_2 = Layer('layer_2', attributes=['attr', 'attr_1'], text_object=text_5, ambiguous=True)
    layer_2.add_annotation((5, 16), attr='L1-2', attr_1='KAKS')
    layer_2.add_annotation((5, 16), attr='L1-2', attr_1='KÜMME')
    layer_2.add_annotation((5, 16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_2.add_annotation((5, 21), attr='L1-3', attr_1='KAKSKÜMMEND KOLM')
    layer_2.add_annotation((9, 14), attr='L1-4', attr_1='KÜMME')
    layer_2.add_annotation((17, 21), attr='L1-5', attr_1='KOLM')

    diff_tagger = DiffTagger(layer_a='layer_1',
                             layer_b='layer_2',
                             output_layer='diff_1_2',
                             output_attributes=('attr', 'attr_1'))

    diff_layer = diff_tagger.make_layer(text=text_5, layers={'layer_1': layer_1, 'layer_2': layer_2})

    assert layer_to_dict( diff_layer ) == {
        'name': 'diff_1_2',
        'attributes': ('span_status', 'input_layer_name', 'attr', 'attr_1'),
        'secondary_attributes': (),
        'parent': None,
        'enveloping': None,
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {'modified_spans': 1,
                 'missing_spans': 2,
                 'extra_spans': 2,
                 'extra_annotations': 3,
                 'missing_annotations': 2,
                 'overlapped': 0,
                 'prolonged': 1,
                 'shortened': 0,
                 'conflicts': 1,
                 'unchanged_spans': 1,
                 'unchanged_annotations': 3},
        'spans': [{'base_span': (0, 4),
                   'annotations': [{'attr': 'L1-0',
                                    'input_layer_name': 'layer_1',
                                    'attr_1': 'SADA',
                                    'span_status': 'missing'}]},
                  {'base_span': (5, 9),
                   'annotations': [{'attr': 'L1-1',
                                    'input_layer_name': 'layer_1',
                                    'attr_1': 'KAKS',
                                    'span_status': 'missing'}]},
                  {'base_span': (5, 16),
                   'annotations': [{'attr': 'L1-2',
                                    'input_layer_name': 'layer_2',
                                    'attr_1': 'KÜMME',
                                    'span_status': 'modified'}]},
                  {'base_span': (5, 21),
                   'annotations': [{'attr': 'L1-3',
                                    'input_layer_name': 'layer_2',
                                    'attr_1': 'KAKSKÜMMEND KOLM',
                                    'span_status': 'extra'}]},
                  {'base_span': (9, 14),
                   'annotations': [{'attr': 'L1-4',
                                    'input_layer_name': 'layer_2',
                                    'attr_1': 'KÜMME',
                                    'span_status': 'extra'}]}
                  ]}


def test_enveloping_not_ambiguous():
    text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')

    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
    layer_0.add_annotation((0, 4), attr='L0-0', attr_0='100')
    layer_0.add_annotation((5, 9), attr='L0-1', attr_0='2')
    layer_0.add_annotation((5, 16), attr='L0-2', attr_0='20')
    layer_0.add_annotation((9, 14), attr='L0-3', attr_0='10')
    layer_0.add_annotation((17, 21), attr='L0-4', attr_0='3')
    layer_0.add_annotation((23, 27), attr='L0-5', attr_0='4')
    layer_0.add_annotation((28, 33), attr='L0-6', attr_0='1000')
    layer_0.add_annotation((34, 38), attr='L0-7', attr_0='5')
    layer_0.add_annotation((34, 42), attr='L0-8', attr_0='500')
    layer_0.add_annotation((38, 42), attr='L0-9', attr_0='100')
    layer_0.add_annotation((43, 47), attr='L0-10', attr_0='6')
    layer_0.add_annotation((43, 54), attr='L0-11', attr_0='60')
    layer_0.add_annotation((47, 52), attr='L0-12', attr_0='10')
    layer_0.add_annotation((55, 61), attr='L0-13', attr_0='7')
    layer_0.add_annotation((62, 66), attr='L0-14', attr_0=',')
    layer_0.add_annotation((67, 74), attr='L0-15', attr_0='8')
    layer_0.add_annotation((76, 82), attr='L0-16', attr_0='9')
    layer_0.add_annotation((76, 89), attr='L0-17', attr_0='90')
    layer_0.add_annotation((82, 87), attr='L0-18', attr_0='10')
    layer_0.add_annotation((90, 95), attr='L0-19', attr_0='1000')

    layer_a = Layer('layer_a', attributes=['attr', 'attr_4'], text_object=text, ambiguous=False, enveloping='layer_0')

    layer_a.add_annotation([layer_0[0], layer_0[2], layer_0[4]], attr='L4-0', attr_4='123')
    layer_a.add_annotation([layer_0[15]], attr='L4-2', attr_4='8')
    layer_a.add_annotation([layer_0[14]], attr='L4-3', attr_4=',')

    layer_b = Layer('layer_b', attributes=['attr', 'attr_4'], text_object=text, ambiguous=False, enveloping='layer_0')

    layer_b.add_annotation([layer_0[0], layer_0[2], layer_0[4]], attr='L4-0', attr_4='123')
    layer_b.add_annotation([layer_0[5], layer_0[6], layer_0[8], layer_0[11], layer_0[13]], attr='L4-1', attr_4='4567')
    layer_b.add_annotation([layer_0[14]], attr='modified', attr_4=',')
    layer_b.add_annotation([layer_0[17], layer_0[19]], attr='L4-4', attr_4='90 000')

    diff_tagger = DiffTagger(layer_a='layer_a',
                             layer_b='layer_b',
                             output_layer='diff_layer',
                             output_attributes=('span_status', 'attr', 'attr_4'),
                             span_status_attribute='span_status')

    diff_layer = diff_tagger.make_layer(text, layers={'layer_a': layer_a, 'layer_b': layer_b})

    assert layer_to_dict( diff_layer ) == {
        'name': 'diff_layer',
        'attributes': ('input_layer_name', 'span_status', 'attr', 'attr_4'),
        'secondary_attributes': (),
        'parent': None,
        'enveloping': 'layer_0',
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {'modified_spans': 1,
                 'missing_spans': 1,
                 'extra_spans': 2,
                 'extra_annotations': 3,
                 'missing_annotations': 2,
                 'overlapped': 0,
                 'prolonged': 0,
                 'shortened': 0,
                 'conflicts': 0,
                 'unchanged_spans': 1,
                 'unchanged_annotations': 1},
        'spans': [{'base_span': ((23, 27), (28, 33), (34, 42), (43, 54), (55, 61)),
                   'annotations': [{'attr': 'L4-1',
                                    'attr_4': '4567',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'}]},
                  {'base_span': ((62, 66),),
                   'annotations': [{'attr': 'L4-3',
                                    'attr_4': ',',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'modified'},
                                   {'attr': 'modified',
                                    'attr_4': ',',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'modified'}]},
                  {'base_span': ((67, 74),),
                   'annotations': [{'attr': 'L4-2',
                                    'attr_4': '8',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'missing'}]},
                  {'base_span': ((76, 89), (90, 95)),
                   'annotations': [{'attr': 'L4-4',
                                    'attr_4': '90 000',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'}]}]}


def test_iterators_on_enveloping_ambiguous_diff_layer():
    diff_tagger = DiffTagger(layer_a='layer_a',
                             layer_b='layer_b',
                             output_layer='diff_layer',
                             output_attributes=('span_status', 'attr', 'attr_5'),
                             span_status_attribute='span_status')

    text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text, ambiguous=True)
    layer_1.add_annotation((0, 4), attr='L1-0', attr_1='SADA')
    layer_1.add_annotation((5, 9), attr='L1-1', attr_1='KAKS')
    layer_1.add_annotation((5, 16), attr='L1-2', attr_1='KAKS')
    layer_1.add_annotation((5, 16), attr='L1-2', attr_1='KÜMME')
    layer_1.add_annotation((5, 16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_1.add_annotation((9, 14), attr='L1-3', attr_1='KÜMME')
    layer_1.add_annotation((17, 21), attr='L1-4', attr_1='KOLM')
    layer_1.add_annotation((23, 27), attr='L1-5', attr_1='NELI')
    layer_1.add_annotation((28, 33), attr='L1-6', attr_1='TUHAT')
    layer_1.add_annotation((34, 38), attr='L1-7', attr_1='VIIS')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='SADA')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='VIIS')
    layer_1.add_annotation((34, 42), attr='L1-8', attr_1='VIISSADA')
    layer_1.add_annotation((38, 42), attr='L1-9', attr_1='SADA')
    layer_1.add_annotation((43, 47), attr='L1-10', attr_1='KUUS')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KUUS')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KÜMME')
    layer_1.add_annotation((43, 54), attr='L1-11', attr_1='KUUSKÜMMEND')
    layer_1.add_annotation((47, 52), attr='L1-12', attr_1='KÜMME')
    layer_1.add_annotation((55, 61), attr='L1-13', attr_1='SEITSE')
    layer_1.add_annotation((62, 66), attr='L1-14', attr_1='KOMA')
    layer_1.add_annotation((67, 74), attr='L1-15', attr_1='KAHEKSA')
    layer_1.add_annotation((76, 82), attr='L1-16', attr_1='ÜHEKSA')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='ÜHEKSA')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='KÜMME')
    layer_1.add_annotation((76, 89), attr='L1-17', attr_1='ÜHEKSAKÜMMEND')
    layer_1.add_annotation((82, 87), attr='L1-18', attr_1='KÜMME')

    layer_a = Layer('layer_a', attributes=['attr', 'attr_5'], text_object=text, ambiguous=True, enveloping='layer_1')

    layer_a.add_annotation([layer_1[0], layer_1[1]], attr='L5-0-0', attr_5='SADA KAKS')
    layer_a.add_annotation([layer_1[0], layer_1[2], layer_1[4]], attr='L5-2-4', attr_5='SADA KAKSKÜMMEND KOLM')
    layer_a.add_annotation([layer_1[5], layer_1[6]], attr='L5-3-5', attr_5='NELI TUHAT')
    layer_a.add_annotation([layer_1[7]], attr='L5-5-7', attr_5='VIIS')
    layer_a.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-8', attr_5='VIISSADA KUUS')
    layer_a.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-9', attr_5='VIISSADA KÜMME')
    layer_a.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-10', attr_5='VIISSADA KUUSKÜMMEND')
    layer_a.add_annotation([layer_1[12], layer_1[14], layer_1[15]], attr='L5-7-11', attr_5='KÜMME KOMA KAHEKSA')
    layer_a.add_annotation([layer_1[13], layer_1[14], layer_1[15]], attr='L5-8-12', attr_5='seitse koma kaheksa')

    layer_b = Layer('layer_b', attributes=['attr', 'attr_5'], text_object=text, ambiguous=True, enveloping='layer_1')

    layer_b.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-1', attr_5='SADA KAKS')
    layer_b.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-2', attr_5='SADA KÜMME')
    layer_b.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-3', attr_5='SADA KAKSKÜMMEND')
    layer_b.add_annotation([layer_1[6], layer_1[7]], attr='L5-4-6', attr_5='TUHAT VIIS')
    layer_b.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-10', attr_5='VIISSADA KUUSKÜMMEND')
    layer_b.add_annotation([layer_1[12], layer_1[14], layer_1[15]], attr='L5-7-11', attr_5='KÜMME KOMA KAHEKSA')
    layer_b.add_annotation([layer_1[13], layer_1[14], layer_1[15]], attr='L5-8-12', attr_5='SEITSE KOMA KAHEKSA')

    diff_layer = diff_tagger.make_layer(text, layers={'layer_a': layer_a, 'layer_b': layer_b})

    assert layer_to_dict( diff_layer ) == {
        'name': 'diff_layer',
        'attributes': ('input_layer_name', 'span_status', 'attr', 'attr_5'),
        'secondary_attributes': (),
        'parent': None,
        'enveloping': 'layer_1',
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {'modified_spans': 2,
                 'missing_spans': 4,
                 'extra_spans': 2,
                 'extra_annotations': 5,
                 'missing_annotations': 7,
                 'overlapped': 1,
                 'prolonged': 2,
                 'shortened': 1,
                 'conflicts': 4,
                 'unchanged_spans': 1,
                 'unchanged_annotations': 2},
        'spans': [{'base_span': ((0, 4), (5, 9)),
                   'annotations': [{'attr_5': 'SADA KAKS',
                                    'attr': 'L5-0-0',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'missing'}]},
                  {'base_span': ((0, 4), (5, 16)),
                   'annotations': [{'attr_5': 'SADA KAKS',
                                    'attr': 'L5-1-1',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'},
                                   {'attr_5': 'SADA KÜMME',
                                    'attr': 'L5-1-2',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'},
                                   {'attr_5': 'SADA KAKSKÜMMEND',
                                    'attr': 'L5-1-3',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'}]},
                  {'base_span': ((0, 4), (5, 16), (17, 21)),
                   'annotations': [{'attr_5': 'SADA KAKSKÜMMEND KOLM',
                                    'attr': 'L5-2-4',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'missing'}]},
                  {'base_span': ((23, 27), (28, 33)),
                   'annotations': [{'attr_5': 'NELI TUHAT',
                                    'attr': 'L5-3-5',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'missing'}]},
                  {'base_span': ((28, 33), (34, 38)),
                   'annotations': [{'attr_5': 'TUHAT VIIS',
                                    'attr': 'L5-4-6',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'extra'}]},
                  {'base_span': ((34, 38),),
                   'annotations': [{'attr_5': 'VIIS',
                                    'attr': 'L5-5-7',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'missing'}]},
                  {'base_span': ((34, 42), (43, 54)),
                   'annotations': [{'attr_5': 'VIISSADA KUUS',
                                    'attr': 'L5-6-8',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'modified'},
                                   {'attr_5': 'VIISSADA KÜMME',
                                    'attr': 'L5-6-9',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'modified'}]},
                  {'base_span': ((55, 61), (62, 66), (67, 74)),
                   'annotations': [{'attr_5': 'seitse koma kaheksa',
                                    'attr': 'L5-8-12',
                                    'input_layer_name': 'layer_a',
                                    'span_status': 'modified'},
                                   {'attr_5': 'SEITSE KOMA KAHEKSA',
                                    'attr': 'L5-8-12',
                                    'input_layer_name': 'layer_b',
                                    'span_status': 'modified'}]}]}

    assert list(iterate_modified(diff_layer, span_status_attribute='span_status')) == [diff_layer[6], diff_layer[7]]

    assert list(iterate_missing(diff_layer, span_status_attribute='span_status')) == [diff_layer[0], diff_layer[2],
                                                                                      diff_layer[3], diff_layer[5]]

    assert list(iterate_extra(diff_layer, span_status_attribute='span_status')) == [diff_layer[1], diff_layer[4]]

    assert list(iterate_diff_conflicts(diff_layer, span_status_attribute='span_status')) == [
        (diff_layer[0], diff_layer[1]),
        (diff_layer[2], diff_layer[1]),
        (diff_layer[3], diff_layer[4]),
        (diff_layer[5], diff_layer[4])
    ]

    assert list(iterate_overlapped(diff_layer, span_status_attribute='span_status')) == [
        (diff_layer[3], diff_layer[4])]

    assert list(iterate_prolonged(diff_layer, span_status_attribute='span_status')) == [
        (diff_layer[0], diff_layer[1]),
        (diff_layer[5], diff_layer[4])
    ]

    assert list(iterate_shortened(diff_layer, span_status_attribute='span_status')) == [
        (diff_layer[2], diff_layer[1]),
    ]
