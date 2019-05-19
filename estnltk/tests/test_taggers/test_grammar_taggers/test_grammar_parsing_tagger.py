import pytest

from estnltk import Text, Layer
from estnltk.taggers import GrammarParsingTagger
from estnltk.finite_grammar import Grammar


def test_raises_error():
    text = Text('Jüri Homenja kontsert toimub E, 22. mai kl 18:00 kultuurimajas Veski 5, Elva, Tartumaa.')

    layer = Layer(name='address_parts', text_object=text, attributes=['grammar_symbol'], ambiguous=True)

    layer.add_annotation((63, 68), grammar_symbol='TÄNAV')
    layer.add_annotation((69, 70), grammar_symbol='MAJA')

    text['address_parts'] = layer

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
