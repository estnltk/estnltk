from typing import Sequence
from collections import defaultdict

from .grammar import Grammar
from .layer_graph import LayerGraph, GrammarNode, NonTerminalNode, PlusNode


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


def add_nodes(graph: LayerGraph,
              nodes_to_add,
              resolve_support_conflicts: bool,
              resolve_start_end_conflicts: bool,
              resolve_terminals_conflicts: bool):
    """Add nodes to the graph and resolve the conflicts.

    resolve_support_conflicts
        Two nodes are in 'support' conflict if they have intersecting supports and the same group but different
        priorities. The node with the higher priority (smaller value) is kept.
    resolve_start_end_conflicts
        Two nodes are in 'start end' conflict if they have the same start, end and name but different score.
        The node with the higher score value is kept.
    resolve_terminals_conflicts
        Two nodes are in 'terminals' conflict if they have the same terminals and name but different score.
        The node with the higher score value is kept.
        If resolve_terminals_conflicts is True, then the value of resolve_start_end_conflicts has no effect.
    For equal scores/priorities both nodes are kept.
    """
    added_nodes = set()
    for node, predecessors, successors in nodes_to_add:
        if node in graph:
            continue
        add_node = True
        nodes_to_remove = set()

        if resolve_support_conflicts:
            for fellow in {p for s in node.support for p in graph.parse_trees.pred[s]}:
                if node.group == fellow.group:
                    if fellow.priority < node.priority:
                        add_node = False
                        break
                    elif node.priority < fellow.priority:
                        nodes_to_remove.add(fellow)

        if add_node and (resolve_start_end_conflicts or resolve_terminals_conflicts):
            for n in graph.map_start_end_to_nodes[(node.start, node.end)]:
                if isinstance(n, GrammarNode) and n.name == node.name:
                    if resolve_start_end_conflicts or n.terminals == node.terminals:
                        if n.score > node.score:
                            add_node = False
                            break
                        elif n.score < node.score:
                            nodes_to_remove.add(n)
        if add_node:
            added_nodes.add(node)
            added_nodes -= nodes_to_remove
            graph.remove_nodes_from(nodes_to_remove)

            for pred in predecessors:
                graph.add_edge(pred, node)
            for succ in successors:
                graph.add_edge(node, succ)
    return added_nodes


def parse_graph(graph: LayerGraph,
                grammar: Grammar,
                depth_limit: int = None,
                width_limit: int = None,
                resolve_support_conflicts: bool = True,  # by priority
                resolve_start_end_conflicts: bool = True,  # by score
                resolve_terminals_conflicts: bool = True,  # by score
                ignore_validators: bool = False,
                debug: bool = False) -> LayerGraph:
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
        worklist = [(n, 0) for n in sorted(graph, reverse=True) if n.name in set(rule_map)|set(hidden_rule_map)]

    while worklist:
        if debug:
            print()
            print('worklist:', [(n.name, d) for n, d in worklist])
        node, d = worklist.pop()
        assert node in graph, 'Node in worklist, but not in graph. This should not happen.'
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
                    if len(new_node.terminals) <= width_limit:
                        node_attributes = rule.decorator(support)
                        assert not (set(node_attributes) - grammar.legal_attributes),\
                            'illegal attributes in decorator output: ' + str(set(node_attributes) - grammar.legal_attributes)
                        new_node.attributes = node_attributes

                        nodes_to_add.append((new_node,
                                             list(graph.pred[support[0]]),
                                             list(graph.succ[support[-1]]),
                                             ))
                        if debug:
                            print('new node:')
                            new_node.print()
                elif debug:
                    print('validator returned False')
            if debug and no_match:
                print('no match')

        # expand with hidden rules
        for rule, pos in hidden_rule_map.get(node.name, []):
            if debug:
                print('rule:', rule)
                no_match = True
            for support in get_match(graph, node, rule.rhs, pos):
                support = tuple(support)
                if debug:
                    no_match = False

                assert all((support[i], support[i + 1]) in graph.edges for i in range(len(support) - 1))
                new_node = PlusNode(rule, support)
                if len(new_node.terminals) < width_limit:
                    node_attributes = rule.decorator(support)
                    assert not (set(node_attributes) - grammar.legal_attributes), \
                        'illegal attributes in decorator output: ' + str(set(node_attributes) - grammar.legal_attributes)
                    new_node.decoration = node_attributes

                    nodes_to_add.append((new_node,
                                         list(graph.pred[support[0]]),
                                         list(graph.succ[support[-1]]),
                                         ))
                    if debug:
                        print('new node:')
                        new_node.print()
            if debug and no_match:
                print('no match')

        added_nodes = add_nodes(graph,
                                nodes_to_add,
                                resolve_support_conflicts,
                                resolve_start_end_conflicts,
                                resolve_terminals_conflicts)
        if d < depth_limit:
            for node in added_nodes:
                if node.name in set(rule_map)|set(hidden_rule_map):
                    worklist.append((node, d+1))
    return graph


def _resolve_conflicts(graph, node_names):
    start_symbols = set(node_names)
    terminals_to_nodes = defaultdict(set)
    for node in graph:
        if node.name in start_symbols:
            for terminal in node.terminals:
                terminals_to_nodes[(terminal, node.group)].add(node)

    conflicting = {}
    for nodes in terminals_to_nodes.values():
        if len(nodes) > 1:
            for node in nodes:
                conflicting[node] = {n for n in nodes if n.priority > node.priority}
    nodes_to_remove = set()
    for node in sorted(conflicting, key=lambda n: n.priority):
        if node not in nodes_to_remove:
            nodes_to_remove.update(conflicting[node])

    graph.remove_nodes_from(nodes_to_remove)

    return graph


def debug_rule(graph, rule, max_depth: int=float('inf')):
    grammar = Grammar(start_symbols=[rule.lhs], rules=[rule], depth_limit=max_depth)
    parse_graph(graph, grammar, debug=True)
