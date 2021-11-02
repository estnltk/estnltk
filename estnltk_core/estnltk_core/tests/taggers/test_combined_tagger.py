from estnltk_core.common import load_text_class
from estnltk_core import Layer, Span
from estnltk_core.taggers import Tagger
from estnltk_core.taggers.combined_tagger import CombinedTagger


class Tagger_1(Tagger):
    """Test tagger 1

    """
    conf_param = []
    input_layers = []
    output_layer = 'layer_1'
    output_attributes = ['attr_1', 'attr_2', 'attr_a']

    def __init__(self):
        pass

    def _make_layer(self, text: 'Text', layers, status: dict):
        layer = Layer(name='layer_1', attributes=['attr_1', 'attr_2', 'attr_a'], text_object=text)
        layer.add_annotation((0, 5), attr_1='1', attr_2='', attr_a='a')
        return layer


class Tagger_2(Tagger):
    """Test tagger 1

    """
    conf_param = []
    input_layers = []
    output_layer = 'layer_1'
    output_attributes = ['attr_1', 'attr_2', 'attr_b']

    def __init__(self):
        pass

    def _make_layer(self, text: 'Text', layers, status: dict):
        layer = Layer(name='layer_1', attributes=['attr_1', 'attr_2', 'attr_b'], text_object=text)
        layer.add_annotation((6, 10), attr_1='2', attr_2='', attr_b='b')
        return layer


class Tagger_3(Tagger):
    """Test tagger 1

    """
    conf_param = []
    input_layers = []
    output_layer = 'layer_1'
    output_attributes = ['attr_1', 'attr_2', 'attr_c']

    def __init__(self):
        pass

    def _make_layer(self, text: 'Text', layers, status: dict):
        layer = Layer(name='layer_1', attributes=['attr_1', 'attr_2', 'attr_c'], text_object=text)
        layer.add_annotation((11, 15), attr_1='3', attr_2='', attr_c='c')
        return layer


def test_tagger():
    tagger_1 = Tagger_1()
    tagger_2 = Tagger_2()

    combined_tagger = CombinedTagger(output_layer='combined', output_attributes=['attr_1', 'attr_2'],
                                     taggers=[tagger_1, tagger_2])
    Text = load_text_class()
    text = Text('Aias sadas saia.')
    combined_tagger.tag(text)
    assert text.combined.to_records() == [{'start':  0, 'end':  5, 'attr_1': '1', 'attr_2': ''},
                                          {'start':  6, 'end': 10, 'attr_1': '2', 'attr_2': ''},
                                          ]


def test_add_tagger():
    tagger_1 = Tagger_1()
    tagger_2 = Tagger_2()
    tagger_3 = Tagger_3()

    combined_tagger = CombinedTagger(output_layer='combined', output_attributes=['attr_1', 'attr_2'],
                                     taggers=[tagger_1])

    combined_tagger.add_tagger(tagger_2)
    combined_tagger.add_tagger(tagger_3)

    Text = load_text_class()
    text = Text('Aias sadas saia.')
    combined_tagger.tag(text)
    assert text.combined.to_records() == [{'start':  0, 'end':  5, 'attr_1': '1', 'attr_2': ''},
                                          {'start':  6, 'end': 10, 'attr_1': '2', 'attr_2': ''},
                                          {'start': 11, 'end': 15, 'attr_1': '3', 'attr_2': ''}
                                          ]
