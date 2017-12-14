import itertools
from collections import defaultdict
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
import pandas as pd
import toolz
import matplotlib.pyplot as plt
from estnltk.spans import Span
from typing import Union, List, Sequence


class Node:
    def __init__(self, name=None, support: Union[Sequence['Node'], Span]=None, weight=1):
        self.name = name
        self.support = support
        self.weight = weight

        if isinstance(support, Span):
            self.text_spans = ((support.start, support.end),)
            self.text = support.text
            if name is None:
                if support.layer:
                    self.name = support.grammar_symbol
                else:
                    self.name = support.text
            for attr in support.legal_attribute_names:
                setattr(self, attr, getattr(support, attr))
        elif isinstance(support, tuple):
            self.text_spans = tuple(sorted(s for n in support for s in n.text_spans))
        else:
            raise TypeError('support must be of type Span or tuple, not {}'.format(type(support)))

        self.start = self.text_spans[0][0]
        self.end = self.text_spans[-1][1]

    def __hash__(self):
        return hash((self.name, self.support))

    def __eq__(self, other):
        return self.name == other.name and self.support == other.support

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __gt__(self, other):
        return (self.start, self.end) > (other.start, other.end)

    def __str__(self):
        # include hash because networkx.drawing.nx_pydot.pydot_layout overlaps nodes with equal str value
        return 'Node({name}, ({span.start}, {span.end}), {h})'.format(span=self, h=hash(self), name=self.name)

    def __repr__(self):
        return str(self)


class TerminalSpan(Span):
    text = None
    start = None
    end = None
    layer = None

    def __init__(self, text):
        self.text = text
        self._legal_attribute_names = {}

        if text == 'START':
            self.start = float('-inf')
            self.end = float('-inf')
        elif text == 'END':
            self.start = float('inf')
            self.end = float('inf')

    def __hash__(self):
        return hash((self.text, self.start, self.end))

    def __repr__(self):
        return 'TerminalSpan({self.text!r})'.format(self=self)


START_SPAN = TerminalSpan('START')
END_SPAN = TerminalSpan('END')
START = Node('START', START_SPAN)
END = Node('END', END_SPAN)


class Grammar:
    def __init__(self, *, start_symbols:Sequence, rules:list):
        self.rules = tuple(rules)
        self.start_symbols = start_symbols
        self.nonterminals = frozenset(i['lhs'] for i in rules)

        terminals = set()
        for i in (set(i.rhs) for i in self.rules):
            terminals.update(i)
        terminals -= self.nonterminals

        self.terminals = frozenset(terminals)
        #self.nonterminal_dependency_order = tuple(self.get_rule_application_order())

    def get_rule_application_order(self) -> List[str]:
        rules_deps = dict(
            (j, set(itertools.chain(*i)) - self.terminals) for j, i in [(k, (i['rhs'] for i in v)) for k, v in
                                                                        toolz.groupby(lambda x: x['lhs'],
                                                                                      self).items()])
        order = []
        while len(order) != len(self.nonterminals):
            for k, v in rules_deps.items():
                if not v and k not in order:
                    order.append(k)
                    break
                else:
                    for _ in order:
                        rules_deps[k] -= set(order)
        return order

    def get_rule(self, lhs, rhs):
        for rule in self.rules:
            if rule.lhs == lhs.name and len(rhs) == len(rule.rhs) and [(a == b.name) for a, b in zip(rule.rhs, rhs)]:
                return rule
        return None

    def __getitem__(self, key):
        if key in self.nonterminals:
            return [i for i in self.rules if i.lhs == key]
        else:
            return self.rules[key]

    def __str__(self):
        rules = '\n\t'.join([str(i) for i in self.rules])
        terminals = ', '.join(sorted(self.terminals))
        nonterminals = ', '.join(sorted(self.nonterminals))
        return '''
Grammar:
\tstart: {start}
\tterminals: {terminals}
\tnonterminals: {nonterminals}
Rules:
\t{rules}
'''.format(start=', '.join(self.start_symbols), rules=rules, terminals=terminals, nonterminals=nonterminals)

    def __repr__(self):
        return str(self)


class Rule:
    def __init__(self, lhs, rhs, priority: int=0, decorator=None, consistency_checker=None):
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        self.rhs = tuple(rhs)

        self.priority = priority

        if decorator:
            self.decorator = decorator
        else:
            self.decorator = lambda x: None

        if consistency_checker:
            self.consistency_checker = consistency_checker
        else:
            self.consistency_checker = lambda x: True

    def __lt__(self, other):
        return self.priority < other.priority

    def __getitem__(self, key):
        if key == 'lhs':
            return self.lhs
        elif key == 'rhs':
            return self.rhs
        else:
            raise AssertionError

    def __str__(self):
        return '{self.lhs} -> {rhs}\t: {self.priority}, cc: {self.consistency_checker.__name__}, dec: {self.decorator.__name__}'.format(self=self, rhs=' '.join(self.rhs))

    def __repr__(self):
        return str(self)


class LayerGraph(nx.DiGraph):
    def __init__(self, **attr):
        self.map_spans_to_nodes = defaultdict(list)
        super().__init__(**attr)

    def update_spans_to_nodes_map(self, node):
        if node not in self.map_spans_to_nodes[node.text_spans]:
            self.map_spans_to_nodes[node.text_spans].append(node)

    def add_node(self, node, **attr):
        super().add_node(node, **attr)
        self.update_spans_to_nodes_map(node)

    def add_nodes_from(self, nodes, **attr):
        super().add_nodes_from(nodes, **attr)
        for node in nodes:
            self.update_spans_to_nodes_map(node)

    def add_edge(self, u, v, **attr):
        super().add_edge(u, v, **attr)
        self.update_spans_to_nodes_map(u)
        self.update_spans_to_nodes_map(v)

    def add_edges_from(self, ebunch, **attr):
        if not isinstance(ebunch, (list, set, tuple)):
            ebunch = list(ebunch)
        super().add_edges_from(ebunch, **attr)
        for u, v, *_ in ebunch:
            self.update_spans_to_nodes_map(u)
            self.update_spans_to_nodes_map(v)


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
            items.append(Node(row_name, a, b))
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
                    nnode = Node("_", Span(e1, s2, legal_attributes={}))
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
                node = Node((s1, e2), nonterminal)
                node.weight = rule.weight

                nodes[node].append((rule, path))
                g2.add_node(node)
                g2.add_edges_from(
                    [(i, node) for i in g2.predecessors(path[0])] +
                    [(node, i) for i in g2.successors(path[-1])])
    return nodes


def choose_parse_tree(nodes: Dict[Node, List[Tuple[Rule, Node]]], grammar: Grammar) -> nx.DiGraph:
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
        for s,e in spans:
            nodes.append(Node(row, Span(s, e, legal_attributes={})))
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
                nodes.append(Node(attr, spans))
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


def get_match_up(G, nodes, names, pos):
    if pos == 0:
        yield nodes
        return
    for node in G.pred[nodes[-1]]:
        if node.name == names[pos-1]:
            yield from get_match_up(G, nodes+[node], names, pos-1)


def get_match_down(G, nodes, names, pos):
    if pos + 1 == len(names):
        yield nodes
        return
    for node in G.succ[nodes[-1]]:
        if node.name == names[pos+1]:
            yield from get_match_down(G, nodes+[node], names, pos+1)


def get_match(graph: LayerGraph, node: Node, names: Sequence[str], pos: int):
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


def add_nodes(G, nodes_to_add):
    for node, span, predecessors, successors in nodes_to_add:
        for pred in predecessors:
            G.add_edge(pred, node)
        for succ in successors:
            G.add_edge(node, succ)


def parse_graph(G, grammar, depth=float('inf')):
    """
    Expands graph bottom-up using grammar.
    """
    rule_map = defaultdict(list)
    for rule in grammar.rules:
        for pos, v in enumerate(rule.rhs):
            rule_map[v].append((rule, pos))
    worklist = [(n,0) for n in G if n.name in rule_map]

    while worklist:
        node, d = worklist.pop()
        # expand fragment
        nodes_to_add = []
        for rule, pos in rule_map[node.name]:
            for sequence in get_match(G, node, rule.rhs, pos):
                sequence = tuple(sequence)
                assert all((sequence[i], sequence[i+1]) in G.edges for i in range(len(sequence)-1))
                if rule.consistency_checker(sequence):
                    new_node = Node(rule.lhs, sequence)
                    new_node.decoration = rule.decorator(sequence)
                    nodes_to_add.append((new_node,
                                         sequence,
                                         list(G.pred[sequence[0]]),
                                         list(G.succ[sequence[-1]]),
                                         ))
        add_nodes(G, nodes_to_add)
        if d < depth:
            for node, _, _, _ in nodes_to_add:
                if node.name in rule_map:
                    worklist.append((node, d+1))
    return G


def print_nodes(graph, text, names=None):
    """ names is the set of node names to be printed
        of names is None, all nodes are printed
    """
    results = []
    for node in graph:
        try:
            if not names or node.name in names:
                results.append((node.name, text.text[node.start:node.end]))
        except:
            pass
    results.sort()
    for name, t in results:
        print('{:20} {}'.format(name, t))


def plot_graph(graph:LayerGraph, size=12, prog='dot'):
    labels = {node:node.name for node in graph.nodes}
    pos = nx.drawing.nx_pydot.pydot_layout(graph, prog=prog)
    plt.figure(figsize=(size,size))
    nx.draw(graph, with_labels=True, labels=labels, node_color=[[1,.8,.8]], node_shape='s', node_size=500, pos=pos)
    plt.show()
