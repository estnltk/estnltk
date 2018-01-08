from collections import defaultdict
from typing import Sequence
import networkx as nx
import matplotlib.pyplot as plt

from estnltk.spans import Span
from estnltk.layer_operations.consecutive import iterate_consecutive_spans
from estnltk.layer_operations.consecutive import iterate_starting_spans
from estnltk.layer_operations.consecutive import iterate_ending_spans


class Node:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    def __lt__(self, other):
        if hasattr(other, 'start') and hasattr(other, 'end'):
            return (self.start, self.end) < (other.start, other.end)
        raise TypeError('unorderable types')

    def __gt__(self, other):
        if hasattr(other, 'start') and hasattr(other, 'end'):
            return (self.start, self.end) > (other.start, other.end)
        raise TypeError('unorderable types')

    def print(self):
        print(self.__class__.__name__)
        d = self.__dict__
        line = '  {:20} {}'.format
        keys = ['name', 'text', 'start', 'end', '_support_']
        for k in keys:
            if k in d:
                print(line(k, d[k]))
        for k in sorted(set(d)-set(keys)):
            print(line(k, d[k]))

    def __str__(self):
        result = ['{self.__class__.__name__}({self.name}'.format(self=self)]
        if hasattr(self, 'start') and hasattr(self, 'end'):
            result.append('({self.start}, {self.end})'.format(self=self))
        # include hash because networkx.drawing.nx_pydot.pydot_layout overlaps nodes with equal str value
        result.append('{h})'.format(h=hash(self)))
        return ', '.join(result)

    def __repr__(self):
        return str(self)


class PhonyNode(Node):
    def __hash__(self):
        return hash((self.name, self.start, self.end, type(self)))

    def __eq__(self, other):
        return isinstance(other, PhonyNode) and self.name == other.name and\
               self.start == other.start and self.end==other.end


START_NODE = PhonyNode('START', float('-inf'), float('-inf'))
END_NODE = PhonyNode('END', float('inf'), float('inf'))


class GrammarNode(Node):
    def __init__(self, name, support, text_spans, terminals, group=None, priority=0):
        start = text_spans[0][0]
        end = text_spans[-1][1]
        self._support_ = support
        self.text_spans = text_spans
        self._terminals_ = terminals
        self._group_ = group
        if group is None:
            self._group_ = hash((name, self._support_, self.text_spans))
        self._priority_ = priority
        super().__init__(name, start, end)



    def __eq__(self, other):
        if isinstance(other, GrammarNode):
            return self.name == other.name and self._support_ == other._support_
        return False

    def __hash__(self):
        return hash((self.name, self._support_, self.text_spans))


class TerminalNode(GrammarNode):
    def __init__(self, span: Span, name_attribute: str, attributes=None):
        name = getattr(span, name_attribute)

        text_spans = ((span.start, span.end),)
        self.text = span.text
        if not attributes:
            attributes = span.legal_attribute_names
        for attr in attributes:
            setattr(self, attr, getattr(span, attr))

        super().__init__(name, span, text_spans, (self,))


class NonTerminalNode(GrammarNode):
    def __init__(self, rule, support: Sequence[GrammarNode]):
        text_spans = tuple(sorted(s for n in support for s in n.text_spans))
        terminals = tuple(sorted(t for n in support for t in n._terminals_))
        super().__init__(rule.lhs, support, text_spans, terminals, rule.group, rule.priority)


class LayerGraph(nx.DiGraph):
    def __init__(self, **attr):
        self.map_spans_to_nodes = defaultdict(list)
        super().__init__(**attr)

    def _update_spans_to_nodes_map(self, node):
        if isinstance(node, GrammarNode) and node not in self.map_spans_to_nodes[node.text_spans]:
            self.map_spans_to_nodes[node.text_spans].append(node)

    def add_node(self, node, **attr):
        super().add_node(node, **attr)
        self._update_spans_to_nodes_map(node)

    def add_nodes_from(self, nodes, **attr):
        super().add_nodes_from(nodes, **attr)
        for node in nodes:
            self._update_spans_to_nodes_map(node)

    def add_edge(self, u, v, **attr):
        super().add_edge(u, v, **attr)
        self._update_spans_to_nodes_map(u)
        self._update_spans_to_nodes_map(v)

    def add_edges_from(self, ebunch, **attr):
        if not isinstance(ebunch, (list, set, tuple)):
            ebunch = list(ebunch)
        super().add_edges_from(ebunch, **attr)
        for u, v, *_ in ebunch:
            self._update_spans_to_nodes_map(u)
            self._update_spans_to_nodes_map(v)


def get_nodes(graph, name):
    return sorted(n for n in graph.nodes if n.name==name)


def get_paths(graph, node, source=None, target=None):
    """
    iterates over all paths in the graph from source to target 
    that include the node
    if source or target is None, then source is replaced by node 'START'
    and target by 'END'
    """
    if not source or not target:
        for node in graph:
            if node.name == 'START' and not source:
                source = node
                if target: break
            elif node.name == 'END' and not target:
                target = node
                if source: break
    if node == source:
        into = [[node]]
    else:
        into = tuple(nx.all_simple_paths(graph, source, node))
    if node == target:
        out = [[node]]
    else:
        out = tuple(nx.all_simple_paths(graph, node, target))
    yield from (i[:-1]+o for i in into for o in out)


def get_spans(node):
    result = []

    def _get_spans(node):
        support = node._support_
        if isinstance(support, Span):
            result.append(support)
        else:
            for supp in support:
                _get_spans(supp)

    _get_spans(node)
    return result


def layer_to_graph(layer, attributes=None):
    if attributes is None:
        attributes = layer.attributes
    assert not attributes or set(attributes) <= set(layer.attributes)

    graph = LayerGraph()
    spans = layer.spans

    for b in iterate_starting_spans(spans):
        graph.add_edge(START_NODE, TerminalNode(b, 'grammar_symbol'))
    for a in iterate_ending_spans(spans):
        graph.add_edge(TerminalNode(a, 'grammar_symbol'), END_NODE)
    for a, b in iterate_consecutive_spans(spans):
        graph.add_edge(TerminalNode(a, 'grammar_symbol'), TerminalNode(b, 'grammar_symbol'))

    if not spans:
        graph.add_edge(START_NODE, END_NODE)

    return graph


def graph_to_parse_trees(graph):
    parse_trees = nx.DiGraph()
    for node in graph.nodes():
        if isinstance(node, NonTerminalNode):
            for supp in node._support_:
                parse_trees.add_edge(node, supp)
        elif isinstance(node, TerminalNode):
            parse_trees.add_edge(node, PhonyNode(node.text, node.start, node.end))
    return parse_trees


def plot_graph(graph:LayerGraph, size=12, prog='dot'):
    labels = {node:node.name for node in graph.nodes}
    pos = nx.drawing.nx_pydot.pydot_layout(graph, prog=prog)
    plt.figure(figsize=(size,size))
    nx.draw(graph, with_labels=True, labels=labels, node_color=[[1,.8,.8]], node_shape='s', node_size=500, pos=pos)
    plt.show()


def print_nodes(graph, text, names=None, attributes=None):
    """ names is the set of node names to be printed.
            If None, all nodes are printed.
        attributes is the list of attributes to be printed
            If None, 'name' and 'text' is printed for each node.
    """
    results = []
    if attributes is None:
        attributes = ['name', 'text']
    for node in graph:
        if not names or node.name in names:
            line = []
            for attribute in attributes:
                try:
                    if attribute == 'text':
                        value = text.text[node.start:node.end]
                    else:
                        value = getattr(node, attribute)
                except AttributeError:
                    value = ''
                line.append(value)
            results.append(line)
    results.sort()
    results = [attributes, ()]+results
    for line in results:
        print(''.join('{:20}'.format(str(value)) for value in line))
