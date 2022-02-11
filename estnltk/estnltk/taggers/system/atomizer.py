from typing import Sequence
from estnltk_core.taggers import Tagger
from estnltk_core import Span
from estnltk_core import SpanList
from estnltk_core import Layer


class Atomizer(Tagger):
    """ Forgets the parent of the input layer. 
    In detail: makes the input layer independent of the parent 
    (parent=None), while preserving its span level (if the input is 
    an enveloping layer, it remains an enveloping layer with the same 
    span level). 
    Outputs an enveloping or simple (enveloping=None, parent=None) 
    layer. 
    
    Note #1: layer's attributes can be reduced to a smaller subset 
    of attributes during the atomizing process. Use parameter 
    output_attributes to specify the subset.
    """
    conf_param = ('enveloping',)

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 output_attributes: Sequence[str]=None,
                 enveloping: str = None
                 ):
        self.output_layer = output_layer
        self.input_layers = [input_layer]
        self.output_attributes = tuple(output_attributes)
        self.enveloping = enveloping

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        raise NotImplementedError( '(!) Unable to create the template layer. '+\
                                  ('Exact configuration of the new layer depends on the input layer {!r}').format(self.input_layers[0]) )

    def _make_layer(self, text, layers, status):
        layer = layers[self.input_layers[0]]
        if self.output_attributes is None:
            output_attributes = layer.attributes
        else:
            output_attributes = self.output_attributes

        result = Layer(name=self.output_layer,
                       attributes=output_attributes,
                       text_object=text,
                       parent=None,
                       enveloping=self.enveloping,
                       ambiguous=layer.ambiguous)
        if layer.ambiguous:
            for span in layer:
                for annotation in span.annotations:
                    result.add_annotation((span.start, span.end), **annotation)
        else:
            for sp in layer:
                span = _rebase_span(span=sp, legal_attributes=output_attributes)
                for attr in output_attributes:
                    setattr(span, attr, getattr(sp, attr))
                result.add_span(span)
        return result


def _rebase_span(span, legal_attributes):
    if isinstance(span, SpanList):
        new_span = SpanList(span_level=span.span_level)
        new_span.spans = span.spans
        return new_span

    if span.span.parent is None:
        return Span(start=span.start, end=span.end, legal_attributes=legal_attributes)

    return _rebase_span(span.parent, legal_attributes)
