from os.path import dirname, join

from estnltk import Text
from estnltk.taggers import SpanTagger
from estnltk_core.tests.helpers.text_objects import new_text


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


def test_ambiguous_input_layer():
    vocabulary = join(dirname(__file__), 'test_span_vocabulary_2.csv')
    tagger = SpanTagger(output_layer='tagged_tokens',
                        input_layer='morph_analysis',
                        input_attribute='lemma',
                        vocabulary=vocabulary,
                        output_attributes=['value', '_priority_'],  # default: None
                        key='_token_',  # default: '_token_'
                        validator_attribute=None,  # the default:
                        ambiguous=True  # default: False
                        )
    text = Text('Eestimaal tunnevad inimesed palju puudust päikesest ja energiast.').tag_layer(['morph_analysis'])
    tagger.tag(text)
    assert text.tagged_tokens.to_records() == [
        [{'value': 'T', '_priority_': 1, 'start': 10, 'end': 18}],
        [{'value': 'K', '_priority_': 2, 'start': 19, 'end': 27},
         {'value': 'I', '_priority_': 3, 'start': 19, 'end': 27}],
        [{'value': 'P', '_priority_': 2, 'start': 42, 'end': 51}]]


def test_not_case_sensitive():
    text = Text('Suur ja väike.').tag_layer(['words'])
    comma_tagger = SpanTagger(input_layer='words',
                              output_layer='size',
                              ambiguous=True,
                              input_attribute='text',
                              output_attributes=[],
                              key='_token_',
                              vocabulary=[{'_token_': 'SUUR'}, {'_token_': 'väike'}],
                              case_sensitive=False
                              )
    comma_tagger.tag(text)

    assert text.size.to_records() == [[{'start': 0, 'end': 4}], [{'start': 8, 'end': 13}]]