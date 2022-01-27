from estnltk_core import Layer, ElementaryBaseSpan
from estnltk_core.layer_operations import merge_layers
from estnltk_core.common import load_text_class
from estnltk_core.converters import layer_to_dict

def test_1():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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
    text_5.add_layer(layer_1)

    layer_5a = Layer('layer_5a', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_1')
    layer_5a.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-1',  attr_5='SADA KAKS')
    layer_5a.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-2',  attr_5='SADA KÜMME')
    layer_5a.add_annotation([layer_1[0], layer_1[2]],                attr='L5-1-3',  attr_5='SADA KAKSKÜMMEND')
    layer_5a.add_annotation([layer_1[0], layer_1[2], layer_1[4]],    attr='L5-2-4',  attr_5='SADA KAKSKÜMMEND KOLM')
    layer_5a.add_annotation([layer_1[5], layer_1[6]],                attr='L5-3-5',  attr_5='NELI TUHAT')
    layer_5a.add_annotation([layer_1[7]],                            attr='L5-5-7',  attr_5='VIIS')
    layer_5a.add_annotation([layer_1[13], layer_1[14], layer_1[15]], attr='L5-8-12', attr_5='SEITSE KOMA KAHEKSA')
    text_5.add_layer(layer_5a)

    layer_5b = Layer('layer_5b', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_1')
    layer_5b.add_annotation([layer_1[0], layer_1[1]],                attr='L5-0-0',  attr_5='SADA KAKS')
    layer_5b.add_annotation([layer_1[6], layer_1[7]],                attr='L5-4-6',  attr_5='TUHAT VIIS')
    layer_5b.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-8',  attr_5='VIISSADA KUUS')
    layer_5b.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-9',  attr_5='VIISSADA KÜMME')
    layer_5b.add_annotation([layer_1[8], layer_1[11]],               attr='L5-6-10', attr_5='VIISSADA KUUSKÜMMEND')
    layer_5b.add_annotation([layer_1[12], layer_1[14], layer_1[15]], attr='L5-7-11', attr_5='KÜMME KOMA KAHEKSA')
    text_5.add_layer(layer_5b)

    # merge layer_5a and layer_5b
    layer_5_new = merge_layers(layers=[layer_5a, layer_5b],
                               output_layer='layer_5_new',
                               output_attributes=['attr', 'attr_5'])

    assert layer_to_dict( layer_5_new ) == \
        {'ambiguous': True,
         'attributes': ('attr', 'attr_5'),
         'secondary_attributes': (),
         'enveloping': 'layer_1',
         'meta': {},
         'name': 'layer_5_new',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'attr': 'L5-0-0', 'attr_5': 'SADA KAKS'}],
                    'base_span': ((0, 4), (5, 9))},
                   {'annotations': [{'attr': 'L5-1-1', 'attr_5': 'SADA KAKS'},
                                    {'attr': 'L5-1-2', 'attr_5': 'SADA KÜMME'},
                                    {'attr': 'L5-1-3', 'attr_5': 'SADA KAKSKÜMMEND'}],
                    'base_span': ((0, 4), (5, 16))},
                   {'annotations': [{'attr': 'L5-2-4', 
                                     'attr_5': 'SADA KAKSKÜMMEND KOLM'}],
                    'base_span': ((0, 4), (5, 16), (17, 21))},
                   {'annotations': [{'attr': 'L5-3-5', 'attr_5': 'NELI TUHAT'}],
                    'base_span': ((23, 27), (28, 33))},
                   {'annotations': [{'attr': 'L5-4-6', 'attr_5': 'TUHAT VIIS'}],
                    'base_span': ((28, 33), (34, 38))},
                   {'annotations': [{'attr': 'L5-5-7', 'attr_5': 'VIIS'}],
                    'base_span': ((34, 38),)},
                   {'annotations': [{'attr': 'L5-6-8', 'attr_5': 'VIISSADA KUUS'},
                                    {'attr': 'L5-6-9', 'attr_5': 'VIISSADA KÜMME'},
                                    {'attr': 'L5-6-10',
                                     'attr_5': 'VIISSADA KUUSKÜMMEND'}],
                    'base_span': ((34, 42), (43, 54))},
                   {'annotations': [{'attr': 'L5-7-11',
                                     'attr_5': 'KÜMME KOMA KAHEKSA'}],
                    'base_span': ((47, 52), (62, 66), (67, 74))},
                   {'annotations': [{'attr': 'L5-8-12',
                                     'attr_5': 'SEITSE KOMA KAHEKSA'}],
                    'base_span': ((55, 61), (62, 66), (67, 74))}]}

