from estnltk.taggers.system.grammar_taggers.finite_grammar.layer_graph import Node, PhonyNode, GrammarNode, TerminalNode
from estnltk.taggers.system.grammar_taggers.finite_grammar.layer_graph import layer_to_graph
from estnltk_core.tests.helpers.text_objects import text_5


def test_Node():
    node_1 = Node('TEST_1', 2, 6)
    node_2 = Node('TEST_2', 4, 8)

    assert node_1.name == 'TEST_1'
    assert node_1.start == 2
    assert node_1.end == 6

    assert node_1 < node_2
    assert node_2 > node_1

    assert Node('TEST_1', 2, 6) < Node('TEST_2', 2, 6)
    assert Node('TEST_2', 2, 6) > Node('TEST_1', 2, 6)

    assert Node('TEST_1', 1, 6) < Node('TEST_1', 2, 6)
    assert Node('TEST_1', 2, 6) > Node('TEST_1', 1, 6)


def test_PhonyNode():
    node_1 = PhonyNode('TEST_1', 2, 6)
    node_2 = PhonyNode('TEST_2', 4, 8)
    node_3 = PhonyNode('TEST_2', 4, 8)

    assert hash(node_1) != hash(node_2)
    assert hash(node_2) == hash(node_3)

    assert node_1 != node_2
    assert node_2 == node_3


def test_TerminalNode():
    span_1 = text_5.layer_0[0]
    node_1 = TerminalNode(span_1.attr_0, span_1, attributes={'attr', 'attr_0'})
    assert node_1.name == span_1.attr_0
    assert node_1.start == span_1.start
    assert node_1.end == span_1.end
    assert node_1.span is span_1
    assert node_1 == node_1
    assert node_1['attr'] == span_1.attr
    assert node_1['attr_0'] == span_1.attr_0

    span_2 = text_5.layer_0[1]
    node_2 = TerminalNode(span_2.attr_0, span_2)
    assert node_2 != node_1
    assert node_2['attr'] == span_2.attr
    assert node_2['attr_0'] == span_2.attr_0


def test_GrammarNode():
    span_0 = text_5.layer_0[0]
    span_1 = text_5.layer_0[1]
    t_0 = TerminalNode('A', span_0)
    t_1 = TerminalNode('B', span_1)
    node_1 = GrammarNode('TEST_1', [t_0, t_1])
    node_2 = GrammarNode('TEST_1', [t_0, t_1])
    node_3 = GrammarNode('TEST_3', [t_0])
    node_4 = GrammarNode('TEST_3', [t_1])
    assert node_1 == node_2
    assert node_1 != node_3
    assert node_3 != node_4


def test_layer_to_graph():
    graph = layer_to_graph(text_5['layer_0'], text_5.text, name_attribute='attr')
    assert len(graph) == 20
    assert [(a.name, b.name) for a, b in sorted(graph.edges)] == [('L0-0', 'L0-1'),
                                                                  ('L0-0', 'L0-2'),
                                                                  ('L0-1', 'L0-3'),
                                                                  ('L0-2', 'L0-4'),
                                                                  ('L0-3', 'L0-4'),
                                                                  ('L0-4', 'L0-5'),
                                                                  ('L0-5', 'L0-6'),
                                                                  ('L0-6', 'L0-7'),
                                                                  ('L0-6', 'L0-8'),
                                                                  ('L0-7', 'L0-9'),
                                                                  ('L0-8', 'L0-10'),
                                                                  ('L0-8', 'L0-11'),
                                                                  ('L0-9', 'L0-10'),
                                                                  ('L0-9', 'L0-11'),
                                                                  ('L0-10', 'L0-12'),
                                                                  ('L0-11', 'L0-13'),
                                                                  ('L0-12', 'L0-13'),
                                                                  ('L0-13', 'L0-14'),
                                                                  ('L0-14', 'L0-15'),
                                                                  ('L0-15', 'L0-16'),
                                                                  ('L0-15', 'L0-17'),
                                                                  ('L0-16', 'L0-18'),
                                                                  ('L0-17', 'L0-19'),
                                                                  ('L0-18', 'L0-19')
                                                                  ]
