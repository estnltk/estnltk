from estnltk.layer.span import Span
from estnltk.layer.ambiguous_span import AmbiguousSpan
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.layer import Layer
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
        self.output_attributes = tuple(output_attributes)
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
                # TODO: test and rewrite using add_annotation
                span = Span(parent=parent,
                            layer=layer)
                for k, v in self.decorator(input_span, text.text).items():
                    setattr(span[0], k, v)
                layer.add_span(span)
            elif enveloping:
                span = EnvelopingSpan(spans=input_span[0].spans, layer=layer)
                for k, v in self.decorator(input_span, text.text).items():
                    setattr(span, k, v)
                layer.add_span(span)
            else:
                layer.add_annotation((input_span.start, input_span.end), **self.decorator(input_span, text.text))

        return layer
