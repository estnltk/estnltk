from os import path

from estnltk.taggers import PhraseTagger
from estnltk.tests.helpers.text_objects import new_text
from estnltk.layer import AmbiguousAttributeList


def test_basic():
    vocabulary = path.join(path.dirname(__file__), 'phrase_vocabulary.csv')
    tagger = PhraseTagger(output_layer='phrases',
                          input_layer='layer_0',
                          input_attribute='attr',
                          vocabulary=vocabulary,
                          key='_phrase_',
                          output_attributes=['number', 'letter', '_priority_', 'attr_1', 'attr_2'],
                          global_validator=None,
                          validator_attribute='_validator_',
                          default_values={'attr_1': 'default_1', 'attr_2': lambda s, t: len(s), '_priority_': 1},
                          conflict_resolving_strategy='ALL',
                          priority_attribute='_priority_',
                          ambiguous=True
                          )
    text = new_text(5)
    tagger.tag(text)

    layer = text['phrases']
    assert layer.letter == AmbiguousAttributeList([['B'], ['A', 'C'], ['D']], 'letter')
    assert layer.number == AmbiguousAttributeList([[2], [1, 3], [4]], 'number')
    assert layer._priority_ == AmbiguousAttributeList([[0], [0, 0], [0]], '_priority_')
    assert layer.attr_1 == AmbiguousAttributeList([['default_1'], ['default_1', 'default_1'], ['default_1']], 'attr_1')
    assert layer.attr_2 == AmbiguousAttributeList([[1], [2, 2], [3]], 'attr_2')
