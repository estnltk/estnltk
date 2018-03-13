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
                        validator_attribute='_validator_',
                        priority_attribute=None,
                        ambiguous=False
                        )
    text = new_text(5)
    tagger.tag(text)

    expected = [
        {'number': 1, 'letter': 'A', 'start': 9, 'end': 14, '_priority_': 0},
        {'number': 2, 'letter': 'B', 'start': 22, 'end': 27, '_priority_': 1},
        {'number': 3, 'letter': 'C', 'start': 22, 'end': 27, '_priority_': 1}
    ]
    assert expected==text['tagged_tokens'].to_records()
