from estnltk.taggers import Tagger
from estnltk.layer import Layer
from estnltk.spans import SpanList
from estnltk.finite_grammar.layer_graph import GrammarNode, layer_to_graph, get_spans
from estnltk.finite_grammar.grammar import parse_graph


class GrammarParsingTagger(Tagger):
    description = 'Parses input layer using grammar. Output layer envelopes input.'
    attributes = None
    configuration = {}
    depends_on = []
    layer_name = ''

    def __init__(self, grammar, input_layer, layer_name='parse', attributes=(), grammar_symbols={}):
        self.grammar = grammar
        self.layer_name = layer_name
        self.input_layer = input_layer
        self.attributes = attributes
        self.depends_on = [input_layer]
        self.grammar_symbols = set(grammar_symbols)

    def _make_layer(self, text, layers):
        graph = layer_to_graph(layers[self.input_layer])
        graph = parse_graph(graph, self.grammar)

        attributes = self.attributes
        layer = Layer(name=self.layer_name,
                      enveloping=self.input_layer,
                      attributes=attributes
                      )
        for node in graph:
            if isinstance(node, GrammarNode) and node.name in self.grammar_symbols:
                # SpanNode and ParseNode are GrammarNode
                span = SpanList()
                span.spans = get_spans(node)
                for attr in attributes:
                    setattr(span, attr, getattr(node, attr, None))
                layer.add_span(span)
        return layer

    def tag(self, text, return_layer=False):
        layer = self._make_layer(text.text, text.layers)
        assert isinstance(layer, Layer), 'make_layer must return a Layer instance'
        if return_layer:
            return layer
        text[self.layer_name] = layer
