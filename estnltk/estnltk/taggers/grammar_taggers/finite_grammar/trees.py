from collections import defaultdict
from typing import Dict, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from typing import List

from .layer_graph import NonTerminalNode, GrammarNode
from .layer_graph import START_NODE as START
from .layer_graph import END_NODE as END
from .grammar import Grammar, Rule


def graph_from_document(rows: Dict[str, List[Tuple[int, int]]]) -> nx.DiGraph:
    nodes = document_to_nodes(rows)
    graph = graph_from_nodes(nodes)
    add_blanks(graph)
    return graph


def edges_from_dataframe(df, items):
    fixed = df.groupby('e1').apply(lambda x: x.groupby('n2').apply(lambda y: y[y.s2 <= y.e2.min()]))
    try:
        fixed['through_blank'] = fixed.s2 != fixed.e1
        edges = []
        for a, b, bl in zip(fixed.a.values, fixed.b.values, fixed.through_blank):
            edges.append((items[a], items[b]))
        return edges
    except AttributeError:
        raise AssertionError('no items in df')


def create_entry_and_exit_nodes(graph: nx.DiGraph, items):
    graph.add_nodes_from([START, END])
    items = sorted(items)
    graph.add_edge(START, items[0])
    for node in (set(graph.nodes()) - {START}) - nx.descendants(graph, START):
        graph.add_edge(START, node)
    graph.add_edge(items[-1], END)
    for node in (set(graph.nodes()) - {END}) - nx.ancestors(graph, END):
        graph.add_edge(node, END)


def matrix_to_dataframe(res, items):
    vals = []
    for a, b in zip(*np.where(res)):
        (s1, e1), n1 = items[a]
        (s2, e2), n2 = items[b]
        vals.append((n1, s1, e1, n2, s2, e2, a, b))
    return pd.DataFrame.from_records(vals, columns='n1 s1 e1 n2 s2 e2 a b'.split())


def get_elementary_nodes(rows):
    items = []

    for row_name, indices in rows.items():
        for (a, b) in indices:
            items.append(NonTerminalNode(row_name, a, b))
    return items


def get_dense_matrix(rows):
    mapping, reverse_mapping = get_dense_mapping(rows)
    b_rows = []
    names = []
    for row_name, indices in rows.items():
        for (a, b) in indices:
            names.append(row_name)
            x = np.zeros(shape=len(reverse_mapping) - 1, dtype=np.bool)
            x[mapping[a]: mapping[b]] = 1
            b_rows.append(x)
    b_rows = np.array(b_rows)
    start_index = []
    end_index = []
    for row in b_rows:
        wh = np.where(row)[0]
        start_index.append(wh[0])
        end_index.append(wh[-1])
    start_index = np.array(start_index)
    res = np.zeros(shape=(len(start_index), len(start_index)), dtype=np.bool)
    for row, idx in zip(range(res.shape[0]), end_index):
        res[row] = start_index > idx
    return res


def get_dense_mapping(rows):
    by_start = defaultdict(list)
    by_end = defaultdict(list)
    for k, v in rows.items():
        for s, e in v:
            by_start[s].append(((s, e), k))
            by_end[e].append(((s, e), k))
    starts = set(by_start.keys())
    ends = set(by_end.keys())
    mapping = {}
    for idx, i in enumerate(sorted(starts | ends)):
        mapping[i] = idx
    reverse_mapping = [v for (v, _) in sorted(mapping.items())]
    return mapping, reverse_mapping


def add_blanks(graph: nx.DiGraph) -> None:
    nodes_to_add = []
    edges_to_add = []
    edges_to_remove = []
    for node in graph.nodes():
        if node != START:
            (s1, e1), name = (node.start, node.end), node.name
            for succ in graph.successors(node):
                (s2, e2), _ = (succ.start, succ.end), succ.name
                if s2 - e1 > 1 and succ != END:
                    nnode = GrammarNode("_", None, ((e1, s2),), ())
                    nodes_to_add.append(nnode)
                    edges_to_add.extend([(node, nnode), (nnode, succ)])
                    edges_to_remove.append((node, succ))
    graph.add_nodes_from(nodes_to_add)
    graph.add_edges_from(edges_to_add)
    graph.remove_edges_from(edges_to_remove)


def get_valid_paths(graph: nx.DiGraph, rule: Rule):
    new_graph = graph.copy()

    new_graph.remove_nodes_from([START, END])
    new_graph.add_nodes_from([START, END])

    entries, exits = [], []

    for node in new_graph.nodes():
        if node[-1] == rule.rhs[0]:
            entries.append(node)
        if node[-1] == rule.rhs[-1]:
            exits.append(node)

    new_graph.add_edges_from([(START, i) for i in entries])
    new_graph.add_edges_from([(i, END) for i in exits])
    paths = [[START]]
    dones_paths = []
    etalon = rule.rhs[:]

    while paths:
        current_path = paths.pop(0)
        for succ in new_graph.successors(current_path[-1]):
            if len(current_path) <= len(etalon):
                if succ[-1] == etalon[len(current_path) - 1]:
                    paths.append(current_path + [succ])
            elif len(current_path) == len(etalon) + 1 and succ == END:
                dones_paths.append(current_path[1:])
    return dones_paths


def get_nonterminal_nodes(graph: nx.DiGraph, grammar: 'Grammar'):
    """"All parse trees.
    """
    g2 = graph.copy()
    order = grammar.nonterminal_dependency_order

    nodes = defaultdict(list)
    for nonterminal in order:
        for rule in grammar[nonterminal]:
            paths = get_valid_paths(g2, rule)
            for path in paths:
                (s1, e1), n1 = path[0]
                (s2, e2), n2 = path[-1]
                node = NonTerminalNode((s1, e2), nonterminal)
                node.weight = rule.weight

                nodes[node].append((rule, path))
                g2.add_node(node)
                g2.add_edges_from(
                    [(i, node) for i in g2.predecessors(path[0])] +
                    [(node, i) for i in g2.successors(path[-1])])
    return nodes


def choose_parse_tree(nodes: Dict[NonTerminalNode, List[Tuple[Rule, NonTerminalNode]]], grammar: Grammar) -> nx.DiGraph:
    if not len([i for i in nodes.keys() if i.name == grammar.start_symbol]) >= 1:
        raise AssertionError('Parse failed, change grammar.')
    # we'll choose the starting symbol with the most cover
    # this is negotiable
    # print([i for i in nodes.keys() if i.name == grammar.start_symbol])
    stack = [
        max((i for i in nodes.keys() if i.name == grammar.start_symbol), key=lambda x: x.weight)
    ]
    graph = nx.DiGraph()
    while stack:
        node = stack.pop(0)
        graph.add_node(node)
        if nodes[node]:
            _, children = max((rule.weight, children) for (rule, children) in nodes[node])
            graph.add_edges_from([(node, i) for i in children])
            stack.extend(children)
    return graph


def document_to_nodes(document):
    nodes = []
    for row, spans in document.items():
        for s, e in spans:
            nodes.append(GrammarNode(row, None, ((s, e),), ()))
    return nodes


def document_to_graph(document, grammar):
    graph = graph_from_document(document)
    nonterminal_nodes = get_nonterminal_nodes(graph, grammar)
    return choose_parse_tree(nonterminal_nodes, grammar)


def graph_from_nodes(nodes):
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    nodes.append(START)
    nodes.append(END)
    nodes.sort()
    for i, n_i in enumerate(nodes):
        stop = float('inf')
        for j in range(i+1, len(nodes)):
            n_j = nodes[j]
            if n_j.start > stop - 1:
                break
            if n_i.end <= n_j.start:
                stop = min(n_j.end, stop)
                graph.add_edge(n_i, n_j)
    return graph


def layer_to_graph_by_attribute(layer:'Layer', attribute:str) -> nx.DiGraph:
    """
    Create a graph from layer attribute values.
    """
    nodes = []
    if layer.ambiguous:
        for spanlist in layer:
            attr_to_spans = defaultdict(list)
            for span in spanlist:
                attr = getattr(span, attribute)
                if attr is None:
                    attr = 'None'
                attr_to_spans[attr].append(span)
            for attr, spans in attr_to_spans.items():
                nodes.append(NonTerminalNode(attr, spans))
    else:
        for span in layer:
            attr = getattr(span, attribute)
            if attr is None:
                attr = 'None'
            # TODO ...

    graph = graph_from_nodes(nodes)
    graph = nx.transitive_reduction(graph)
    add_blanks(graph)

    return graph
