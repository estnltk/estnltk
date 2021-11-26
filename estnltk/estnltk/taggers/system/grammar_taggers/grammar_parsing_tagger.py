from estnltk.taggers import Tagger
from estnltk import Layer
from estnltk.taggers.system.grammar_taggers.finite_grammar.layer_graph import GrammarNode, layer_to_graph, get_spans
from estnltk.taggers.system.grammar_taggers.finite_grammar import parse_graph

from estnltk_core.layer_operations import resolve_conflicts


class GrammarParsingTagger(Tagger):
    """Parses input layer using grammar. Output layer envelopes input.

    """
    conf_param = ['grammar', 'name_attribute', 'output_nodes', 'resolve_support_conflicts',
                  'resolve_start_end_conflicts', 'resolve_terminals_conflicts', 'ambiguous', 
                  'gap_validator', 'debug', 'force_resolving_by_priority', 'priority_attribute']

    def __init__(self,
                 grammar,
                 layer_of_tokens,
                 name_attribute='grammar_symbol',
                 output_layer='parse',
                 attributes=(),
                 output_nodes=None,
                 gap_validator=None,
                 resolve_support_conflicts: bool = True,
                 resolve_start_end_conflicts: bool = True,
                 resolve_terminals_conflicts: bool = True,
                 force_resolving_by_priority: bool = False,
                 priority_attribute='_priority',
                 debug=False,
                 output_ambiguous: bool = False):
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
        # Force resolving conflicts by priority attribute as the final step
        self.force_resolving_by_priority = force_resolving_by_priority
        self.priority_attribute = priority_attribute
        self.debug = debug
        self.ambiguous = output_ambiguous

    def _make_layer_template(self):
        layer_attributes = self.output_attributes
        layer_is_ambiguous = self.ambiguous
        if self.force_resolving_by_priority:
            # If self.force_resolving_by_priority, then we'll always create an ambigouos 
            # layer ( to allow maximum ambiguities )
            layer_is_ambiguous = True
            # Add priority attribute to layer
            if self.priority_attribute not in layer_attributes:
                layer_attributes += (self.priority_attribute, )
        return Layer(name=self.output_layer,
                     text_object=None,
                     enveloping=self.input_layers[0],
                     attributes=layer_attributes,
                     ambiguous=layer_is_ambiguous )

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
        layer = self._make_layer_template()
        layer.text_object = text
        layer_attributes = layer.attributes
        try:
            for node in graph:
                if isinstance(node, GrammarNode) and node.name in self.output_nodes:
                    annotation = {}
                    for attr in layer_attributes:
                        if attr == '_group_':
                            annotation['_group_'] = node.group
                        elif attr == 'name':
                            annotation['name'] = node.name
                        elif attr == '_priority_':
                            annotation['_priority_'] = node.priority
                        elif attr == self.priority_attribute:
                            if self.force_resolving_by_priority:
                                # Take node's priority, which will be used
                                # for final conflict resolving
                                annotation[self.priority_attribute] = node.priority
                        else:
                            annotation[attr] = node[attr]
                    layer.add_annotation(get_spans(node), **annotation)
            if self.force_resolving_by_priority:
                # The final conflict resolving.
                # The layer was created with maximum ambiguity: 
                # now force resolving all conflicts by the priority_attribute
                resolve_conflicts(layer, conflict_resolving_strategy='ALL',
                                  priority_attribute=self.priority_attribute)
                if not self.ambiguous:
                    layer.ambiguous = False
                # Remove priority attribute, if it is not required in the output
                if self.priority_attribute not in self.output_attributes:
                    layer.attributes = tuple([attr for attr in layer.attributes if attr != self.priority_attribute])
                    for span in layer:
                        for annotation in span.annotations:
                            delattr(annotation, self.priority_attribute)
        except ValueError as e:
            if e.args[0] == 'The layer is not ambiguous and this span already has a different annotation.':
                raise ValueError('there exists an ambiguous span among output nodes of the grammar, '
                                 'make the output layer ambiguous by setting output_ambiguous=True '
                                 'or adjust grammar by changing priority, scoring and lhs parameters of rules',
                                 e.args[0])
            raise
        return layer
