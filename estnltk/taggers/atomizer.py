from typing import Sequence
from estnltk.taggers import Tagger
from estnltk.text import Span, SpanList, Layer


class Atomizer(Tagger):
    """Forgets the parent of the input layer.

    Outputs an enveloping or simple (enveloping=None, parent=None) layer."""
    conf_param = ('enveloping',)

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 output_attributes: Sequence[str]=None,
                 enveloping: str = None
                 ):
        self.output_layer = output_layer
        self.input_layers = [input_layer]
        self.output_attributes = output_attributes
        self.enveloping = enveloping

    def _make_layer(self, raw_text, input_layers, status):
        layer = input_layers[self.input_layers[0]]
        if self.output_attributes is None:
            output_attributes = layer.attributes
        else:
            output_attributes = self.output_attributes

        result = Layer(name=self.output_layer,
                       attributes=output_attributes,
                       parent=None,
                       enveloping=self.enveloping,
                       ambiguous=layer.ambiguous)
        if layer.ambiguous:
            for span_list in layer:
                for sp in span_list:
                    span = rebase_span(span=sp, attributes=output_attributes)
                    result.add_span(span)
        else:
            for sp in layer:
                span = rebase_span(span=sp, attributes=output_attributes)
                result.add_span(span)
        return result


def rebase_span(span, attributes):
    if isinstance(span, SpanList):
        new_span = SpanList()
        new_span.spans = span.spans
        for attr in attributes:
            setattr(new_span, attr, getattr(span, attr))
        return new_span
    if span.parent is None:
        new_span = Span(start=span.start, end=span.end, legal_attributes=attributes)
        for attr in attributes:
            setattr(new_span, attr, getattr(span, attr))
        return new_span
    else:
        return rebase_span(span.parent, attributes)
