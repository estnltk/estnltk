from os.path import dirname, join

from estnltk.taggers import PhraseTagger
from estnltk.tests.helpers.text_objects import new_text
from estnltk.layer import AmbiguousAttributeList

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

    assert text['phrases'].letter == AmbiguousAttributeList([['B'], ['A', 'C'], ['D']], 'letter')
    assert text['phrases'].number == AmbiguousAttributeList([[2], [1, 3], [4]], 'number')
    assert text['phrases']._priority_ == AmbiguousAttributeList([[0], [0, 0], [0]], '_priority_')
