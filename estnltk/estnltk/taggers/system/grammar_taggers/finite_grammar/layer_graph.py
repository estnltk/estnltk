from collections import defaultdict
from collections.abc import Hashable
from typing import Sequence
import networkx as nx
import matplotlib.pyplot as plt
import pandas

from estnltk import Span
from estnltk_core.layer_operations.iterators.consecutive import iterate_consecutive_spans


class Node:
    def __init__(self, name: str, start: int, end: int):
        self.name = name
        assert 0 <= start, start
        assert start <= end, (start, end)
        self.start = start
        self.end = end

    def __lt__(self, other):
        if isinstance(other, Node):
            return (self.start, self.end, self.name) < (other.start, other.end, other.name)
        raise TypeError('unorderable types')

    def __gt__(self, other):
        if isinstance(other, Node):
            return (self.start, self.end, self.name) > (other.start, other.end, other.name)
        raise TypeError('unorderable types')

    def __eq__(self, other):
        if isinstance(other, Node):
            return (self.start, self.end, self.name) == (other.start, other.end, other.name)
        return False

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
        result = ['{self.__class__.__name__}({self.name!r}, {self.start}, {self.end}'.format(self=self)]
        # include hash because networkx.drawing.nx_pydot.pydot_layout overlaps nodes with equal str value
        if isinstance(self, Hashable):
            result.append(', {}'.format(hash(self)))
        result.append(')')
        return ''.join(result)

    def __repr__(self):
        lines = [self.__class__.__name__]
        line = '  {:20} {}'.format
        d = self.__dict__
        keys = ['name', 'text', 'start', 'end', '_support_']
        for k in keys:
            if k in d:
                value = d[k]
                if isinstance(value, (list, tuple)):
                    value = ', '.join(str(v) for v in value)
                lines.append(line(k, value))
        for k in sorted(set(d)-set(keys)):
            value = d[k]
            if isinstance(value, (list, tuple)):
                value = ', '.join(str(v) for v in value)
            lines.append(line(k, value))
        return '\n'.join(lines)

    def to_html(self):
        keys = ['name', 'start', 'end']
        data = [{key: getattr(self, key) for key in keys}]
        df = pandas.DataFrame(data=data, columns=keys)
        table = df.to_html(index=False, escape=False)
        return table

    def _repr_html_(self):
        table = self.to_html()
        result = ['<h4>', self.__class__.__name__, '</h4>\n', table]
        if isinstance(self, (NonTerminalNode, PlusNode)):
            support = []
            result.append('<h5>Support</h5>\n')
            for n in self.support:
                support.append(n.__dict__)
                support[-1]['node type'] = n.__class__.__name__
            support = pandas.DataFrame(data=support, columns=['node type', 'name', 'start', 'end'])
            support = support.to_html(index=False, escape=False)
            result.append(support)
        return ''.join(result)


class PhonyNode(Node):
    def __hash__(self):
        return hash((self.name, self.start, self.end, type(self)))

    def __eq__(self, other):
        return isinstance(other, PhonyNode) and self.name == other.name and\
               self.start == other.start and self.end == other.end


class SpanNode(Node):
    def __init__(self, span):
        self.span = span
        super().__init__(str(span.text), span.start, span.end)

    def __hash__(self):
        return hash((self.name, self.span.base_span))


class GrammarNode(Node):
    def __init__(self, name, support, attributes: dict=None, group=None, priority=0, score=0):
        self.name = name
        self.support = tuple(support)
        assert all(isinstance(n, GrammarNode) for n in self.support)
        if isinstance(self, TerminalNode):
            self.terminals = (self,)
        else:
            self.terminals = tuple(t for n in self.support for t in n.terminals)
        assert all(isinstance(n, TerminalNode) for n in self.terminals)
        assert self.terminals == tuple(sorted(self.terminals)), 'support not sorted'
        start = self.terminals[0].start
        end = self.terminals[-1].end
        if group is None:
            self.group = hash((name, self.support))
        else:
            self.group = group
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes
        self.priority = priority
        self.score = score

        super().__init__(name, start, end)

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __eq__(self, other):
        if isinstance(other, GrammarNode):
            return self.name == other.name and self.support == other.support
        return False

    def __hash__(self):
        return hash((self.name, self.support))


class TerminalNode(GrammarNode):
    def __init__(self, name, span: Span, attributes=None):
        self.span = span
        self.start = span.start
        self.end = span.end
        self.text = span.text
        super().__init__(name, (self,))
        if attributes is None:
            attributes = span.layer.attributes
        for attr in attributes:
            self.attributes[attr] = getattr(span, attr)

    def __hash__(self):
        return hash((self.name, self.span.base_span))

    def __eq__(self, other):
        if isinstance(other, TerminalNode):
            return self.name == other.name and self.span == other.span
        return False


class NonTerminalNode(GrammarNode):
    def __init__(self, rule, support: Sequence[GrammarNode]):
        score = rule.scoring(support)
        super().__init__(rule.lhs, support, group=rule.group, priority=rule.priority, score=score)


class PlusNode(NonTerminalNode):
    def __init__(self, rule, support: Sequence[GrammarNode]):
        new_support = []
        # maybe too general, but let it be
        for node in support:
            if isinstance(node, PlusNode):
                new_support.extend(node.support)
            else:
                new_support.append(node)
        new_support = tuple(new_support)
        # super().__init__(rule.lhs, new_support, group=rule.group, priority=rule.priority)
        super().__init__(rule, new_support)


class MSeqNode(PlusNode):
    pass


class LayerGraph(nx.DiGraph):
    def __init__(self, **attr):
        self.map_start_end_to_nodes = defaultdict(list)
        self.parse_trees = nx.DiGraph()
        super().__init__(**attr)

    def _update_start_end_to_nodes_map(self, node):
        if isinstance(node, GrammarNode) and node not in self.map_start_end_to_nodes[(node.start, node.end)]:
            self.map_start_end_to_nodes[(node.start, node.end)].append(node)

    def _update_parse_trees(self, node):
        if isinstance(node, (NonTerminalNode, PlusNode)):
            for supp in node.support:
                self.parse_trees.add_edge(node, supp)
        elif isinstance(node, TerminalNode):
            self.parse_trees.add_edge(node, SpanNode(node.span))

    def add_node(self, node, **attr):
        if node in self:
            return
        super().add_node(node, **attr)
        self._update_start_end_to_nodes_map(node)
        self._update_parse_trees(node)

    def add_nodes_from(self, nodes, **attr):
        for node in nodes:
            self.add_node(node, **attr)

    def add_edge(self, u, v, **attr):
        super().add_edge(u, v, **attr)
        self._update_start_end_to_nodes_map(u)
        self._update_start_end_to_nodes_map(v)
        self._update_parse_trees(u)
        self._update_parse_trees(v)

    def add_edges_from(self, ebunch, **attr):
        if not isinstance(ebunch, (list, set, tuple)):
            ebunch = list(ebunch)
        super().add_edges_from(ebunch, **attr)
        for u, v, *_ in ebunch:
            self._update_start_end_to_nodes_map(u)
            self._update_start_end_to_nodes_map(v)
            self._update_parse_trees(u)
            self._update_parse_trees(v)

    def remove_nodes_from(self, nodes):
        nodes_to_remove = set(nodes)
        for n in nodes:
            nodes_to_remove.update(nx.ancestors(self.parse_trees, n))
        for n in nodes_to_remove:
            assert isinstance(n, NonTerminalNode), 'attempt to remove a non NonTerminalNode: ' + str(n)
            self.map_start_end_to_nodes[(n.start, n.end)].remove(n)
        self.parse_trees.remove_nodes_from(nodes_to_remove)
        super().remove_nodes_from(nodes_to_remove)

    def _repr_html_(self):
        records = []
        attributes = ['name', 'start', 'end']
        for n in sorted(self.nodes):
            record = {a: str(getattr(n, a)) for a in attributes}
            record['node type'] = n.__class__.__name__
            records.append(record)
        table = pandas.DataFrame(data=records, columns=['node type', 'name', 'start', 'end'])
        html_table = table.to_html(index=False, escape=False)

        return '<h4>LayerGraph</h4>\n' + html_table


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
    return [t.span for t in node.terminals]


def layer_to_graph(layer, raw_text, name_attribute='grammar_symbol', attributes=None, gap_validator=None):
    if attributes is None:
        attributes = layer.attributes
    assert not attributes or set(attributes) <= set(layer.attributes)

    graph = LayerGraph()

    if layer.ambiguous:
        for sp in layer:
            assert sp.start >= 0, sp
            names_1 = {getattr(b, name_attribute) for b in sp.annotations}
            for name_1 in names_1:
                graph.add_node(TerminalNode(name_1, sp, attributes))
        for sp_1, sp_2 in iterate_consecutive_spans(layer, raw_text, gap_validator=gap_validator):
            names_1 = {getattr(b, name_attribute) for b in sp_1.annotations}
            names_2 = {getattr(b, name_attribute) for b in sp_2.annotations}
            for name_1 in names_1:
                for name_2 in names_2:
                    graph.add_edge(TerminalNode(name_1, sp_1, attributes), TerminalNode(name_2, sp_2, attributes))
    else:
        for sp in layer:
            graph.add_node(TerminalNode(getattr(sp, name_attribute), sp, attributes))
        for a, b in iterate_consecutive_spans(layer, raw_text, gap_validator=gap_validator):
            name_a = getattr(a, name_attribute)
            name_b = getattr(b, name_attribute)
            graph.add_edge(TerminalNode(name_a, a, attributes), TerminalNode(name_b, b, attributes))

    return graph


def plot_graph(graph:LayerGraph, size=12, prog='dot'):
    labels = {node: node.name for node in graph.nodes}
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
