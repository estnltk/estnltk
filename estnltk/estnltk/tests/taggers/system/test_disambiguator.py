from estnltk import Text, Layer
from estnltk.taggers import Disambiguator
from estnltk_core.converters import layer_to_dict

def test_1():
    text = Text('Tere, maailm!')

    layer_1 = Layer(name='simple_ambiguous', attributes=['attr_1', 'attr_2'], ambiguous=True, text_object=text)
    layer_1.add_annotation((0, 4), attr_1=1, attr_2=2)
    layer_1.add_annotation((0, 4), attr_1=3, attr_2=4)
    layer_1.add_annotation((0, 4), attr_1=5, attr_2=6)
    layer_1.add_annotation((4, 5), attr_1=7, attr_2=8)
    layer_1.add_annotation((4, 5), attr_1=9, attr_2=10)
    layer_1.add_annotation((0, 4), attr_1=11, attr_2=12)
    layer_1.add_annotation((6, 12), attr_1=13, attr_2=14)
    layer_1.add_annotation((6, 12), attr_1=15, attr_2=16)
    layer_1.add_annotation((12, 13), attr_1=17, attr_2=18)
    text.add_layer(layer_1)

    def decorator(ambiguous_span, raw_text):
        attr_1 = 0
        for annotation in ambiguous_span.annotations:
            attr_1 += annotation.attr_1
        return {'attr_1': attr_1}

    tagger_1 = Disambiguator(output_layer='simple',
                             input_layer='simple_ambiguous',
                             output_attributes=['attr_1'],
                             decorator=decorator)
    tagger_1.tag(text)

    assert layer_to_dict( text.simple ) == \
        {'ambiguous': False,
         'attributes': ('attr_1',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'simple',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'attr_1': 20}], 'base_span': (0, 4)},
                   {'annotations': [{'attr_1': 16}], 'base_span': (4, 5)},
                   {'annotations': [{'attr_1': 28}], 'base_span': (6, 12)},
                   {'annotations': [{'attr_1': 17}], 'base_span': (12, 13)}]}

    layer_2 = Layer(name='enveloping_ambiguous',
                    attributes=['attr_3'],
                    enveloping='simple_ambiguous',
                    ambiguous=True)

    spans = text.simple_ambiguous[0:2]
    layer_2.add_annotation(spans, attr_3=30)
    layer_2.add_annotation(spans, attr_3=31)

    spans = text.simple_ambiguous[2:4]
    layer_2.add_annotation(spans, attr_3=32)

    text.add_layer(layer_2)

    def decorator(ambiguous_span, raw_text):
        return {'attr_1': len(ambiguous_span)}

    tagger_2 = Disambiguator(output_layer='enveloping',
                             input_layer='enveloping_ambiguous',
                             output_attributes=['attr_1', ],
                             decorator=decorator
                            )
    tagger_2.tag(text)
    
    assert layer_to_dict( text.enveloping ) == \
        {'ambiguous': False,
         'attributes': ('attr_1',),
         'secondary_attributes': (),
         'enveloping': 'simple_ambiguous',
         'meta': {},
         'name': 'enveloping',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'attr_1': 2}], 'base_span': ((0, 4), (4, 5))},
                   {'annotations': [{'attr_1': 2}], 'base_span': ((6, 12), (12, 13))}]}

