from os import path

from estnltk.taggers import PhraseTagger
from estnltk_core.tests.helpers.text_objects import new_text
from estnltk_core.layer import AmbiguousAttributeList
from estnltk import Annotation


def decorator(span, annotation):
    assert isinstance(annotation, Annotation)
    assert span is annotation.span
    annotation['attr_1'] = 'default_1'
    annotation['attr_2'] = len(annotation.span)
    annotation['_priority_'] = 1
    return True


def test_basic():
    vocabulary = path.join(path.dirname(__file__), 'phrase_vocabulary.csv')
    tagger = PhraseTagger(output_layer='phrases',
                          input_layer='layer_0',
                          input_attribute='attr',
                          vocabulary=vocabulary,
                          key='_phrase_',
                          output_attributes=['number', 'letter', '_priority_', 'attr_1', 'attr_2'],
                          decorator=decorator,
                          conflict_resolving_strategy='ALL',
                          priority_attribute='_priority_',
                          output_ambiguous=True
                          )
    text = new_text(5)
    tagger.tag(text)

    layer = text['phrases']
    assert layer.letter == AmbiguousAttributeList([['B'], ['A', 'C'], ['D']], 'letter')
    assert layer.number == AmbiguousAttributeList([[2], [1, 3], [4]], 'number')
    assert layer._priority_ == AmbiguousAttributeList([[1], [1, 1], [1]], '_priority_')
    assert layer.attr_1 == AmbiguousAttributeList([['default_1'], ['default_1', 'default_1'], ['default_1']], 'attr_1')
    assert layer.attr_2 == AmbiguousAttributeList([[1], [2, 2], [3]], 'attr_2')
