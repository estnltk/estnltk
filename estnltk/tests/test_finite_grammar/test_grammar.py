import pytest
from estnltk.finite_grammar import Rule, Grammar


def test_Rule():
    rule = Rule('A', ['B', 'SEQ(C)'], 10, 'group', lambda x: {'decorator': True}, lambda x: False, lambda x: 0.5)
    assert rule.lhs == 'A'
    assert rule.rhs == ('B', 'SEQ(C)')
    assert rule.priority == 10
    assert rule.group == 'group'
    assert rule.decorator(None) == {'decorator': True}
    assert rule.validator(None) == False
    assert rule.scoring(None) == 0.5

    with pytest.raises(AssertionError):
        Rule('(', 'B')
    with pytest.raises(AssertionError):
        Rule('A', ')')


def test_Rule_defaults():
    rule = Rule('A', 'B REP(C)')
    assert rule.lhs == 'A'
    assert rule.rhs == ('B', 'REP(C)')
    assert rule.priority == 0
    assert rule.group
    assert rule.decorator(None) == {}
    assert rule.validator(None) == True
    assert rule.scoring(None) == 0


def test_Grammar():
    grammar = Grammar(['S'], None, 5, 20, {'attr_1', 'attr_2'})
    grammar.add(Rule('S', 'A'))
    grammar.add(Rule('S', 'B'))
    grammar.add(Rule('A', 'B F'))
    grammar.add(Rule('B', 'G'))

    assert grammar.start_symbols == ('S',)
    assert len(grammar.rules) == 4
    assert grammar.depth_limit == 5
    assert grammar.width_limit == 20
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


def test_Grammar_defaults():
    grammar = Grammar()
    assert grammar.start_symbols == ()
    assert grammar.rules == []
    assert grammar.depth_limit == float('inf')
    assert grammar.width_limit == float('inf')
    assert grammar.legal_attributes == frozenset()
