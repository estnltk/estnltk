from estnltk.spans import SpanList
from estnltk.layer import Layer
from estnltk.taggers import TaggerNew


class EnvelopingGapTagger(TaggerNew):
    """ Tags all spans that are not covered by any span of any input layer.
        The resulting spans can be annotated with a decorator function.
    """
    description = 'Tags gaps of input layers.'
    conf_param = ['decorator', 'input_layers', 'enveloped_layer']

    def __init__(self, layer_name, input_layers, enveloped_layer, attributes=(), decorator=None):
        self.input_layers = input_layers
        self.enveloped_layer = enveloped_layer
        self.depends_on = input_layers + [enveloped_layer]
        self.layer_name = layer_name
        assert bool(attributes) == bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.attributes = tuple(attributes)
        self.decorator = decorator

    def _make_layer(self, raw_text, input_layers, status):
        layers = [input_layers[name] for name in self.input_layers]
        assert all(layer.enveloping == self.enveloped_layer for layer in layers)
        enveloped = input_layers[self.enveloped_layer]
        layer = Layer(
            name=self.layer_name,
            attributes=self.attributes,
            parent=None,
            enveloping=self.enveloped_layer,
            ambiguous=False
            )
        for gap in enveloping_gaps(layers, enveloped):
            spl = SpanList()
            spl.spans = gap
            if self.decorator:
                decorations = self.decorator(gap)
                for attr in self.attributes:
                    setattr(spl, attr, decorations[attr])
            layer.add_span(spl)
        return layer


def enveloping_gaps(layers, enveloped):
    cover = set()
    for layer in layers:
        if layer.ambiguous:
            for sp_list in layer.spans.spans:
                cover.update(sp_list[0])
        else:
            for sp_list in layer.spans.spans:
                cover.update(sp_list)

    spans = iter(enveloped)
    s = next(spans)
    while s:
        while s in cover:
            s = next(spans)
        gap = []
        while s not in cover:
            gap.append(s)
            try:
                s = next(spans)
            except StopIteration:
                s = None
                break
        yield gap
