from os.path import dirname, join

from estnltk.taggers import PhraseTagger
from estnltk.tests.helpers.text_objects import new_text


def test_basic():
    vocabulary = join(dirname(__file__), 'phrase_vocabulary.csv')
    tagger = PhraseTagger(output_layer='phrases',
                          input_layer='layer_0',
                          input_attribute='attr',
                          vocabulary=vocabulary,
                          key='_phrase_',
                          output_attributes=['number', 'letter', '_priority_'],
                          conflict_resolving_strategy='ALL',
                          priority_attribute=None,
                          ambiguous=True
                          )
    text = new_text(5)
    tagger.tag(text)

    assert text['phrases'].letter == [['B'], ['A', 'C'], ['D']]
    assert text['phrases'].number == [[2], [1, 3], [4]]
    assert text['phrases']._priority_ == [[0], [0, 0], [0]]
