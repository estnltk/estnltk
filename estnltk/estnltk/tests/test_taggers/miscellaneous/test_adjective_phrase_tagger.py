from estnltk.taggers import AdjectivePhraseTagger
from estnltk import Text


def test_adjective_phrase_tagger():
    text = Text("Eile leitud koer oli väga energiline ja mänguhimuline.").analyse('morphology')

    tagger = AdjectivePhraseTagger()
    tagger.tag(text)

    assert text.grammar_tags.to_records() == [
        [{'grammar_symbol': 'ADV2', 'start': 0, 'end': 4}],
         [{'grammar_symbol': 'ADJ', 'start': 5, 'end': 11}],
         [{'grammar_symbol': 'RANDOM_TEXT', 'start': 12, 'end': 20}],
         [{'grammar_symbol': 'ADJ_M', 'start': 21, 'end': 25},
          {'grammar_symbol': 'ADV2', 'start': 21, 'end': 25}],
         [{'grammar_symbol': 'ADJ', 'start': 26, 'end': 36}],
         [{'grammar_symbol': 'CONJ', 'start': 37, 'end': 39}],
         [{'grammar_symbol': 'ADJ', 'start': 40, 'end': 53}],
         [{'grammar_symbol': 'RANDOM_TEXT', 'start': 53, 'end': 54}]]

    assert text.adjective_phrases.to_records() == [
        [[{'grammar_symbol': 'ADJ', 'start': 5, 'end': 11}]],
        [[{'grammar_symbol': 'ADJ_M', 'start': 21, 'end': 25},
          {'grammar_symbol': 'ADV2', 'start': 21, 'end': 25}],
         [{'grammar_symbol': 'ADJ', 'start': 26, 'end': 36}],
         [{'grammar_symbol': 'CONJ', 'start': 37, 'end': 39}],
         [{'grammar_symbol': 'ADJ', 'start': 40, 'end': 53}]]]
