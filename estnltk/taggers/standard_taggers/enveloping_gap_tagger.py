from typing import Sequence

from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


def default_decorator(gap):
    return {}


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
        self.decorator = decorator or default_decorator

    def _make_layer(self, text, layers, status):
        layers_with_gaps = [layers[name] for name in self.layers_with_gaps]
        assert all(layer.enveloping == self.enveloped_layer for layer in layers_with_gaps)
        enveloped = layers[self.enveloped_layer]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            text_object=text,
            parent=None,
            enveloping=self.enveloped_layer,
            ambiguous=False
            )
        decorator = self.decorator
        for gap in enveloping_gaps(layers_with_gaps, enveloped):
            layer.add_annotation(gap, **decorator(gap))
        return layer


def enveloping_gaps(layers, enveloped):
    cover = {bs for layer in layers for span in layer for bs in span.base_span}

    spans = iter(enveloped)
    s = next(spans)
    while s:
        while s.base_span in cover:
            s = next(spans)
        gap = []
        while s.base_span not in cover:
            gap.append(s)
            try:
                s = next(spans)
            except StopIteration:
                s = None
                break
        yield gap
