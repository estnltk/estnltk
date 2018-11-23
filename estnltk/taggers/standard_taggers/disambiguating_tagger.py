from estnltk import Layer, AmbiguousSpan, Span, EnvelopingSpan
from estnltk.taggers import Tagger


def default_decorator(span, raw_text):
    return {}


class DisambiguatingTagger(Tagger):
    """Disambiguates ambiguous layer."""

    conf_param = ('decorator',)

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 output_attributes=(),
                 decorator=default_decorator):
        self.input_layers = [input_layer]
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.decorator = decorator

    def _make_layer(self, text, layers, status):
        input_layer = layers[self.input_layers[0]]
        parent = input_layer.parent
        enveloping = input_layer.enveloping
        layer = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=text,
                      parent=parent,
                      enveloping=enveloping,
                      ambiguous=False)
        for input_span in input_layer:
            assert isinstance(input_span, AmbiguousSpan)
            if parent:
                span = Span(parent=parent,
                            legal_attributes=self.output_attributes)
            elif enveloping:
                span = EnvelopingSpan(spans=input_span[0].spans)
            else:
                span = Span(start=input_span[0].start,
                            end=input_span[0].end,
                            legal_attributes=self.output_attributes)
            for k, v in self.decorator(input_span, text.text).items():
                setattr(span, k, v)
            layer.add_span(span)
        return layer
