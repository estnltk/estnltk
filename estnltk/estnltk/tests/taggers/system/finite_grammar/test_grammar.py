import pytest
from estnltk.taggers.system.grammar_taggers.finite_grammar import Rule, Grammar
from estnltk.taggers.system.grammar_taggers.finite_grammar import match_SEQ_pattern


def test_match_SEQ_pattern():
    assert 'bla' == match_SEQ_pattern('SEQ(bla)')
    assert None is match_SEQ_pattern('MSEQ()')


def test_Rule():
    rule = Rule('A', ['B', 'SEQ(C)'], 10, 'group', lambda x: {'decorator': True}, lambda x: False, lambda x: 0.5)
    assert rule.lhs == 'A'
    assert rule.rhs == ('B', 'SEQ(C)')
    assert rule.priority == 10
    assert rule.group == 'group'
    assert rule.decorator(None) == {'decorator': True}
    assert rule.validator(None) is False
    assert rule.scoring(None) == 0.5

    with pytest.raises(AssertionError):
        Rule('(', 'B')
    with pytest.raises(AssertionError):
        Rule('A', ')')


def test_Rule_defaults():
    rule = Rule('A', 'B SEQ(C)')
    assert rule.lhs == 'A'
    assert rule.rhs == ('B', 'SEQ(C)')
    assert rule.priority == 0
    assert rule.group
    assert rule.decorator(None) == {}
    assert rule.validator(None) is True
    assert rule.scoring(None) == 0


def test_Grammar():
    grammar = Grammar(['S'], None, 5, 20, {'attr_1', 'attr_2'})
    grammar.add(Rule('S', 'A'))
    grammar.add(Rule('S', 'B'))
    grammar.add(Rule('A', 'B F'))
    grammar.add(Rule('B', 'G'))

    assert grammar.start_symbols == ('S',)
    assert 4 == len(grammar.rules)
    assert {'F', 'G'} == grammar.terminals
    assert {'A', 'B', 'S'} == grammar.nonterminals
    assert 5 == grammar.depth_limit
    assert 20 == grammar.width_limit
    assert grammar.legal_attributes == frozenset({'attr_1', 'attr_2'})
    assert grammar.hidden_rule_map == {}
    assert grammar.has_finite_max_depth()

    grammar.add(Rule('B', 'SEQ(D)'))
    assert len(grammar.rules) == 5
    assert len(grammar.hidden_rule_map) == 2
    assert grammar.has_finite_max_depth()

    grammar.add(Rule('G', 'A B'))
    assert not grammar.has_finite_max_depth()

    grammar = Grammar([])
    grammar.add(Rule('A', 'A B'))
    with pytest.raises(AssertionError):
        grammar.rules

    grammar = Grammar([])
    grammar.add(Rule('A', 'SEQ(A)'))
    with pytest.raises(AssertionError):
        grammar.rules

    grammar = Grammar()
    grammar.add(Rule('A', 'SEQ(B)'))
    assert len(grammar.rules) == 1
    assert {'B'} == grammar.terminals
    assert {'A', 'SEQ(B)'} == grammar.nonterminals


def test_Grammar_defaults():
    grammar = Grammar()
    assert grammar.start_symbols == ()
    assert grammar.rules == []
    assert grammar.depth_limit == float('inf')
    assert grammar.width_limit == float('inf')
    assert grammar.legal_attributes == frozenset()
