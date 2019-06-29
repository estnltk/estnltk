from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
from estnltk import EnvelopingSpan
from estnltk.finite_grammar.layer_graph import GrammarNode, layer_to_graph, get_spans
from estnltk.finite_grammar import parse_graph


class GrammarParsingTagger(Tagger):
    """Parses input layer using grammar. Output layer envelopes input."""

    conf_param = ['grammar', 'name_attribute', 'output_nodes', 'resolve_support_conflicts',
                  'resolve_start_end_conflicts', 'resolve_terminals_conflicts', 'ambiguous', 'gap_validator', 'debug']

    def __init__(self,
                 grammar,
                 layer_of_tokens,
                 name_attribute='grammar_symbol',
                 output_layer='parse',
                 attributes=(),
                 output_nodes=None,
                 gap_validator=None,
                 resolve_support_conflicts: bool=True,
                 resolve_start_end_conflicts: bool=True,
                 resolve_terminals_conflicts: bool=True,
                 debug=False,
                 output_ambiguous: bool=False):
        self.grammar = grammar
        self.input_layers = [layer_of_tokens]
        self.name_attribute = name_attribute
        self.output_layer = output_layer
        self.output_attributes = tuple(attributes)
        if output_nodes is None:
            self.output_nodes = set(grammar.start_symbols)
        else:
            self.output_nodes = set(output_nodes)

        self.gap_validator = gap_validator
        self.resolve_support_conflicts = resolve_support_conflicts
        self.resolve_start_end_conflicts = resolve_start_end_conflicts
        self.resolve_terminals_conflicts = resolve_terminals_conflicts
        self.debug = debug
        self.ambiguous = output_ambiguous

    def _make_layer(self, text, layers, status):
        graph = layer_to_graph(layer=layers[self.input_layers[0]],
                               raw_text=text.text,
                               name_attribute=self.name_attribute,
                               gap_validator=self.gap_validator)
        graph = parse_graph(graph=graph,
                            grammar=self.grammar,
                            resolve_support_conflicts=self.resolve_support_conflicts,
                            resolve_start_end_conflicts=self.resolve_start_end_conflicts,
                            resolve_terminals_conflicts=self.resolve_terminals_conflicts,
                            debug=self.debug)

        attributes = self.output_attributes
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      enveloping=self.input_layers[0],
                      attributes=attributes,
                      ambiguous=self.ambiguous
                      )
        try:
            for node in graph:
                if isinstance(node, GrammarNode) and node.name in self.output_nodes:
                    span = EnvelopingSpan(spans=get_spans(node), layer=layer)
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
        except ValueError as e:
            if e.args[0] == 'this layer is not ambiguous and the span is already in the spanlist':
                raise ValueError('there exists an ambiguous span among output nodes of the grammar, '
                                 'make the output layer ambiguous by setting output_ambiguous=True '
                                 'or adjust grammar by changing priority, scoring and lhs parameters of rules',
                                 e.args[1])
            raise
        return layer
