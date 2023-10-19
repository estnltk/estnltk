from typing import Union

import pytest
from copy import deepcopy

from estnltk_core import Layer
from estnltk_core import RelationLayer
from estnltk_core.common import create_text_object
from estnltk_core.converters import layer_to_dict
from estnltk_core.taggers import RelationTagger

class DummyButValidRelationTagger(RelationTagger):
    """Dummy But Valid RelationTagger (for testing)."""
    conf_param = []

    def __init__(self, output_layer, input_layers):
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_span_names = ['arg0', 'arg1']
        self.output_attributes = ['attr']
        self.conf_param = ['extra_param_1', '_extra_param_2']
        self.extra_param_1 = 1
        self._extra_param_2 = None

    def _make_layer_template(self) -> RelationLayer:
        return RelationLayer(self.output_layer, self.output_span_names, self.output_attributes)

    def _make_layer(self, text: Union['BaseText', 'Text'], layers, status=None) -> RelationLayer:
        layer = self._make_layer_template()
        layer.text_object = text
        layer.add_annotation( arg0=(0,1), arg1=(1,2) )
        layer.add_annotation( arg0=(2,3), arg1=(1,2), attr=43 )
        return layer


def test_relation_tagger_smoke():
    # Smoke test normal definition and run of relation tagger
    text1 = create_text_object('ABCDEFGHIJ')
    assert text1.layers == set()
    assert text1.relation_layers == set()
    relation_tagger = DummyButValidRelationTagger('my_relations', [])
    relation_tagger.tag( text1 )
    assert text1.layers == set()
    assert text1.relation_layers == { relation_tagger.output_layer }
    outcome_layer = text1[ relation_tagger.output_layer ]
    assert outcome_layer.text_object == text1
    assert outcome_layer.name == relation_tagger.output_layer
    assert outcome_layer.span_names == relation_tagger.output_span_names
    assert outcome_layer.attributes == relation_tagger.output_attributes
    expected_layer_dict = \
        {'ambiguous': False,
         'attributes': ('attr',),
         'meta': {},
         'name': 'my_relations',
         'relations': [{'annotations': [{'attr': None}],
                        'named_spans': {'arg0': (0, 1), 'arg1': (1, 2)}},
                       {'annotations': [{'attr': 43}],
                        'named_spans': {'arg0': (2, 3), 'arg1': (1, 2)}}],
         'secondary_attributes': (),
         'display_order': ('arg0', 'arg1', 'attr'), 
         'serialisation_module': 'relations_v1',
         'span_names': ('arg0', 'arg1')}
    assert layer_to_dict(outcome_layer) == expected_layer_dict
    
    # Test tagger with dependency layers
    input_layers = ['span_layer1', 'relation_layer1']
    relation_tagger_with_deps = DummyButValidRelationTagger('my_relations_2', input_layers)
    # Can't tag text if dependencies are missing
    with pytest.raises(Exception):
        relation_tagger_with_deps.tag( text1 )
    text1.add_layer( Layer('span_layer1', attributes=('a', 'b')) )
    # Still some dependencies are missing ...
    with pytest.raises(Exception):
        relation_tagger_with_deps.tag( text1 )
    text1.add_layer( RelationLayer('relation_layer1', span_names=('u', 'v'), attributes=('a', 'b')) )
    # Now tagging is successful
    relation_tagger_with_deps.tag( text1 )
    # Check the outcome
    expected_layer_dict_2 = deepcopy(expected_layer_dict)
    expected_layer_dict_2['name'] = relation_tagger_with_deps.output_layer
    outcome_layer = text1[ relation_tagger_with_deps.output_layer ]
    assert layer_to_dict(outcome_layer) == expected_layer_dict_2


class FawltyConfigurationRelationTagger(RelationTagger):
    """Fawlty (Faulty) Configuration RelationTagger (for testing)."""

    def __init__(self, skip_output_layer=True, 
                       skip_input_layers=False, 
                       skip_output_span_names=False, 
                       empty_span_names=False, 
                       skip_output_attributes=False, 
                       skip_conf_param=False, 
                       skip_conf_param_attrs=False, 
                       add_attrs_outside_conf_param=False ):
        if not skip_output_layer:
            self.output_layer = 'my_relations'
        if not skip_input_layers:
            self.input_layers = []
        if not skip_output_span_names:
            if not empty_span_names:
                self.output_span_names = ['arg0', 'arg1']
            else:
                self.output_span_names = []
        if not skip_output_attributes:
            self.output_attributes = ['attr']
        if not skip_conf_param:
            self.conf_param = ['extra_param_1', '_extra_param_2']
        if not skip_conf_param_attrs:
            self.extra_param_1 = 1
            self._extra_param_2 = None
        if add_attrs_outside_conf_param:
            self.extra_param_3 = 0

    def _make_layer(self, text: Union['BaseText', 'Text'], layers, status=None) -> RelationLayer:
        layer = RelationLayer(self.output_layer, self.output_span_names, self.output_attributes, text_object=text)
        layer.add_annotation( arg0=(0,1), arg1=(1,2) )
        layer.add_annotation( arg0=(2,3), arg1=(1,2), attr=43 )
        return layer


def test_relation_tagger_configuration_errors():
    # Test errors risen due to faulty configurations / definitions of relation tagger
    
    # Check all faulty configurations
    for conf_params in [{'skip_output_layer': True}, 
                        {'skip_output_layer': False, 'skip_input_layers':True },
                        {'skip_output_layer': False, 'skip_output_span_names':True },
                        {'skip_output_layer': False, 'empty_span_names':True },
                        {'skip_output_layer': False, 'skip_output_attributes':True },
                        {'skip_output_layer': False, 'skip_conf_param':True },
                        {'skip_output_layer': False, 'add_attrs_outside_conf_param':True }]:
        with pytest.raises(Exception):
            relation_tagger = FawltyConfigurationRelationTagger(**conf_params)


class FawltyLayerCreationRelationTagger(RelationTagger):
    """Fawlty (Faulty) Layer Creation RelationTagger (for testing)."""

    def __init__(self, unassigned_layer=True, 
                       wrong_layer_type=False, 
                       wrong_layer_name=False, 
                       wrong_spans=False, 
                       wrong_attributes=False ):
        self.output_layer = 'my_relations'
        self.input_layers = []
        self.output_span_names = ['arg0', 'arg1']
        self.output_attributes = ['attr']
        self.conf_param = ['unassigned_layer', 
                           'wrong_layer_type', 
                           'wrong_layer_name',
                           'wrong_spans',
                           'wrong_attributes']
        self.unassigned_layer = unassigned_layer
        self.wrong_layer_type = wrong_layer_type
        self.wrong_layer_name = wrong_layer_name
        self.wrong_spans = wrong_spans
        self.wrong_attributes = wrong_attributes

    def _make_layer(self, text: Union['BaseText', 'Text'], layers, status=None) -> RelationLayer:
        if self.unassigned_layer:
            layer = RelationLayer(self.output_layer, self.output_span_names, self.output_attributes, text_object=None)
            layer.add_annotation( arg0=(0,1), arg1=(1,2) )
            layer.add_annotation( arg0=(2,3), arg1=(1,2), attr=43 )
        elif self.wrong_layer_type:
            layer = Layer(self.output_layer, self.output_attributes, text_object=text)
        elif self.wrong_layer_name:
            layer = RelationLayer('my-my-my_what_a_layer', self.output_span_names, self.output_attributes, text_object=text)
            layer.add_annotation( arg0=(0,1), arg1=(1,2) )
            layer.add_annotation( arg0=(2,3), arg1=(1,2), attr=43 )
        elif self.wrong_spans:
            layer = RelationLayer(self.output_layer, ('span1', 'span2'), self.output_attributes, text_object=text)
        elif self.wrong_attributes:
            layer = RelationLayer(self.output_layer,  self.output_span_names, ('attr1', 'attr2'), text_object=text)
            layer.add_annotation( arg0=(0,1), arg1=(1,2) )
            layer.add_annotation( arg0=(2,3), arg1=(1,2) )
        else:
            # create normal layer
            layer = RelationLayer(self.output_layer, self.output_span_names, self.output_attributes, text_object=text)
            layer.add_annotation( arg0=(0,1), arg1=(1,2) )
            layer.add_annotation( arg0=(2,3), arg1=(1,2), attr=43 )
        return layer


def test_relation_tagger_layer_creation_errors():
    # Test errors risen due to faulty layer creation of relation tagger
    text1 = create_text_object('ABCDEFGHIJ')
    # Check all faulty layer creation settings
    for conf_params in [{'unassigned_layer': True}, 
                        {'unassigned_layer': False, 'wrong_layer_type':True },
                        {'unassigned_layer': False, 'wrong_layer_name':True },
                        {'unassigned_layer': False, 'wrong_spans':True },
                        {'unassigned_layer': False, 'wrong_attributes':True }]:
        relation_tagger = FawltyLayerCreationRelationTagger(**conf_params)
        with pytest.raises(Exception):
            relation_tagger.tag( text1 )