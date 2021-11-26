import pytest

from estnltk import Text, Layer
from estnltk.taggers import GrammarParsingTagger
from estnltk.taggers.system.grammar_taggers.finite_grammar import Grammar


def test_raises_error():
    text = Text('Jüri Homenja kontsert toimub E, 22. mai kl 18:00 kultuurimajas Veski 5, Elva, Tartumaa.')

    layer = Layer(name='address_parts', text_object=text, attributes=['grammar_symbol'], ambiguous=True)

    layer.add_annotation((63, 68), grammar_symbol='TÄNAV')
    layer.add_annotation((69, 70), grammar_symbol='MAJA')

    text.add_layer(layer)

    grammar = Grammar(start_symbols=['ADDRESS1', 'ADDRESS2'])
    grammar.add_rule('ADDRESS1', 'TÄNAV MAJA')
    grammar.add_rule('ADDRESS2', 'TÄNAV MAJA')

    tagger = GrammarParsingTagger(grammar=grammar,
                                  layer_of_tokens='address_parts',
                                  output_layer='addresses',
                                  output_ambiguous=False,
                                  attributes=['_group_']
                                  )
    with pytest.raises(ValueError) as e:
        tagger(text)

    assert e.value.args[0] == 'there exists an ambiguous span among output nodes of the grammar, ' \
                              'make the output layer ambiguous by setting output_ambiguous=True ' \
                              'or adjust grammar by changing priority, scoring and lhs parameters of rules'



def test_force_resolving_by_priority():
    # Example text snippet
    text = Text('Lendur. Lenduri diivani tugijalg. Lenduri diivani tugi ja jalg.'
                'Lendur Leo. Lendur Leo diivan. Leo ja Matthias.').tag_layer('morph_analysis')

    # Create Grammar for capturing noun phrase candidates
    grammar = Grammar(start_symbols=['NOUN_PHRASE'], 
                      depth_limit=float('inf'), # the default
                      width_limit=float('inf'), # the default
                      )
    grammar.add_rule('NOUN', 'S', group='g0', priority=4)
    grammar.add_rule('NOUN', 'H', group='g0', priority=4)
    grammar.add_rule('NOUN_PHRASE', 'NOUN',        group='g0', priority=4)
    grammar.add_rule('NOUN_PHRASE', 'MSEQ(NOUN)',  group='g0', priority=3)
    grammar.add_rule('NOUN_PHRASE', 'NOUN J NOUN', group='g0', priority=2)
    grammar.add_rule('NOUN_PHRASE', 'MSEQ(NOUN) J NOUN', group='g0', priority=1)

    # Create & apply GrammarParsingTagger with force_resolving_by_priority=True
    grammar_tagger = GrammarParsingTagger(grammar=grammar,
                                          name_attribute='partofspeech',
                                          layer_of_tokens='morph_analysis',
                                          output_layer='noun_phrases',
                                          force_resolving_by_priority=True)
    grammar_tagger.tag(text)
    expected_phrases = \
       ['Lendur', 'Lenduri diivani tugijalg', 'Lenduri diivani tugi ja jalg', 
        'Lendur Leo', 'Lendur Leo diivan', 'Leo ja Matthias']
    expected_phrase_spans = \
        [(0, 6), (8, 32), (34, 62), (63, 73), (75, 92), (94, 109)]
    # Collect phrases & spans
    noun_phrases = [phrase.enclosing_text for phrase in text['noun_phrases']]
    noun_phrase_spans = [(phrase.start, phrase.end) for phrase in text['noun_phrases']]
    #print( noun_phrases )
    #print( noun_phrase_spans )
    # Check results
    assert expected_phrases == noun_phrases
    assert expected_phrase_spans == noun_phrase_spans

