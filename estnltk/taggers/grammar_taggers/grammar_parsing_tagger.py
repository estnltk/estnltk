from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
from estnltk import SpanList, EnvelopingSpan
from estnltk.finite_grammar.layer_graph import GrammarNode, layer_to_graph, get_spans
from estnltk.finite_grammar import parse_graph


class GrammarParsingTagger(Tagger):
    """Parses input layer using grammar. Output layer envelopes input."""

    conf_param = ['grammar', 'name_attribute', 'input_layer', 'output_nodes', 'resolve_support_conflicts',
                  'resolve_start_end_conflicts', 'resolve_terminals_conflicts']

    def __init__(self,
                 grammar,
                 layer_of_tokens,
                 name_attribute='grammar_symbol',
                 layer_name='parse',
                 attributes=(),
                 output_nodes=None,
                 resolve_support_conflicts: bool = True,
                 resolve_start_end_conflicts: bool = True,
                 resolve_terminals_conflicts: bool = True):
        self.grammar = grammar
        self.output_layer = layer_name
        self.name_attribute = name_attribute
        self.input_layer = layer_of_tokens
        self.input_layers = [layer_of_tokens]
        self.output_attributes = attributes
        if output_nodes is None:
            self.output_nodes = set(grammar.start_symbols)
        else:
            self.output_nodes = set(output_nodes)
        self.resolve_support_conflicts = resolve_support_conflicts
        self.resolve_start_end_conflicts = resolve_start_end_conflicts
        self.resolve_terminals_conflicts = resolve_terminals_conflicts

    def _make_layer(self, text, layers, status):
        graph = layer_to_graph(layers[self.input_layer],
                               name_attribute=self.name_attribute)
        graph = parse_graph(graph,
                            self.grammar,
                            resolve_support_conflicts=self.resolve_support_conflicts,
                            resolve_start_end_conflicts=self.resolve_start_end_conflicts,
                            resolve_terminals_conflicts=self.resolve_terminals_conflicts)

        attributes = self.output_attributes
        layer = Layer(name=self.output_layer,
                      enveloping=self.input_layer,
                      attributes=attributes
                      )
        for node in graph:
            if isinstance(node, GrammarNode) and node.name in self.output_nodes:
                span = EnvelopingSpan(spans=get_spans(node))
                for attr in attributes:
                    if attr == '_group_':
                        span._group_ = node.group
                    elif attr == 'name':
                        span.name = node.name
                    elif attr == '_priority_':
                        span._priority_ = node.priority
                    else:
                        setattr(span, attr, node[attr])
                layer.add_span(span)
        return layer
