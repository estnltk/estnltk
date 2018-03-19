from typing import Sequence

from estnltk.spans import SpanList
from estnltk.layer import Layer
from estnltk.taggers import Tagger


class EnvelopingGapTagger(Tagger):
    """ Tags all spans that are not covered by any span of any input layer.
        The resulting spans can be annotated with a decorator function.
    """
    conf_param = ['decorator', 'layers_with_gaps', 'enveloped_layer']

    def __init__(self,
                 output_layer: str,
                 layers_with_gaps: Sequence[str],
                 enveloped_layer: str,
                 output_attributes: Sequence=(),
                 decorator: callable=None):
        self.layers_with_gaps = layers_with_gaps
        self.enveloped_layer = enveloped_layer
        self.input_layers = list(layers_with_gaps) + [enveloped_layer]
        self.output_layer = output_layer
        assert bool(output_attributes) == bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.output_attributes = tuple(output_attributes)
        self.decorator = decorator

    def _make_layer(self, raw_text, layers, status):
        layers_with_gaps = [layers[name] for name in self.layers_with_gaps]
        assert all(layer.enveloping == self.enveloped_layer for layer in layers_with_gaps)
        enveloped = layers[self.enveloped_layer]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            parent=None,
            enveloping=self.enveloped_layer,
            ambiguous=False
            )
        for gap in enveloping_gaps(layers_with_gaps, enveloped):
            spl = SpanList()
            spl.spans = gap
            if self.decorator:
                decorations = self.decorator(gap)
                for attr in self.output_attributes:
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
