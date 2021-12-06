from estnltk.taggers import AdjectivePhraseTagger
from estnltk import Text
from estnltk_core.converters import layer_to_records

def test_adjective_phrase_tagger():
    text = Text("Eile leitud koer oli väga energiline ja mänguhimuline.").analyse('morphology')

    tagger = AdjectivePhraseTagger()
    tagger.tag(text)

    assert layer_to_records( text.grammar_tags ) == [
        [{'grammar_symbol': 'ADV2', 'start': 0, 'end': 4}],
         [{'grammar_symbol': 'ADJ', 'start': 5, 'end': 11}],
         [{'grammar_symbol': 'RANDOM_TEXT', 'start': 12, 'end': 20}],
         [{'grammar_symbol': 'ADJ_M', 'start': 21, 'end': 25},
          {'grammar_symbol': 'ADV2', 'start': 21, 'end': 25}],
         [{'grammar_symbol': 'ADJ', 'start': 26, 'end': 36}],
         [{'grammar_symbol': 'CONJ', 'start': 37, 'end': 39}],
         [{'grammar_symbol': 'ADJ', 'start': 40, 'end': 53}],
         [{'grammar_symbol': 'RANDOM_TEXT', 'start': 53, 'end': 54}]]

    assert layer_to_records( text.adjective_phrases ) == [
        [[{'grammar_symbol': 'ADJ', 'start': 5, 'end': 11}]],
        [[{'grammar_symbol': 'ADJ_M', 'start': 21, 'end': 25},
          {'grammar_symbol': 'ADV2', 'start': 21, 'end': 25}],
         [{'grammar_symbol': 'ADJ', 'start': 26, 'end': 36}],
         [{'grammar_symbol': 'CONJ', 'start': 37, 'end': 39}],
         [{'grammar_symbol': 'ADJ', 'start': 40, 'end': 53}]]]
