import pytest

import re
from copy import copy, deepcopy

from estnltk_core import ElementaryBaseSpan
from estnltk_core import RelationLayer, Relation

from estnltk_core.common import load_text_class
from estnltk_core.converters import dict_to_layer, layer_to_dict


def test_relation_layer_basic():
    # Test basic API of the relations layer (w/o Text object)
    
    # Test creating layer:
    layer = RelationLayer('test', span_names=['arg0', 'arg1'], 
                                  attributes=['attr1', 'attr2'])
    assert layer.span_names == ('arg0', 'arg1')
    assert layer.attributes == ('attr1', 'attr2')
    assert layer.ambiguous == False
    assert len(layer) == 0
    assert layer.span_level is None
    
    with pytest.raises(AssertionError):
        # error: layer name cannot consist of whitespace
        layer2 = RelationLayer('  ', span_names=['arg0', 'arg1'], 
                                     attributes=['attr1', 'attr2'])
    
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer2 = RelationLayer('test2', span_names=['arg0', 'arg1'], 
                                        attributes=['arg1', 'attr1', 'attr2'])
    
    # Test that span names and attributes cannot be mingled later
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer.attributes = ('arg0', 'arg1')
    with pytest.raises(AssertionError):
        # error: span_names and attribute names cannot overlap
        layer.span_names = ('attr1', 'attr2')

    # Test adding annotations:
    # add relation annotation via dict 
    layer.add_annotation( {'arg0': (0, 4), 'arg1': (6, 12), 'attr1': 1})
    # add relation annotation via kwargs
    layer.add_annotation( arg0=(20, 24), arg1=(26, 32), attr1=2, attr2=2 )
    # combine dict and keywords, skip one arg
    layer.add_annotation( {'arg0': (14, 18), 'attr1': 3}, attr2=3 )
    # leave annotations empty
    layer.add_annotation( arg0=(40, 44), arg1=(46, 52) )

    assert len(layer) == 4
    assert layer.span_level == 0
    assert [sp.as_tuple for sp in layer[0].spans] == \
            [('arg0', ElementaryBaseSpan(0, 4)),   ('arg1', ElementaryBaseSpan(6, 12))]
    assert [sp.as_tuple for sp in layer[1].spans] == \
            [('arg0', ElementaryBaseSpan(20, 24)), ('arg1', ElementaryBaseSpan(26, 32))]
    assert [sp.as_tuple for sp in layer[2].spans] == \
            [('arg0', ElementaryBaseSpan(14, 18))]
    assert [sp.as_tuple for sp in layer[3].spans] == \
            [('arg0', ElementaryBaseSpan(40, 44)), ('arg1', ElementaryBaseSpan(46, 52))]
    assert [dict(a) for a in layer[0].annotations] == [{'attr1': 1, 'attr2': None}]
    assert [dict(a) for a in layer[1].annotations] == [{'attr1': 2, 'attr2': 2}]
    assert [dict(a) for a in layer[2].annotations] == [{'attr1': 3, 'attr2': 3}]
    assert [dict(a) for a in layer[3].annotations] == [{'attr1': None, 'attr2': None}]

    with pytest.raises(ValueError):
        # error: named span(s) cannot be missing
        layer.add_annotation( {'attr1': 4, 'attr2': 4} )
    with pytest.raises(ValueError):
        # error: layer has different span level than newly addable spans
        layer.add_annotation( {'arg0': [(50, 54), (56, 64)], 'attr1': 4} )
    with pytest.raises(TypeError):
        # error: wrong type for named span
        layer.add_annotation( {'arg0': 1, 'attr1': 4} )
    with pytest.raises(ValueError):
        # error: wrong type for named span
        layer.add_annotation( {'arg1': None, 'attr1': 4} )
    with pytest.raises(Exception):
        # error: cannot add more than one annotation to unambiguous layer
        layer.add_annotation( arg0=(20, 24), arg1=(26, 32), attr1=4, attr2=4 )


def test_relation_layer_basic_with_text_obj():
    # Test basic API of the relations layer (with Text object)
    
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('0123456789')
    layer = RelationLayer('test', span_names=['arg0', 'arg1'], 
                                   attributes=['summa'],
                                   text_object=text)
    layer.add_annotation( {'arg0': (0, 1), 'arg1': (1, 2), 'summa': 1} )
    layer.add_annotation( {'arg0': (2, 3), 'arg1': (3, 4), 'summa': 5} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (2, 3), 'summa': 7} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (4, 5), 'summa': 9} )
    relations = []
    for rel in layer:
        relation_dict = {**{sp: rel[sp].text for sp in layer.span_names},
                         **{a: rel[a] for a in layer.attributes} }
        relations.append(relation_dict)
    assert relations == \
        [{'arg0': '0', 'arg1': '1', 'summa': 1}, \
         {'arg0': '2', 'arg1': '3', 'summa': 5}, \
         {'arg0': '5', 'arg1': '2', 'summa': 7}, \
         {'arg0': '5', 'arg1': '4', 'summa': 9}]


def test_relation_layer_access_via_get_item():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('0123456789')
    # Case 1: unambiguous layer
    layer = RelationLayer('relations', span_names=['arg0', 'arg1'], 
                                       attributes=['summa'],
                                       text_object=text)
    layer.add_annotation( {'arg0': (0, 1), 'arg1': (1, 2), 'summa': 1} )
    layer.add_annotation( {'arg0': (2, 3), 'arg1': (3, 4), 'summa': 5} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (2, 3), 'summa': 7} )
    layer.add_annotation( {'arg0': (5, 6), 'arg1': (4, 5), 'summa': 9} )
    text.add_layer(layer)
    # access single span
    assert str(text['relations']['arg0']) == \
        "[[NamedSpan(arg0: '0')], [NamedSpan(arg0: '2')], [NamedSpan(arg0: '5')], [NamedSpan(arg0: '5')]]"
    assert str(text['relations'][['arg0']]) == \
        "[[NamedSpan(arg0: '0')], [NamedSpan(arg0: '2')], [NamedSpan(arg0: '5')], [NamedSpan(arg0: '5')]]"
    # access span and attribute
    assert str(text['relations'][['arg1', 'summa']]) == \
        "[[NamedSpan(arg1: '1'), 1], [NamedSpan(arg1: '3'), 5], [NamedSpan(arg1: '2'), 7], [NamedSpan(arg1: '4'), 9]]"
    # access multiple spans
    assert str(text['relations'][['arg0', 'arg1']]) == \
        "[[NamedSpan(arg0: '0'), NamedSpan(arg1: '1')], [NamedSpan(arg0: '2'), NamedSpan(arg1: '3')], "+\
         "[NamedSpan(arg0: '5'), NamedSpan(arg1: '2')], [NamedSpan(arg0: '5'), NamedSpan(arg1: '4')]]"

    with pytest.raises(ValueError):
        # error: illegal attribute or span name
        text['relations'][['arg2', 'arg3']]

    # Case 2: ambiguous layer
    layer2 = RelationLayer('relations2', span_names=['arg0', 'arg1'], 
                                         attributes=['less_than'],
                                         text_object=text, ambiguous=True)
    layer2.add_annotation( {'arg0': (0, 1), 'arg1': (1, 2), 'less_than': 2} )
    layer2.add_annotation( {'arg0': (0, 1), 'arg1': (1, 2), 'less_than': 3} )
    layer2.add_annotation( {'arg0': (2, 3), 'arg1': (3, 4), 'less_than': 6} )
    layer2.add_annotation( {'arg0': (5, 6), 'arg1': (2, 3), 'less_than': 8} )
    layer2.add_annotation( {'arg0': (5, 6), 'arg1': (4, 5), 'less_than': 10} )
    text.add_layer(layer2)
    # access single span
    assert str(text['relations2']['arg0']) == \
        "[[[NamedSpan(arg0: '0')], [NamedSpan(arg0: '0')]], "+\
         "[[NamedSpan(arg0: '2')]], "+\
         "[[NamedSpan(arg0: '5')]], "+\
         "[[NamedSpan(arg0: '5')]]]"
    assert str(text['relations2'][['arg0']]) == \
        "[[[NamedSpan(arg0: '0')], [NamedSpan(arg0: '0')]], "+\
         "[[NamedSpan(arg0: '2')]], "+\
         "[[NamedSpan(arg0: '5')]], "+\
         "[[NamedSpan(arg0: '5')]]]"
    # access span and attribute
    assert str(text['relations2'][['arg1', 'less_than']]) == \
        "[[[NamedSpan(arg1: '1'), 2], [NamedSpan(arg1: '1'), 3]], "+\
         "[[NamedSpan(arg1: '3'), 6]], "+\
         "[[NamedSpan(arg1: '2'), 8]], "+\
         "[[NamedSpan(arg1: '4'), 10]]]"
    assert str(text['relations2'][['arg0', 'arg1']]) == \
        "[[[NamedSpan(arg0: '0'), NamedSpan(arg1: '1')], [NamedSpan(arg0: '0'), NamedSpan(arg1: '1')]], "+\
         "[[NamedSpan(arg0: '2'), NamedSpan(arg1: '3')]], "+\
         "[[NamedSpan(arg0: '5'), NamedSpan(arg1: '2')]], "+\
         "[[NamedSpan(arg0: '5'), NamedSpan(arg1: '4')]]]"

    # single relation: access single span
    assert str(text['relations2'][0]['arg0']) == "NamedSpan(arg0: '0')"
    assert str(text['relations2'][0][['arg0']]) == \
        "[[NamedSpan(arg0: '0')], [NamedSpan(arg0: '0')]]"  # TODO: is this expected behaviour?
    # single relation: access single span and attribute
    assert str(text['relations2'][0][['arg0', 'less_than']]) == \
        "[[NamedSpan(arg0: '0'), 2], [NamedSpan(arg0: '0'), 3]]"


def test_relation_layer_named_span_resolve_foreign_attribute():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Create input text
    text = Text('See on Peeter. Ta on, nagu ta on. Aga tubli mees.')
    relation_layer = RelationLayer('coref', span_names=('mention', 'entity'), attributes=('rel_id',))
    relation_layer.add_annotation(mention=(0,3),   entity=(7,13), rel_id=0)
    relation_layer.add_annotation(mention=(15,17), entity=(7,13), rel_id=1)
    # Add words/morph annotations
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 6)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (7, 13)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (13, 14)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (15, 17)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (18, 20)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (20, 21)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (22, 26)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (27, 29)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (30, 32)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (32, 33)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (34, 37)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (38, 43)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (44, 48)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (48, 49)}]}
    morph_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'see',
                                     'normalized_text': 'See',
                                     'partofspeech': 'P',
                                     'root': 'see',
                                     'root_tokens': ['see']}],
                    'base_span': (0, 3)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'vad',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (4, 6)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'Peeter',
                                     'normalized_text': 'Peeter',
                                     'partofspeech': 'H',
                                     'root': 'Peeter',
                                     'root_tokens': ['Peeter']}],
                    'base_span': (7, 13)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (13, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'tema',
                                     'normalized_text': 'Ta',
                                     'partofspeech': 'P',
                                     'root': 'tema',
                                     'root_tokens': ['tema']}],
                    'base_span': (15, 17)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'vad',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (18, 20)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (20, 21)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'nagu',
                                     'normalized_text': 'nagu',
                                     'partofspeech': 'J',
                                     'root': 'nagu',
                                     'root_tokens': ['nagu']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'nagu',
                                     'normalized_text': 'nagu',
                                     'partofspeech': 'D',
                                     'root': 'nagu',
                                     'root_tokens': ['nagu']}],
                    'base_span': (22, 26)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'tema',
                                     'normalized_text': 'ta',
                                     'partofspeech': 'P',
                                     'root': 'tema',
                                     'root_tokens': ['tema']}],
                    'base_span': (27, 29)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'vad',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (30, 32)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (32, 33)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'aga',
                                     'normalized_text': 'Aga',
                                     'partofspeech': 'J',
                                     'root': 'aga',
                                     'root_tokens': ['aga']}],
                    'base_span': (34, 37)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'tubli',
                                     'normalized_text': 'tubli',
                                     'partofspeech': 'A',
                                     'root': 'tubli',
                                     'root_tokens': ['tubli']}],
                    'base_span': (38, 43)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mees',
                                     'normalized_text': 'mees',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']}],
                    'base_span': (44, 48)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (48, 49)}]}
    text.add_layer( dict_to_layer(words_layer_dict) )
    text.add_layer( dict_to_layer(morph_layer_dict) )
    
    # Try to resolve foreign attributes
    # Case 1: try to get foreign attribute when Text obj is missing
    with pytest.raises(AttributeError):
        # -> Unable to resolve foreign attribute X: the layer is not attached to Text object.
        relation_layer[0].mention.morph_analysis
    
    # Attach text_object
    relation_layer.text_object = text
    text.add_layer( relation_layer )
    
    # Case 2: Collect mappings from named spans to morph layer spans
    collected_mappings = []
    for rel in relation_layer:
        for sp in rel.spans:
            collected_mappings.append( f'{sp} -> {sp.morph_analysis}' )
    assert collected_mappings == \
        ["NamedSpan(mention: 'See') -> Span('See', [{'normalized_text': 'See', 'lemma': 'see', 'root': 'see', 'root_tokens': ['see'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}])", 
         "NamedSpan(entity: 'Peeter') -> Span('Peeter', [{'normalized_text': 'Peeter', 'lemma': 'Peeter', 'root': 'Peeter', 'root_tokens': ['Peeter'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'H'}])", 
         "NamedSpan(mention: 'Ta') -> Span('Ta', [{'normalized_text': 'Ta', 'lemma': 'tema', 'root': 'tema', 'root_tokens': ['tema'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}])", 
         "NamedSpan(entity: 'Peeter') -> Span('Peeter', [{'normalized_text': 'Peeter', 'lemma': 'Peeter', 'root': 'Peeter', 'root_tokens': ['Peeter'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'H'}])"]

    if Text().__class__.__name__ == 'Text':
        # Case 3: if the estnltk main package is available, we can 
        # also collect mappings from named span to corresponding 
        # lemma/postag etc.
        collected_lemma_mappings = []
        collected_pos_mappings = []
        for rel in relation_layer:
            for sp in rel.spans:
                collected_lemma_mappings.append( f'{sp} -> {sp.lemma}' )
                collected_pos_mappings.append( f'{sp} -> {sp.partofspeech}' )
        assert collected_lemma_mappings == \
            ["NamedSpan(mention: 'See') -> ['see']", "NamedSpan(entity: 'Peeter') -> ['Peeter']", 
             "NamedSpan(mention: 'Ta') -> ['tema']", "NamedSpan(entity: 'Peeter') -> ['Peeter']"]
        assert collected_pos_mappings == \
            ["NamedSpan(mention: 'See') -> ['P']", "NamedSpan(entity: 'Peeter') -> ['H']", 
             "NamedSpan(mention: 'Ta') -> ['P']", "NamedSpan(entity: 'Peeter') -> ['H']"]


def test_relation_layer_deep_copy():
    # Simple empty layer
    layer = RelationLayer('test', span_names=['my_span'])
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Simple relations layer with some relations
    layer = RelationLayer('test', span_names=['my_span'], 
                                   attributes=['attribute1', 'attribute2'],
                                   ambiguous=True)
    layer.add_annotation(my_span=(0, 2), attribute1='test1')
    layer.add_annotation(my_span=(2, 4), attribute2='test2')
    layer_deepcopy = deepcopy( layer )
    assert layer == layer_deepcopy
    assert layer.span_names == layer_deepcopy.span_names
    assert layer.attributes == layer_deepcopy.attributes
    assert layer.ambiguous  == layer_deepcopy.ambiguous
    assert layer is not layer_deepcopy
    assert layer.meta is not layer_deepcopy.meta

    # Modify attributes
    # Initially, both layers' attributes point to the same tuple
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy.attributes is layer.attributes
    layer_deepcopy.attributes = [*layer_deepcopy.attributes, 'new_attribute']
    assert layer_deepcopy.attributes != layer.attributes
    assert layer_deepcopy != layer
    layer_deepcopy.attributes = layer_deepcopy.attributes[:-1]
    # After modification of one layer, tuples won't be same anymore ...
    assert layer_deepcopy.attributes == layer.attributes
    assert layer_deepcopy == layer
    assert layer_deepcopy.attributes is not layer.attributes

    # Modify relations
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] == layer[0]
    # Relation references are different
    assert layer_deepcopy[0] is not layer[0]
    # Deleting relation from one layer does not affect the other layer
    del layer_deepcopy[0]
    del layer_deepcopy[0]
    assert layer_deepcopy != layer
    layer_deepcopy.add_annotation(my_span=(0, 2), attribute1='test1')
    layer_deepcopy.add_annotation(my_span=(2, 4), attribute2='test2')
    assert layer_deepcopy == layer
    assert layer_deepcopy[0] is not layer[0]

    # Modify annotations
    assert layer_deepcopy[0].annotations == layer[0].annotations
    # We can modify annotations without affecting the other layer
    layer_deepcopy.add_annotation( {**{sp.name: sp.base_span for sp in layer_deepcopy[1].spans}, \
                                    **{'attribute2': 'test3'}} )
    assert layer_deepcopy[0].annotations == layer[0].annotations
    assert layer_deepcopy[1].annotations != layer[1].annotations
    assert layer_deepcopy != layer
    del layer_deepcopy[1].annotations[-1]
    assert layer_deepcopy[1].annotations == layer[1].annotations
    assert layer_deepcopy == layer
    assert layer_deepcopy[1].annotations is not layer[1].annotations
    layer[0].annotations[-1].attribute1 = '???'
    assert layer_deepcopy[0].annotations[-1].attribute1 == 'test1'
    assert layer_deepcopy[0].annotations != layer[0].annotations
    layer_deepcopy[0].annotations[-1].attribute1 = '???'
    assert layer_deepcopy[0].annotations == layer[0].annotations
    assert layer_deepcopy[0] == layer[0]
    assert layer_deepcopy == layer