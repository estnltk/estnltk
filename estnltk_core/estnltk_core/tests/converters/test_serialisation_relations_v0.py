#
# Test that converters are aware of the relations serialisation module 
# and can convert a RelationLayer ('relations_v0') to dict and backwards.
#

from estnltk_core.converters import dict_to_layer, layer_to_dict
from estnltk_core.converters import dict_to_text, text_to_dict
from estnltk_core.layer.relation_layer import RelationLayer, Relation

from estnltk import Text
from estnltk_core import RelationLayer

example_text_dict = \
    {'layers': [{'ambiguous': True,
                 'attributes': ('normalized_form',),
                 'enveloping': None,
                 'meta': {},
                 'name': 'words',
                 'parent': None,
                 'secondary_attributes': (),
                 'serialisation_module': None,
                 'spans': [{'annotations': [{'normalized_form': None}],
                            'base_span': (0, 4)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (5, 14)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (15, 21)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (21, 22)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (23, 29)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (30, 32)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (33, 41)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (42, 43)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (43, 51)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (51, 52)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (53, 58)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (58, 59)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (60, 61)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (61, 63)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (64, 66)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (67, 74)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (75, 79)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (80, 88)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (89, 93)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (94, 101)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (102, 107)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (108, 111)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (112, 117)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (117, 118)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (119, 122)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (123, 128)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (129, 132)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (133, 136)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (136, 137)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (137, 138)}]}],
     'relation_layers': [],
     'meta': {},
     'text': 'Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: "Ma ei '
             'suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli '
             'see!"'}


def test_convert_relations_layer_to_dict():
    # Convert RelationLayer -> dict
    text_obj = dict_to_text( example_text_dict )
    coref_layer = RelationLayer('coreference', span_names=['mention', 'entity'], 
                                                attributes=['rel_id'], 
                                                text_object=text_obj )
    # Add relation based on a dictionary
    coref_layer.add_annotation( {'mention': (30, 32), 'entity': (0, 4)}, rel_id=1 )
    coref_layer.add_annotation( {'mention': (61, 63), 'entity': (0, 4)}, rel_id=2 )
    # Or add relation by keyword arguments
    coref_layer.add_annotation( mention=(75, 88), entity=(42, 52), rel_id=3 )
    coref_layer.add_annotation( mention=(133, 136), entity=(42, 52), rel_id=4 )
    expected_relations_layer_dict = \
        {'ambiguous': False,
         'attributes': ('rel_id',),
         'secondary_attributes': (),
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'rel_id': 1}],
                        'named_spans': {'entity': (0, 4), 'mention': (30, 32)}},
                       {'annotations': [{'rel_id': 2}],
                        'named_spans': {'entity': (0, 4), 'mention': (61, 63)}},
                       {'annotations': [{'rel_id': 3}],
                        'named_spans': {'entity': (42, 52), 'mention': (75, 88)}},
                       {'annotations': [{'rel_id': 4}],
                        'named_spans': {'entity': (42, 52), 'mention': (133, 136)}}],
         'serialisation_module': 'relations_v0',
         'span_names': ('mention', 'entity') }
    # Validate dict
    assert expected_relations_layer_dict == layer_to_dict(coref_layer)

def test_convert_relations_dict_to_layer():
    # Convert dict -> RelationLayer
    text_obj = dict_to_text( example_text_dict )
    relations_layer_dict = \
        {'ambiguous': False,
         'attributes': ('rel_id',),
         'secondary_attributes': (),
         'meta': {},
         'name': 'coreference',
         'relations': [{'annotations': [{'rel_id': 1}],
                        'named_spans': {'entity': (0, 4), 'mention': (30, 32)}},
                       {'annotations': [{'rel_id': 2}],
                        'named_spans': {'entity': (0, 4), 'mention': (61, 63)}},
                       {'annotations': [{'rel_id': 3}],
                        'named_spans': {'entity': (42, 52), 'mention': (75, 88)}},
                       {'annotations': [{'rel_id': 4}],
                        'named_spans': {'entity': (42, 52), 'mention': (133, 136)}}],
         'serialisation_module': 'relations_v0',
         'span_names': ('mention', 'entity') }
    coref_layer = dict_to_layer(relations_layer_dict)
    coref_layer.text_object = text_obj
    # Validate layer
    assert isinstance(coref_layer, RelationLayer)
    assert coref_layer.name == 'coreference'
    assert coref_layer.attributes == ('rel_id',)
    assert coref_layer.secondary_attributes == ()
    assert coref_layer.span_names == ('mention', 'entity')
    assert coref_layer.meta == {}
    assert len(coref_layer) == 4
    results = []
    for rel in coref_layer:
        assert isinstance(rel, Relation)
        results.append( (rel['rel_id'],rel['mention'].text, rel['entity'].text) )
    assert results == \
        [ (1, 'ta', 'Mari'), \
          (2, 'Ma', 'Mari'), \
          (3, 'seda raamatut', '"Sipsikut"'), \
          (4, 'see', '"Sipsikut"') ]


def test_convert_text_with_relation_layers_to_dict():
    # Convert Text obj with Layer and RelationLayer --> dict
    text_obj = dict_to_text( example_text_dict )
    text_obj['words'].clear_spans()
    coref_layer1 = RelationLayer('coreference_a', span_names=['mention', 'entity'], 
                                                 attributes=['rel_id'], 
                                                 text_object=text_obj )
    coref_layer1.add_annotation( {'mention': (30, 32), 'entity': (0, 4)}, rel_id=1 )
    coref_layer1.add_annotation( {'mention': (61, 63), 'entity': (0, 4)}, rel_id=2 )
    coref_layer2 = RelationLayer('coreference_b', span_names=['entity', 'mention'], 
                                                  attributes=['rel_id'], 
                                                  text_object=text_obj )
    coref_layer2.add_annotation( mention=(75, 88), entity=(42, 52), rel_id=3 )
    coref_layer2.add_annotation( mention=(133, 136), entity=(42, 52), rel_id=4 )
    text_obj.add_layer( coref_layer1 )
    text_obj.add_layer( coref_layer2 )
    expected_text_obj_dict = \
        {'layers': [{'ambiguous': True,
                     'attributes': ('normalized_form',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'words',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': []}],
         'meta': {},
         'relation_layers': [{'ambiguous': False,
                              'attributes': ('rel_id',),
                              'meta': {},
                              'name': 'coreference_a',
                              'relations': [{'annotations': [{'rel_id': 1}],
                                             'named_spans': {'entity': (0, 4),
                                                             'mention': (30, 32)}},
                                            {'annotations': [{'rel_id': 2}],
                                             'named_spans': {'entity': (0, 4),
                                                             'mention': (61, 63)}}],
                              'secondary_attributes': (),
                              'serialisation_module': 'relations_v0',
                              'span_names': ('mention', 'entity')},
                             {'ambiguous': False,
                              'attributes': ('rel_id',),
                              'meta': {},
                              'name': 'coreference_b',
                              'relations': [{'annotations': [{'rel_id': 3}],
                                             'named_spans': {'entity': (42, 52),
                                                             'mention': (75, 88)}},
                                            {'annotations': [{'rel_id': 4}],
                                             'named_spans': {'entity': (42, 52),
                                                             'mention': (133, 136)}}],
                              'secondary_attributes': (),
                              'serialisation_module': 'relations_v0',
                              'span_names': ('entity', 'mention')}],
         'text': 'Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: "Ma ei '
                 'suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli '
                 'see!"'}
    assert expected_text_obj_dict == text_to_dict(text_obj)


def test_convert_dict_to_text_with_relation_layers():
    # Convert dict --> Text obj with Layer and RelationLayer
    text_obj_dict = \
        {'layers': [{'ambiguous': True,
                     'attributes': ('normalized_form',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'words',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': []}],
         'meta': {},
         'relation_layers': [{'ambiguous': False,
                              'attributes': ('rel_id',),
                              'meta': {},
                              'name': 'coreference_a',
                              'relations': [{'annotations': [{'rel_id': 1}],
                                             'named_spans': {'entity': (0, 4),
                                                             'mention': (30, 32)}},
                                            {'annotations': [{'rel_id': 2}],
                                             'named_spans': {'entity': (0, 4),
                                                             'mention': (61, 63)}}],
                              'secondary_attributes': (),
                              'serialisation_module': 'relations_v0',
                              'span_names': ('mention', 'entity')},
                             {'ambiguous': False,
                              'attributes': ('rel_id',),
                              'meta': {},
                              'name': 'coreference_b',
                              'relations': [{'annotations': [{'rel_id': 1}],
                                             'named_spans': {'entity': (42, 52),
                                                             'mention': (75, 88)}},
                                            {'annotations': [{'rel_id': 2}],
                                             'named_spans': {'entity': (42, 52),
                                                             'mention': (133, 136)}}],
                              'secondary_attributes': (),
                              'serialisation_module': 'relations_v0',
                              'span_names': ('entity', 'mention')}],
         'text': 'Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: "Ma ei '
                 'suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli '
                 'see!"'}
    text_obj = dict_to_text(text_obj_dict)
    assert text_obj.layers == {'words'}
    assert text_obj.relation_layers == {'coreference_a', 'coreference_b'}
    assert isinstance(text_obj['coreference_a'], RelationLayer)
    assert isinstance(text_obj['coreference_b'], RelationLayer)
    layer_a = []
    for rel in text_obj['coreference_a']:
        assert isinstance(rel, Relation)
        layer_a.append( (rel['rel_id'], rel['mention'].text, rel['entity'].text) )
    assert layer_a == [ (1, 'ta', 'Mari'), \
                        (2, 'Ma', 'Mari') ]
    layer_b = []
    for rel in text_obj['coreference_b']:
        assert isinstance(rel, Relation)
        layer_b.append( (rel['rel_id'], rel['mention'].text, rel['entity'].text) )
    assert layer_b == [ (1, 'seda raamatut', '"Sipsikut"'), \
                        (2, 'see', '"Sipsikut"') ]