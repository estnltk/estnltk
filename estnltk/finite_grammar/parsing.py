from typing import Sequence
from collections import defaultdict
import regex as re

from .grammar import Grammar, Rule
from .layer_graph import LayerGraph, NonTerminalNode, PlusNode


def get_match_up(graph, nodes, names, pos):
    if pos == 0:
        yield nodes
        return
    for node in graph.pred[nodes[-1]]:
        if node.name == names[pos-1]:
            yield from get_match_up(graph, nodes + [node], names, pos - 1)


def get_match_down(graph, nodes, names, pos):
    if pos + 1 == len(names):
        yield nodes
        return
    for node in graph.succ[nodes[-1]]:
        if node.name == names[pos+1]:
            yield from get_match_down(graph, nodes+[node], names, pos+1)


def get_match(graph: LayerGraph, node: NonTerminalNode, names: Sequence[str], pos: int):
    """
    Yields all sequences s of consecutive nodes in the graph G for which
        s[pos] == node and [node.name for node in s]==names.
    """
    # generator of all preceding sequences of the node (that also include the node)
    match_up = get_match_up(graph, [node], names, pos)
    # all succeeding sequences of the node (that also include the node)
    # this is stored as a list since we may iterate over it several times
    match_down = list(get_match_down(graph, [node], names, pos))
    assert all(md[0].name == names[pos] for md in match_down)
    yield from (mu[:0:-1]+md for mu in match_up for md in match_down)


def add_nodes(graph, nodes_to_add, resolve_conflicts):
    added_nodes = set()
    for node, predecessors, successors in nodes_to_add:
        if resolve_conflicts:
            nodes_to_remove = set()
            add_node = True
            for fellow in {p for s in node._support_ for p in graph.parse_trees.pred[s]}:
                if node._group_ == fellow._group_:
                    if fellow._priority_ < node._priority_:
                        add_node = False
                        break
                    elif node._priority_ < fellow._priority_:
                        nodes_to_remove.add(fellow)
            if add_node:
                added_nodes.add(node)
                added_nodes -= nodes_to_remove
                graph.remove_nodes_from(nodes_to_remove)
            else:
                continue

        added_nodes.add(node)
        for pred in predecessors:
            graph.add_edge(pred, node)
        for succ in successors:
            graph.add_edge(node, succ)
    return added_nodes

# seq_reg = re.compile('(SEQ|REP)\((.*)\)$')


def parse_graph(graph: LayerGraph,
                grammar: Grammar,
                depth_limit: int=None,
                width_limit: int=None,
                resolve_conflicts=True,
                debug: bool=False,
                ignore_validators: bool=False) -> LayerGraph:
    """
    Expands graph bottom-up using grammar. Changes the input graph.
    """
    if depth_limit is None:
        depth_limit = grammar.depth_limit
    if width_limit is None:
        width_limit = grammar.width_limit
    rule_map = grammar.rule_map
    hidden_rule_map = grammar.hidden_rule_map

    worklist = None
    if depth_limit > 0:
        worklist = [(n, 0) for n in graph if n.name in set(rule_map)|set(hidden_rule_map)]

    while worklist:
        node, d = worklist.pop()
        # expand fragment
        nodes_to_add = []
        for rule, pos in rule_map[node.name]:
            if debug:
                print('rule:', rule)
            no_match = True
            for support in get_match(graph, node, rule.rhs, pos):
                support = tuple(support)
                if debug:
                    no_match = False
                    print('match:', support)
                assert all((support[i], support[i+1]) in graph.edges for i in range(len(support) - 1))
                if ignore_validators or rule.validator(support):
                    new_node = NonTerminalNode(rule, support)
                    if len(new_node._terminals_) <= width_limit:
                        decoration = rule.decorator(support)
                        assert not (set(decoration) - grammar.legal_attributes),\
                            'illegal attributes in decorator output: ' + str(set(decoration) - grammar.legal_attributes)
                        new_node.decoration = decoration

                        nodes_to_add.append((new_node,
                                             list(graph.pred[support[0]]),
                                             list(graph.succ[support[-1]]),
                                             ))
                        if debug:
                            print('new node:')
                            node.print()
                elif debug:
                    print('validator returned False')
            if debug and no_match:
                print('no match')

        # expand with hidden rules
        for rule, pos in hidden_rule_map.get(node.name, []):
            for support in get_match(graph, node, rule.rhs, pos):
                support = tuple(support)

                assert all((support[i], support[i + 1]) in graph.edges for i in range(len(support) - 1))
                new_node = PlusNode(rule, support)
                if len(new_node._terminals_) < width_limit:
                    decoration = rule.decorator(support)
                    assert not (set(decoration) - grammar.legal_attributes), \
                        'illegal attributes in decorator output: ' + str(set(decoration) - grammar.legal_attributes)
                    new_node.decoration = decoration

                    nodes_to_add.append((new_node,
                                         list(graph.pred[support[0]]),
                                         list(graph.succ[support[-1]]),
                                         ))
                    if debug:
                        print('new node:')
                        node.print()

        added_nodes = add_nodes(graph, nodes_to_add, resolve_conflicts)
        if d < depth_limit:
            for node in added_nodes:
                if node.name in rule_map:
                    worklist.append((node, d+1))
    return graph


def _resolve_conflicts(graph, node_names):
    start_symbols = set(node_names)
    terminals_to_nodes = defaultdict(set)
    for node in graph:
        if node.name in start_symbols:
            for terminal in node._terminals_:
                terminals_to_nodes[(terminal, node._group_)].add(node)

    conflicting = {}
    for nodes in terminals_to_nodes.values():
        if len(nodes) > 1:
            for node in nodes:
                conflicting[node] = {n for n in nodes if n._priority_ > node._priority_}
    nodes_to_remove = set()
    for node in sorted(conflicting, key=lambda n: n._priority_):
        if node not in nodes_to_remove:
            nodes_to_remove.update(conflicting[node])

    graph.remove_nodes_from(nodes_to_remove)

    return graph


def debug_rule(graph, rule, max_depth: int=float('inf')):
    grammar = Grammar(start_symbols=[rule.lhs], rules=[rule], depth_limit=max_depth)
    parse_graph(graph, grammar, debug=True)
