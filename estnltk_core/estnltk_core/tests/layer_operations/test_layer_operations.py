from estnltk_core import Layer, ElementaryBaseSpan

from estnltk_core.layer import AmbiguousAttributeTupleList
from estnltk_core.tests import new_text
from estnltk_core.converters.layer_dict_converter import dict_to_layer

from estnltk_core.layer_operations import apply_filter
from estnltk_core.layer_operations import drop_annotations
from estnltk_core.layer_operations import keep_annotations
from estnltk_core.layer_operations import diff_layer
from estnltk_core.layer_operations import unique_texts

from estnltk_core.common import load_text_class

def test_apply_filter():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    def filter_function(layer, i, j):
        return layer[i].annotations[j].attr_1 in {'B', 'C', 'E', 'F'}

    text_3 = Text('Tere, maailm!')

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text_3, ambiguous=True)
    layer_1.add_annotation(ElementaryBaseSpan(0, 4), attr='L1-0', attr_1='A')
    layer_1.add_annotation(ElementaryBaseSpan(0, 4), attr='L1-0', attr_1='B')
    layer_1.add_annotation(ElementaryBaseSpan(4, 5), attr='L1-1', attr_1='C')
    layer_1.add_annotation(ElementaryBaseSpan(6, 12), attr='L1-2', attr_1='D')
    layer_1.add_annotation(ElementaryBaseSpan(6, 12), attr='L1-2', attr_1='E')
    layer_1.add_annotation(ElementaryBaseSpan(12, 13), attr='L1-3', attr_1='F')
    text_3.add_layer(layer_1)

    layer = text_3.layer_1

    apply_filter(layer=layer,
                 function=filter_function,
                 preserve_spans=False,
                 drop_immediately=False
                 )
    expected = {
        'name': 'layer_1',
        'attributes': ('attr', 'attr_1'),
        'parent': None,
        'enveloping': None,
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {},
        'spans': [{'base_span': (0, 4),
                   'annotations': [{'attr_1': 'B', 'attr': 'L1-0'}]},
                  {'base_span': (4, 5), 'annotations': [{'attr_1': 'C', 'attr': 'L1-1'}]},
                  {'base_span': (6, 12), 'annotations': [{'attr_1': 'E', 'attr': 'L1-2'}]},
                  {'base_span': (12, 13), 'annotations': [{'attr_1': 'F', 'attr': 'L1-3'}]}]}
    expected = dict_to_layer(expected)
    assert expected == layer


def test_drop_annotations():
    text = new_text(3)
    drop_annotations(layer=text.layer_1,
                     attribute='attr_1',
                     values={'A', 'D'}
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'B']], [['L1-1', 'C']], [['L1-2', 'E']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text.layer_1['attr', 'attr_1'] == expected


def test_keep_annotations():
    # test attribute and values
    text = new_text(3)
    keep_annotations(layer=text.layer_1,
                     attribute='attr_1',
                     values={'B', 'C', 'E', 'F'}
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'B']], [['L1-1', 'C']], [['L1-2', 'E']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text.layer_1['attr', 'attr_1'] == expected

    # test preserve_spans=True
    text = new_text(3)
    keep_annotations(layer=text.layer_1,
                     attribute='attr_1',
                     values={},
                     preserve_spans=True,
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'A']], [['L1-1', 'C']], [['L1-2', 'D']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text.layer_1['attr', 'attr_1'] == expected


def test_layer_unique_texts():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Üks kaks kolm neli. Neli kolm kaks üks.')
    layer_1 = Layer('words', attributes=[], text_object=text, ambiguous=False)
    layer_1.add_annotation( ElementaryBaseSpan(0, 3) )
    layer_1.add_annotation( ElementaryBaseSpan(4, 8) )
    layer_1.add_annotation( ElementaryBaseSpan(9, 13) )
    layer_1.add_annotation( ElementaryBaseSpan(14, 18) )
    layer_1.add_annotation( ElementaryBaseSpan(18, 19) )
    layer_1.add_annotation( ElementaryBaseSpan(20, 24) )
    layer_1.add_annotation( ElementaryBaseSpan(25, 29) )
    layer_1.add_annotation( ElementaryBaseSpan(30, 34) )
    layer_1.add_annotation( ElementaryBaseSpan(35, 38) )
    layer_1.add_annotation( ElementaryBaseSpan(38, 39) )
    text.add_layer( layer_1 )
    
    result = unique_texts( text['words'], order=None )
    expected = {'.', 'kaks', 'kolm', 'neli', 'Neli', 'üks', 'Üks'}
    assert set(result) == expected

    text = Text('Üks kaks kolm neli.')
    layer_2 = Layer('words', attributes=[], text_object=text, ambiguous=False)
    layer_2.add_annotation( ElementaryBaseSpan(0, 3) )
    layer_2.add_annotation( ElementaryBaseSpan(4, 8) )
    layer_2.add_annotation( ElementaryBaseSpan(9, 13) )
    layer_2.add_annotation( ElementaryBaseSpan(14, 18) )
    layer_2.add_annotation( ElementaryBaseSpan(18, 19) )
    text.add_layer( layer_2 )

    result = unique_texts( text['words'], order='asc' )
    expected = ['.', 'kaks', 'kolm', 'neli', 'Üks']
    assert result == expected

    result = unique_texts( text['words'], order='desc' )
    expected = ['Üks', 'neli', 'kolm', 'kaks', '.']
    assert result, expected


def test_layer_groupby_attributes():
    text   = new_text( 5 )
    groups = text.layer_1.groupby(['attr_1'], return_type='spans')
    assert groups.count == {('SADA',): 3, \
                            ('KAKS',): 2,
                            ('KAKSKÜMMEND',): 1,
                            ('KÜMME',): 6,
                            ('KOLM',): 1,
                            ('NELI',): 1,
                            ('TUHAT',): 1,
                            ('VIIS',): 2,
                            ('VIISSADA',): 1,
                            ('KUUS',): 2,
                            ('KUUSKÜMMEND',): 1,
                            ('SEITSE',): 1,
                            ('KOMA',): 1,
                            ('KAHEKSA',): 1,
                            ('ÜHEKSA',): 2,
                            ('ÜHEKSAKÜMMEND',): 1}
    assert groups.groups[ ('KAHEKSA',) ] == [ text.layer_1[15] ]
    assert groups.groups[ ('KAKS',) ] == [ text.layer_1[1], text.layer_1[2] ]
    assert groups.groups[ ('KAKSKÜMMEND',) ] == [ text.layer_1[2] ]


def test_layer_groupby_text():
    # Case 1
    text   = new_text( 5 )
    groups = text.layer_1.groupby(['text'], return_type='spans')
    assert groups.count == { ('Sada',): 1,
                             ('kaheksa',): 1,
                             ('kaks',): 1,
                             ('kakskümmend',): 1,
                             ('kolm',): 1,
                             ('Neli',): 1,
                             ('koma',): 1,
                             ('kuus',): 1,
                             ('kuuskümmend',): 1,
                             ('kümme',): 3,
                             ('sada',): 1,
                             ('seitse',): 1,
                             ('tuhat',): 1,
                             ('viis',): 1,
                             ('viissada',): 1,
                             ('Üheksa',): 1,
                             ('Üheksakümmend',): 1 }
    assert groups.groups[ ('neli',) ] == []
    assert groups.groups[ ('viis',) ] == [ text.layer_1[7] ]
    assert groups.groups[ ('sada',) ] == [ text.layer_1[9] ]
    assert groups.groups[ ('kümme',) ] == [ text.layer_1[3], text.layer_1[12], text.layer_1[18] ]

    # Case 2:
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text_1 = Text('Üks kaks kolm neli kaks.')
    layer_1 = Layer('test', attributes=['label'], text_object=text_1, ambiguous=True)
    layer_1.add_annotation( ElementaryBaseSpan(0, 3), label=1 )
    layer_1.add_annotation( ElementaryBaseSpan(4, 8), label=2 )
    layer_1.add_annotation( ElementaryBaseSpan(9, 13), label=3 )
    layer_1.add_annotation( ElementaryBaseSpan(14, 18), label=4 )
    layer_1.add_annotation( ElementaryBaseSpan(19, 23), label=2 )
    text_1.add_layer( layer_1 )
    
    text_2 = Text('Neli kolm kaks üks kaks.')
    layer_2 = Layer('test', attributes=['label'], text_object=text_2, ambiguous=False)
    layer_2.add_annotation( ElementaryBaseSpan(0, 4), label=4 )
    layer_2.add_annotation( ElementaryBaseSpan(5, 9), label=3 )
    layer_2.add_annotation( ElementaryBaseSpan(10, 14), label=2 )
    layer_2.add_annotation( ElementaryBaseSpan(15, 18), label=1 )
    layer_2.add_annotation( ElementaryBaseSpan(19, 23), label=2 )
    text_2.add_layer( layer_2 )

    counter1 = text_1['test'].groupby( ['text', 'label'], return_type='annotations' )
    expected = {('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 1, ('neli', 4): 1}
    assert counter1.count == expected
    counter2 = text_2['test'].groupby( ['text', 'label'], return_type='annotations' )
    merged_counts = counter2.count
    for k,v in counter1.count.items():
        if k not in merged_counts.keys():
            merged_counts[k] = v
        else:
            merged_counts[k] += v
    expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 4, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
    assert merged_counts == expected


def test_layer_groupby_enveloping_layer():
    # Get a grouping of spans
    text = new_text( 5 )
    assert text.layer_4.enveloping == text.layer_0.name
    grouped_spanlist_texts = []
    for (env_layer_id, list_of_spans) in text.layer_0.groupby( text.layer_4 ):
        grouped_spanlist_texts.append( [sp.text for sp in list_of_spans] )
    assert grouped_spanlist_texts == [ \
       ['Sada', 'kakskümmend', 'kolm'],
       [' Neli', 'tuhat', 'viissada', 'kuuskümmend', 'seitse'],
       ['koma'],
       ['kaheksa'],
       ['Üheksakümmend', 'tuhat']
    ]
    # Get a grouping of spans' annotations
    grouped_annotations_1 = []
    for (env_layer_id, list_of_annotations) in text.layer_0.groupby( text.layer_4, return_type='annotations' ):
        grouped_annotations_1.append( [] )
        for ann in list_of_annotations:
            ann_dict = {}
            for attr in text.layer_0.attributes:
                ann_dict[attr] = ann[attr]
            grouped_annotations_1[-1].append( ann_dict )
    assert grouped_annotations_1 == [ \
       [ {'attr': 'L0-0', 'attr_0': '100'},
         {'attr': 'L0-2', 'attr_0': '20'},
         {'attr': 'L0-4', 'attr_0': '3'} ],
       [ {'attr': 'L0-5', 'attr_0': '4'},
         {'attr': 'L0-6', 'attr_0': '1000'},
         {'attr': 'L0-8', 'attr_0': '500'},
         {'attr': 'L0-11', 'attr_0': '60'},
         {'attr': 'L0-13', 'attr_0': '7'} ],
       [ {'attr': 'L0-14', 'attr_0': ','} ],
       [ {'attr': 'L0-15', 'attr_0': '8'} ],
       [ {'attr': 'L0-17', 'attr_0': '90'},
         {'attr': 'L0-19', 'attr_0': '1000'} ]
    ]


def test_diff_layer():
    layer_1 = Layer('layer_1')
    layer_2 = Layer('layer_2')
    result = list(diff_layer(layer_1, layer_2))
    expected = []
    assert result == expected

    layer_1 = Layer('layer_1')
    layer_1.add_annotation(ElementaryBaseSpan(0, 3))
    layer_2 = Layer('layer_2')
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], None)]
    assert result == expected

    layer_1 = Layer('layer_1')
    layer_1.add_annotation((0, 3))
    layer_1.add_annotation((6, 9))
    layer_1.add_annotation((12, 15))
    layer_1.add_annotation((18, 21))
    layer_2 = Layer('layer_2')
    layer_2.add_annotation((1, 3))
    layer_2.add_annotation((6, 9))
    layer_2.add_annotation((12, 15))
    layer_2.add_annotation((18, 20))
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], None),
                (None, layer_2[0]),
                (None, layer_2[3]),
                (layer_1[3], None)]
    assert result == expected

    layer_1 = Layer('layer_1', attributes=['label'])
    layer_1.add_annotation((0, 3), label=1)
    layer_2 = Layer('layer_2', attributes=['label'])
    layer_2.add_annotation((0, 3), label=2)
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], layer_2[0])]
    assert result == expected

    def fun(x, y):
        return True

    layer_1 = Layer('layer_1', attributes=['label'])
    layer_1.add_annotation((0, 3), label=1)
    layer_1.add_annotation((5, 7), label=1)
    layer_2 = Layer('layer_2', attributes=['label'])
    layer_2.add_annotation((0, 3), label=2)
    layer_2.add_annotation((6, 7), label=1)
    result = list(diff_layer(layer_1, layer_2, fun))
    expected = [(layer_1[1], None),
                (None, layer_2[1])]
    assert result == expected



