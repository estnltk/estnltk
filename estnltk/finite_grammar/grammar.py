from typing import Sequence, List
from collections import defaultdict
import itertools
import toolz

from .layer_graph import NonTerminalNode, LayerGraph


class Grammar:

    _internal_attributes = frozenset({'name', 'text', 'start', 'end', '_terminals_', '_support_', '_priority_', '_group_'})

    def __init__(self, *, start_symbols: Sequence, rules: list=None, max_depth: int=float('inf'), legal_attributes=None):

        if legal_attributes is None:
            self.legal_attributes = frozenset()
        else:
            legal_attributes = frozenset(legal_attributes)
            assert not legal_attributes & self._internal_attributes, 'legal attributes contain internal attributes'
            self.legal_attributes = legal_attributes
        if rules is None:
            self.rules = []
        else:
            self.rules = rules
        self._check_rules()
        self.start_symbols = start_symbols
        self.max_depth = max_depth
        self._terminals_and_nonterminals()

    def _terminals_and_nonterminals(self):
        self.nonterminals = frozenset(r['lhs'] for r in self.rules)
        terminals = set()
        for i in (set(i.rhs) for i in self.rules):
            terminals.update(i)
        self.terminals = frozenset(terminals - self.nonterminals)

    def _check_rules(self):
        assert len(self.rules) == len({(r.lhs, r.rhs) for r in self.rules}), 'repetitive rules'

    def add(self, rule):
        self.rules.append(rule)
        self._check_rules()
        self._terminals_and_nonterminals()

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

    def __init__(self, lhs, rhs, priority: int=0, group=None, decorator=None, validator=None):
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        self.rhs = tuple(rhs)

        self.priority = priority
        self.group = group
        if group is None:
            self.group = hash((self.lhs, self.rhs))

        if decorator:
            self.decorator = decorator
        else:
            self.decorator = self.default_decorator

        if validator:
            self.validator = validator
        else:
            self.validator = self.default_validator

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
        return '{self.lhs} -> {rhs}\t: {self.priority}, val: {self.validator.__name__}, dec: {self.decorator.__name__}'.format(self=self, rhs=' '.join(self.rhs))

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


def parse_graph(graph: LayerGraph, grammar: Grammar, max_depth: int=None, resolve_conflicts=True, debug: bool=False) -> LayerGraph:
    """
    Expands graph bottom-up using grammar. Changes the input graph.
    """
    if max_depth is None:
        max_depth = grammar.max_depth
    rule_map = defaultdict(list)
    for rule in grammar.rules:
        for pos, v in enumerate(rule.rhs):
            rule_map[v].append((rule, pos))
    worklist = None
    if max_depth > 0:
        worklist = [(n,0) for n in graph if n.name in rule_map]

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
                if rule.validator(support):
                    new_node = NonTerminalNode(rule, support)
                    decoration = rule.decorator(support)
                    assert not (set(decoration) - grammar.legal_attributes),\
                        'illegal attributes in decorator output: ' + str(set(decoration) - grammar.legal_attributes)
                    for name, value in decoration.items():
                        setattr(new_node, name, value)
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
        added_nodes = add_nodes(graph, nodes_to_add, resolve_conflicts)
        if d < max_depth:
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


def debug_rule(graph, rule, max_depth:int=float('inf')):
    grammar = Grammar(start_symbols=[rule.lhs], rules=[rule], max_depth=max_depth)
    parse_graph(graph, grammar, debug=True)
