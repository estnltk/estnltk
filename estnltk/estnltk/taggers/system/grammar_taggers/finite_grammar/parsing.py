import itertools
from typing import Sequence

from estnltk import logger
from estnltk.taggers.system.grammar_taggers.finite_grammar import Grammar
from estnltk.taggers.system.grammar_taggers.finite_grammar.layer_graph import LayerGraph, NonTerminalNode, PlusNode, MSeqNode


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
    match_up = list(get_match_up(graph, [node], names, pos))
    # all succeeding sequences of the node (that also include the node)
    # this is stored as a list since we may iterate over it several times
    match_down = list(get_match_down(graph, [node], names, pos))
    assert all(md[0].name == names[pos] for md in match_down)
    yield from (mu[:0:-1]+md for mu in match_up for md in match_down)


def add_node(graph: LayerGraph,
             node,
             resolve_support_conflicts: bool,
             resolve_start_end_conflicts: bool,
             resolve_terminals_conflicts: bool):
    """Try and add the node to the graph and resolve the conflicts.

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
    Returns: bool
        True, if the node is added to the graph
        False, if the node is already in the graph or it can not be added due to the conflicts
    """
    if node in graph:
        return False
    nodes_to_remove = set()

    if isinstance(node, NonTerminalNode) and not isinstance(node, PlusNode):
        if resolve_support_conflicts:
            for fellow in {p for s in node.support for p in graph.parse_trees.pred[s]}:
                if node.group == fellow.group:
                    if fellow.priority < node.priority:
                        return False
                    elif node.priority < fellow.priority:
                        nodes_to_remove.add(fellow)

        if resolve_start_end_conflicts or resolve_terminals_conflicts:
            for n in graph.map_start_end_to_nodes[(node.start, node.end)]:
                if n.name == node.name:
                    if resolve_start_end_conflicts or n.terminals == node.terminals:
                        if n.score > node.score:
                            return False
                        elif n.score < node.score:
                            nodes_to_remove.add(n)
    if isinstance(node, MSeqNode):
        supp = set(node.support)
        for fellow in {p for s in node.support for p in graph.parse_trees.pred[s]}:
            if isinstance(fellow, MSeqNode):
                if set(fellow.support) < supp:
                    nodes_to_remove.add(fellow)
                elif set(fellow.support) >= supp:
                    return False

    graph.remove_nodes_from(nodes_to_remove)
    for n in nodes_to_remove:
        logger.debug('removed node: {!r}'.format(n))

    graph.add_node(node)
    logger.debug('added node: {!r}'.format(node))
    for pred in graph.pred[node.support[0]]:
        graph.add_edge(pred, node)
    for succ in graph.succ[node.support[-1]]:
        graph.add_edge(node, succ)
    return True


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
    mseq_rule_map = grammar.mseq_rule_map

    worklist = None
    if depth_limit > 0:
        names_to_parse = set(rule_map) | set(hidden_rule_map) | set(mseq_rule_map)
        worklist = [(n, 0) for n in sorted(graph, reverse=True) if n.name in names_to_parse]

    while worklist:
        if debug:
            print(100*'-')
            print('worklist:', [(n.name, d) for n, d in worklist])
        node, d = worklist.pop()
        # the node might have been removed due to conflict resolving
        if node not in graph:
            continue

        nodes_1 = _expand_fragment(node, graph, grammar, rule_map, width_limit, NonTerminalNode, ignore_validators, debug)
        nodes_2 = _expand_fragment(node, graph, grammar, hidden_rule_map, width_limit, PlusNode, True, debug)
        nodes_3 = _expand_fragment(node, graph, grammar, mseq_rule_map, width_limit, MSeqNode, True, debug)

        for node in itertools.chain(nodes_1, nodes_2, nodes_3):
            node_added = add_node(graph,
                                  node,
                                  resolve_support_conflicts,
                                  resolve_start_end_conflicts,
                                  resolve_terminals_conflicts)
            if node_added and d < depth_limit and node.name in set(rule_map)|set(hidden_rule_map):
                worklist.append((node, d+1))
    return graph


def _expand_fragment(node, graph, grammar, rule_map, width_limit, node_class, ignore_validators, debug):
    for rule, pos in rule_map.get(node.name, []):
        if debug:
            print()
            print('rule:', rule)
            no_match = True
        for support in get_match(graph, node, rule.rhs, pos):
            support = tuple(support)
            if debug:
                no_match = False
                print('match:', support)
            assert all((support[i], support[i + 1]) in graph.edges for i in range(len(support) - 1))
            if ignore_validators or rule.validator(support):
                new_node = node_class(rule, support)
                if len(new_node.terminals) <= width_limit:
                    node_attributes = rule.decorator(support)
                    assert not (set(node_attributes) - grammar.legal_attributes), \
                        'illegal attributes in decorator output: ' + str(
                            set(node_attributes) - grammar.legal_attributes)
                    new_node.attributes = node_attributes
                    if debug:
                        print('new node:')
                        new_node.print()

                    yield new_node
            elif debug:
                print('validator returned False')
        if debug and no_match:
            print('no match')


def debug_rule(graph, rule, max_depth: int=float('inf')):
    grammar = Grammar(start_symbols=[rule.lhs], rules=[rule], depth_limit=max_depth)
    parse_graph(graph, grammar, debug=True)
