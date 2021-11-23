#
#  Tests for legacy layer operations
#

from estnltk_core.tests import new_text
from estnltk_core.common import load_text_class
from estnltk_core.layer.layer import Layer, ElementaryBaseSpan
from estnltk_core.layer import AmbiguousAttributeTupleList
from estnltk_core.converters.layer_dict_converter import dict_to_layer

from estnltk_core.legacy.layer_operations import apply_filter
from estnltk_core.legacy.layer_operations import drop_annotations
from estnltk_core.legacy.layer_operations import keep_annotations
from estnltk_core.legacy.layer_operations import count_by
from estnltk_core.legacy.layer_operations import unique_texts


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

    layer = text_3['layer_1']

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
    drop_annotations(layer=text['layer_1'],
                     attribute='attr_1',
                     values={'A', 'D'}
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'B']], [['L1-1', 'C']], [['L1-2', 'E']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text['layer_1']['attr', 'attr_1'] == expected


def test_keep_annotations():
    # test attribute and values
    text = new_text(3)
    keep_annotations(layer=text['layer_1'],
                     attribute='attr_1',
                     values={'B', 'C', 'E', 'F'}
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'B']], [['L1-1', 'C']], [['L1-2', 'E']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text['layer_1']['attr', 'attr_1'] == expected

    # test preserve_spans=True
    text = new_text(3)
    keep_annotations(layer=text['layer_1'],
                     attribute='attr_1',
                     values={},
                     preserve_spans=True,
                     )
    expected = AmbiguousAttributeTupleList([[['L1-0', 'A']], [['L1-1', 'C']], [['L1-2', 'D']], [['L1-3', 'F']]],
                                           ('attr', 'attr_1'))
    assert text['layer_1']['attr', 'attr_1'] == expected


def test_layer_count_by():
    from estnltk_core import Layer, ElementaryBaseSpan
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

    counter = count_by( text_1['test'], 'label' )
    expected = {(1,): 1, (2,): 2, (3,): 1, (4,): 1}
    assert counter == expected
    counter = count_by( text_2['test'], ['label'], counter=counter)
    expected = {(1,): 2, (2,): 4, (3,): 2, (4,): 2}
    assert counter == expected

    counter = count_by( text_1['test'], ['text', 'label'] )
    expected = {('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 1, ('neli', 4): 1}
    assert counter == expected
    counter = count_by( text_2['test'], ['text', 'label'], counter=counter )
    expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 4, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
    assert counter == expected


def test_layer_unique_texts():
    from estnltk_core import Layer, ElementaryBaseSpan
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
