from os.path import dirname, join

from estnltk.taggers import SpanTagger
from estnltk.tests.helpers.text_objects import new_text


def test_basic():
    vocabulary = join(dirname(__file__), 'span_vocabulary.csv')
    tagger = SpanTagger(output_layer='tagged_tokens',
                        input_layer='layer_0',
                        input_attribute='attr',
                        vocabulary=vocabulary,
                        output_attributes=['number', 'letter', '_priority_'],
                        key='_token_',
                        validator_attribute=None,
                        priority_attribute=None,
                        ambiguous=True
                        )
    text = new_text(5)
    tagger.tag(text)

    expected = [
     [{'letter': 'A', 'end': 14, 'number': 1, 'start': 9, '_priority_': 0}],
     [{'letter': 'B', 'end': 27, 'number': 2, 'start': 22, '_priority_': 1},
      {'letter': 'C', 'end': 27, 'number': 3, 'start': 22, '_priority_': 1}]]

    assert expected==text['tagged_tokens'].to_records()
