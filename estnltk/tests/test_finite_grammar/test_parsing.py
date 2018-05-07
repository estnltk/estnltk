from estnltk.finite_grammar import Grammar, Rule, parse_graph
from estnltk.finite_grammar.layer_graph import layer_to_graph
from estnltk.tests.helpers.text_objects import text_3


def test_parse_graph():
    # simple rules, no validators, decorators, scoring
    grammar = Grammar()
    grammar.add(Rule('E', 'A B C D'))

    grammar.add(Rule('F', 'A B'))
    grammar.add(Rule('G', 'B C'))
    grammar.add(Rule('H', 'C D'))

    grammar.add(Rule('I', 'F G'))
    grammar.add(Rule('J', 'F H'))

    graph = layer_to_graph(text_3['layer_0'], text_3.text, name_attribute='attr_0')
    graph = parse_graph(graph,
                        grammar,
                        resolve_support_conflicts=False,
                        resolve_start_end_conflicts=False,
                        resolve_terminals_conflicts=False,
                        debug=False)
    assert [(a.name, b.name) for a, b in sorted(graph.edges)] == [#('START', 'A'),
                                                                 #('START', 'F'),
                                                                 #('START', 'E'),
                                                                 #('START', 'J'),
                                                                 ('A', 'B'),
                                                                 ('A', 'G'),
                                                                 ('F', 'C'),
                                                                 ('F', 'H'),
                                                                 #('E', 'END'),
                                                                 #('J', 'END'),
                                                                 ('B', 'C'),
                                                                 ('B', 'H'),
                                                                 ('G', 'D'),
                                                                 ('C', 'D'),
                                                                 #('H', 'END'),
                                                                 #('D', 'END')
                                                                 ]


def test_parse_graph_SEQ():
    # test sequence rule
    grammar = Grammar()
    grammar.add(Rule('E', 'A'))
    grammar.add(Rule('F', 'B'))
    grammar.add(Rule('F', 'C'))
    grammar.add(Rule('G', 'D'))
    grammar.add(Rule('H', 'E SEQ(F) G'))

    graph = layer_to_graph(text_3['layer_0'], text_3.text, name_attribute='attr_0')
    graph = parse_graph(graph,
                        grammar,
                        resolve_support_conflicts=False,
                        resolve_start_end_conflicts=False,
                        resolve_terminals_conflicts=False,
                        debug=False)
    assert [(a.name, b.name) for a, b in sorted(graph.edges)] == [#('START', 'A'),
                                                                 #('START', 'E'),
                                                                 #('START', 'H'),
                                                                 ('A', 'B'),
                                                                 ('A', 'F'),
                                                                 ('A', 'SEQ(F)'),
                                                                 ('A', 'SEQ(F)'),
                                                                 ('E', 'B'),
                                                                 ('E', 'F'),
                                                                 ('E', 'SEQ(F)'),
                                                                 ('E', 'SEQ(F)'),
                                                                 #('H', 'END'),
                                                                 ('B', 'C'),
                                                                 ('B', 'F'),
                                                                 ('B', 'SEQ(F)'),
                                                                 ('F', 'C'),
                                                                 ('F', 'F'),
                                                                 ('F', 'SEQ(F)'),
                                                                 ('SEQ(F)', 'C'),
                                                                 ('SEQ(F)', 'F'),
                                                                 ('SEQ(F)', 'SEQ(F)'),
                                                                 ('SEQ(F)', 'D'),
                                                                 ('SEQ(F)', 'G'),
                                                                 ('C', 'D'),
                                                                 ('C', 'G'),
                                                                 ('F', 'D'),
                                                                 ('F', 'G'),
                                                                 ('SEQ(F)', 'D'),
                                                                 ('SEQ(F)', 'G'),
                                                                 #('D', 'END'),
                                                                 #('G', 'END')
                                                                 ]


def test_parse_graph_support_conflicts():
    # test sequence rule
    grammar = Grammar()
    grammar.add(Rule('E', 'A B', group='g1', priority=2))
    grammar.add(Rule('F', 'B C', group='g1', priority=1))
    grammar.add(Rule('G', 'C D', group='g1', priority=0))

    grammar.add(Rule('K', 'A B', group='g2', priority=0))
    grammar.add(Rule('L', 'B C', group='g2', priority=1))
    grammar.add(Rule('M', 'C D', group='g2', priority=2))

    graph = layer_to_graph(text_3['layer_0'], text_3.text, name_attribute='attr_0')
    graph = parse_graph(graph,
                        grammar,
                        resolve_support_conflicts=True,
                        resolve_start_end_conflicts=False,
                        resolve_terminals_conflicts=False,
                        debug=False)
    assert [(a.name, b.name) for a, b in sorted(graph.edges)] == [#('START', 'A'),
                                                                 #('START', 'K'),
                                                                 ('A', 'B'),
                                                                 ('K', 'C'),
                                                                 ('K', 'G'),
                                                                 ('K', 'M'),
                                                                 ('B', 'C'),
                                                                 ('B', 'G'),
                                                                 ('B', 'M'),
                                                                 ('C', 'D'),
                                                                 #('G', 'END'),
                                                                 #('M', 'END'),
                                                                 #('D', 'END')
                                                                 ]


def test_parse_graph_start_end_conflicts():
    # test sequence rule
    grammar = Grammar()
    grammar.add(Rule('E', 'A B', group='g1', priority=2))
    grammar.add(Rule('F', 'B C', group='g1', priority=1))
    grammar.add(Rule('G', 'C D', group='g1', priority=0))

    grammar.add(Rule('K', 'A B', group='g2', priority=0))
    grammar.add(Rule('L', 'B C', group='g2', priority=1))
    grammar.add(Rule('M', 'C D', group='g2', priority=2))

    graph = layer_to_graph(text_3['layer_0'], text_3.text, name_attribute='attr_0')
    graph = parse_graph(graph,
                        grammar,
                        resolve_support_conflicts=True,
                        resolve_start_end_conflicts=False,
                        resolve_terminals_conflicts=False,
                        debug=False)
    assert [(a.name, b.name) for a, b in sorted(graph.edges)] == [#('START', 'A'),
                                                                 #('START', 'K'),
                                                                 ('A', 'B'),
                                                                 ('K', 'C'),
                                                                 ('K', 'G'),
                                                                 ('K', 'M'),
                                                                 ('B', 'C'),
                                                                 ('B', 'G'),
                                                                 ('B', 'M'),
                                                                 ('C', 'D'),
                                                                 #('G', 'END'),
                                                                 #('M', 'END'),
                                                                 #('D', 'END')
                                                                 ]
