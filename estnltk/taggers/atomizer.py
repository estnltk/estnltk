from typing import Sequence
from estnltk.taggers import Tagger
from estnltk.text import Span, SpanList, Layer


class Atomizer(Tagger):
    """Forgets the parents of the input layer.

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
                    span = _rebase_span(span=sp, legal_attributes=output_attributes)
                    for attr in output_attributes:
                        setattr(span, attr, getattr(sp, attr))
                    result.add_span(span)
        else:
            for sp in layer:
                span = _rebase_span(span=sp, legal_attributes=output_attributes)
                for attr in output_attributes:
                    setattr(span, attr, getattr(sp, attr))
                result.add_span(span)
        return result


def _rebase_span(span, legal_attributes):
    if isinstance(span, SpanList):
        new_span = SpanList()
        new_span.spans = span.spans
        return new_span
    if span.parent is None:
        return Span(start=span.start, end=span.end, legal_attributes=legal_attributes)
    else:
        return _rebase_span(span.parent, legal_attributes)
