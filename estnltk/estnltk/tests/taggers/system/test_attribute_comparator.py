from collections import OrderedDict

from estnltk.taggers import AttributeComparator
from estnltk import Text, Layer

from estnltk.converters import layer_to_dict

def test_attribute_comparison_tagger_init():
    tagger = AttributeComparator(output_layer="new_layer",
                                 input_layers=["layer_1", "layer_2"],
                                 input_attributes=["id", "lemma", "head", "deprel"],
                                 attributes_to_compare=["head", "deprel"])

    assert tagger.constant_attributes == ["id", "lemma"]
    assert tagger.output_attributes == ("id", "lemma", "head", "head_1", "head_2", "deprel", "deprel_1", "deprel_2")

def test_head_attribute_comparison():
    text = Text("Poole tunni pärast on varbad külmast kanged.")

    layer_1 = Layer(name='layer_1', text_object=text, attributes=['head'])
    layer_1.add_annotation((0, 5), head=3)
    layer_1.add_annotation((6, 11), head=1)
    layer_1.add_annotation((12, 18), head=4)
    layer_1.add_annotation((19, 21), head=0)
    layer_1.add_annotation((22, 28), head=4)
    layer_1.add_annotation((29, 36), head=4)
    layer_1.add_annotation((37, 43), head=4)
    layer_1.add_annotation((43, 44), head=7)

    layer_2 = Layer(name='layer_2', text_object=text, attributes=['head'])
    layer_2.add_annotation((0, 5), head=3)
    layer_2.add_annotation((6, 11), head=1)
    layer_2.add_annotation((12, 18), head=4)
    layer_2.add_annotation((19, 21), head=0)
    layer_2.add_annotation((22, 28), head=4)
    layer_2.add_annotation((29, 36), head=7)
    layer_2.add_annotation((37, 43), head=4)
    layer_2.add_annotation((43, 44), head=7)

    tagger = AttributeComparator(output_layer="new_layer",
                                 input_layers=["layer_1", "layer_2"],
                                 input_attributes=["head"],
                                 attributes_to_compare=["head"])

    new_layer = tagger.make_layer(text=text, layers=OrderedDict([('layer_1', layer_1), ('layer_2', layer_2)]))

    assert layer_to_dict(new_layer) == {'ambiguous': False,
                                     'attributes': ('head', 'head_1', 'head_2'),
                                     'secondary_attributes': (),
                                     'enveloping': None,
                                     'meta': {},
                                     'name': 'new_layer',
                                     'parent': None,
                                     'serialisation_module': None,
                                     'spans': [{'annotations': [{'head': 3, 'head_1': 3, 'head_2': 3}],
                                       'base_span': (0, 5)},
                                      {'annotations': [{'head': 1, 'head_1': 1, 'head_2': 1}],
                                       'base_span': (6, 11)},
                                      {'annotations': [{'head': 4, 'head_1': 4, 'head_2': 4}],
                                       'base_span': (12, 18)},
                                      {'annotations': [{'head': 0, 'head_1': 0, 'head_2': 0}],
                                       'base_span': (19, 21)},
                                      {'annotations': [{'head': 4, 'head_1': 4, 'head_2': 4}],
                                       'base_span': (22, 28)},
                                      {'annotations': [{'head': None, 'head_1': 4, 'head_2': 7}],
                                       'base_span': (29, 36)},
                                      {'annotations': [{'head': 4, 'head_1': 4, 'head_2': 4}],
                                       'base_span': (37, 43)},
                                      {'annotations': [{'head': 7, 'head_1': 7, 'head_2': 7}],
                                       'base_span': (43, 44)}]}

def test_deprel_attribute_comparison():
    text = Text("Suurim paksus 28 cm")

    layer_1 = Layer(name='layer_1', text_object=text, attributes=['deprel'])
    layer_1.add_annotation((0, 6), deprel='@AN>')
    layer_1.add_annotation((7, 13), deprel='ROOT')
    layer_1.add_annotation((14, 16), deprel='@PRD')
    layer_1.add_annotation((17, 19), deprel='@<Q')

    layer_2 = Layer(name='layer_2', text_object=text, attributes=['deprel'])
    layer_2.add_annotation((0, 6), deprel='@AN>')
    layer_2.add_annotation((7, 13), deprel='ROOT')
    layer_2.add_annotation((14, 16), deprel='@ADVL')
    layer_2.add_annotation((17, 19), deprel='@<Q')

    tagger = AttributeComparator(output_layer="new_layer",
                                 input_layers=["layer_1", "layer_2"],
                                 input_attributes=["deprel"],
                                 attributes_to_compare=["deprel"])

    new_layer = tagger.make_layer(text=text, layers=OrderedDict([('layer_1', layer_1), ('layer_2', layer_2)]))

    assert layer_to_dict(new_layer) == {'ambiguous': False,
                                     'attributes': ('deprel', 'deprel_1', 'deprel_2'),
                                     'secondary_attributes': (),
                                     'enveloping': None,
                                     'meta': {},
                                     'name': 'new_layer',
                                     'parent': None,
                                     'serialisation_module': None,
                                     'spans': [{'annotations': [{'deprel': '@AN>',
                                         'deprel_1': '@AN>',
                                         'deprel_2': '@AN>'}],
                                       'base_span': (0, 6)},
                                      {'annotations': [{'deprel': 'ROOT', 'deprel_1': 'ROOT', 'deprel_2': 'ROOT'}],
                                       'base_span': (7, 13)},
                                      {'annotations': [{'deprel': None, 'deprel_1': '@PRD', 'deprel_2': '@ADVL'}],
                                       'base_span': (14, 16)},
                                      {'annotations': [{'deprel': '@<Q', 'deprel_1': '@<Q', 'deprel_2': '@<Q'}],
                                       'base_span': (17, 19)}]}