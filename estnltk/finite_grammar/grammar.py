from typing import Sequence, List
from collections import defaultdict
import itertools
import toolz

from .layer_graph import ParseNode, LayerGraph


class Grammar:
    def __init__(self, *, start_symbols:Sequence, rules:list, max_depth:int=float('inf')):
        self.rules = tuple(rules)
        self.start_symbols = start_symbols
        self.max_depth = max_depth
        self.nonterminals = frozenset(i['lhs'] for i in rules)

        terminals = set()
        for i in (set(i.rhs) for i in self.rules):
            terminals.update(i)
        terminals -= self.nonterminals

        self.terminals = frozenset(terminals)
        #self.nonterminal_dependency_order = tuple(self.get_rule_application_order())

    def get_rule_application_order(self) -> List[str]:
        rules_depths = dict(
            (j, set(itertools.chain(*i)) - self.terminals) for j, i in [(k, (i['rhs'] for i in v)) for k, v in
                                                                        toolz.groupby(lambda x: x['lhs'],
                                                                                      self).items()])
        order = []
        while len(order) != len(self.nonterminals):
            for k, v in rules_depths.items():
                if not v and k not in order:
                    order.append(k)
                    break
                else:
                    for _ in order:
                        rules_depths[k] -= set(order)
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
\tmax_depth: {max_depth}
Rules:
\t{rules}
'''.format(start=', '.join(self.start_symbols), rules=rules, terminals=terminals,
           nonterminals=nonterminals, max_depth=self.max_depth)

    def __repr__(self):
        return str(self)


class Rule:
    @staticmethod
    def default_validator(x):
        return True

    @staticmethod
    def default_decorator(x):
        return {}

    def __init__(self, lhs, rhs, priority: int=0, decorator=None, consistency_checker=None):
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        self.rhs = tuple(rhs)

        self.priority = priority

        if decorator:
            self.decorator = decorator
        else:
            self.decorator = self.default_decorator

        if consistency_checker:
            self.consistency_checker = consistency_checker
        else:
            self.consistency_checker = self.default_validator

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


def get_match(graph: LayerGraph, node: ParseNode, names: Sequence[str], pos: int):
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


def parse_graph(G, grammar, max_depth=None):
    """
    Expands graph bottom-up using grammar.
    """
    if not max_depth:
        max_depth = grammar.max_depth
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
                    new_node = ParseNode(rule.lhs, sequence)
                    decoration = rule.decorator(sequence)
                    for name, value in decoration.items():
                        setattr(new_node, name, value)
                    nodes_to_add.append((new_node,
                                         sequence,
                                         list(G.pred[sequence[0]]),
                                         list(G.succ[sequence[-1]]),
                                         ))
        add_nodes(G, nodes_to_add)
        if d < max_depth:
            for node, _, _, _ in nodes_to_add:
                if node.name in rule_map:
                    worklist.append((node, d+1))
    return G
