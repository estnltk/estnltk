from estnltk import Text, Layer, ElementaryBaseSpan
from estnltk.layer_operations import merge_layers


def test_1():
    t = 'Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.'

    text_5 = Text(t)

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text_5, ambiguous=True)
    layer_1.add_annotation(ElementaryBaseSpan( 0,  4), attr='L1-0',  attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan( 5,  9),  attr='L1-1',  attr_1='KAKS')
    layer_1.add_annotation(ElementaryBaseSpan( 5, 16),  attr='L1-2',  attr_1='KAKS')
    layer_1.add_annotation(ElementaryBaseSpan( 5, 16),  attr='L1-2',  attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan( 5, 16),  attr='L1-2',  attr_1='KAKSKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan( 9, 14),  attr='L1-3',  attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(17, 21),  attr='L1-4',  attr_1='KOLM')
    layer_1.add_annotation(ElementaryBaseSpan(23, 27),  attr='L1-5',  attr_1='NELI')
    layer_1.add_annotation(ElementaryBaseSpan(28, 33),  attr='L1-6',  attr_1='TUHAT')
    layer_1.add_annotation(ElementaryBaseSpan(34, 38),  attr='L1-7',  attr_1='VIIS')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42),  attr='L1-8',  attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42),  attr='L1-8',  attr_1='VIIS')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42),  attr='L1-8',  attr_1='VIISSADA')
    layer_1.add_annotation(ElementaryBaseSpan(38, 42),  attr='L1-9',  attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan(43, 47),  attr='L1-10', attr_1='KUUS')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54),  attr='L1-11', attr_1='KUUS')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54),  attr='L1-11', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54),  attr='L1-11', attr_1='KUUSKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan(47, 52),  attr='L1-12', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(55, 61),  attr='L1-13', attr_1='SEITSE')
    layer_1.add_annotation(ElementaryBaseSpan(62, 66),  attr='L1-14', attr_1='KOMA')
    layer_1.add_annotation(ElementaryBaseSpan(67, 74),  attr='L1-15', attr_1='KAHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 82),  attr='L1-16', attr_1='ÜHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89),  attr='L1-17', attr_1='ÜHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89),  attr='L1-17', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89),  attr='L1-17', attr_1='ÜHEKSAKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan(82, 87),  attr='L1-18', attr_1='KÜMME')
    text_5['layer_1'] = layer_1

    layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_1')
    layer_5.add_annotation([layer_1[0], layer_1[1]],                attr='L5-0-0',  attr_5='SADA KAKS')
    layer_5.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-1',  attr_5='SADA KAKS')
    layer_5.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-2',  attr_5='SADA KÜMME')
    layer_5.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-3',  attr_5='SADA KAKSKÜMMEND')
    layer_5.add_annotation([layer_1[0], layer_1[2], layer_1[4]],    attr='L5-2-4',  attr_5='SADA KAKSKÜMMEND KOLM')
    layer_5.add_annotation([layer_1[5], layer_1[6]],                attr='L5-3-5',  attr_5='NELI TUHAT')
    layer_5.add_annotation([layer_1[7]],                            attr='L5-5-7',  attr_5='VIIS')
    layer_5.add_annotation([layer_1[6], layer_1[7]],                attr='L5-4-6',  attr_5='TUHAT VIIS')
    layer_5.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-8',  attr_5='VIISSADA KUUS')
    layer_5.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-9',  attr_5='VIISSADA KÜMME')
    layer_5.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-10', attr_5='VIISSADA KUUSKÜMMEND')
    layer_5.add_annotation([layer_1[12], layer_1[14], layer_1[15]], attr='L5-7-11', attr_5='KÜMME KOMA KAHEKSA')
    layer_5.add_annotation([layer_1[13], layer_1[14], layer_1[15]], attr='L5-8-12', attr_5='SEITSE KOMA KAHEKSA')
    text_5['layer_5'] = layer_5

    # use merge to copy layer_5
    layer_5_new = merge_layers(layers=[layer_5],
                               output_layer='layer_5_new',
                               output_attributes=['attr', 'attr_5'])

    assert layer_5_new.to_records() == [
        [[{'attr': 'L1-0', 'attr_1': 'SADA', 'start': 0, 'end': 4}],
         [{'attr': 'L1-1', 'attr_1': 'KAKS', 'start': 5, 'end': 9}]],
        [[{'attr': 'L1-0', 'attr_1': 'SADA', 'start': 0, 'end': 4}],
         [{'attr': 'L1-2', 'attr_1': 'KAKS', 'start': 5, 'end': 16},
          {'attr': 'L1-2', 'attr_1': 'KÜMME', 'start': 5, 'end': 16},
          {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND', 'start': 5, 'end': 16}]],
        [[{'attr': 'L1-0', 'attr_1': 'SADA', 'start': 0, 'end': 4}],
         [{'attr': 'L1-2', 'attr_1': 'KAKS', 'start': 5, 'end': 16},
          {'attr': 'L1-2', 'attr_1': 'KÜMME', 'start': 5, 'end': 16},
          {'attr': 'L1-2', 'attr_1': 'KAKSKÜMMEND', 'start': 5, 'end': 16}],
         [{'attr': 'L1-4', 'attr_1': 'KOLM', 'start': 17, 'end': 21}]],
        [[{'attr': 'L1-5', 'attr_1': 'NELI', 'start': 23, 'end': 27}],
         [{'attr': 'L1-6', 'attr_1': 'TUHAT', 'start': 28, 'end': 33}]],
        [[{'attr': 'L1-6', 'attr_1': 'TUHAT', 'start': 28, 'end': 33}],
         [{'attr': 'L1-7', 'attr_1': 'VIIS', 'start': 34, 'end': 38}]],
        [[{'attr': 'L1-7', 'attr_1': 'VIIS', 'start': 34, 'end': 38}]],
        [[{'attr': 'L1-8', 'attr_1': 'SADA', 'start': 34, 'end': 42},
          {'attr': 'L1-8', 'attr_1': 'VIIS', 'start': 34, 'end': 42},
          {'attr': 'L1-8', 'attr_1': 'VIISSADA', 'start': 34, 'end': 42}],
         [{'attr': 'L1-11', 'attr_1': 'KUUS', 'start': 43, 'end': 54},
          {'attr': 'L1-11', 'attr_1': 'KÜMME', 'start': 43, 'end': 54},
          {'attr': 'L1-11', 'attr_1': 'KUUSKÜMMEND', 'start': 43, 'end': 54}]],
        [[{'attr': 'L1-12', 'attr_1': 'KÜMME', 'start': 47, 'end': 52}],
         [{'attr': 'L1-14', 'attr_1': 'KOMA', 'start': 62, 'end': 66}],
         [{'attr': 'L1-15', 'attr_1': 'KAHEKSA', 'start': 67, 'end': 74}]],
        [[{'attr': 'L1-13', 'attr_1': 'SEITSE', 'start': 55, 'end': 61}],
         [{'attr': 'L1-14', 'attr_1': 'KOMA', 'start': 62, 'end': 66}],
         [{'attr': 'L1-15', 'attr_1': 'KAHEKSA', 'start': 67, 'end': 74}]]]
