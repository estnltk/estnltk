from estnltk import Span
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


class SegmentTagger(Tagger):
    """ Tags and decorates text segments according to the input layer.
    """
    conf_param = ['decorator', 'start_predicate']

    def __init__(self,
                 output_layer,
                 input_layer,
                 output_attributes=(),
                 start_predicate=None,
                 decorator=None):
        self.output_layer = output_layer
        self.input_layers = [input_layer]

        assert bool(output_attributes) is bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.output_attributes = output_attributes
        self.decorator = decorator

        if start_predicate is None:
            start_predicate = lambda span: True
        elif not callable(start_predicate):
            raise ValueError('unexpected type of start_predicate: {}'.format(type(start_predicate)))
        self.start_predicate = start_predicate

    def _make_layer(self, text, layers, status):
        layer = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=text,
                      parent=None,
                      enveloping=None,
                      ambiguous=False)

        input_layer = layers[self.input_layers[0]]
        last_start_span = None
        for span in input_layer:
            if self.start_predicate(span):
                if last_start_span is not None:
                    layer.add_annotation(Span(last_start_span.start, span.start), **self.decorator(last_start_span))
                last_start_span = span
        if last_start_span is not None:
            layer.add_annotation(Span(last_start_span.start, len(text.text)), **self.decorator(last_start_span))

        return layer
