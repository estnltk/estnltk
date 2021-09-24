from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


def default_decorator(span, raw_text):
    return {}


class DisambiguatingTagger(Tagger):
    """Disambiguates ambiguous layer.

    """
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

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        raise NotImplementedError( '(!) Unable to create the template layer. '+\
                                  ('Exact configuration of the new layer depends on the input layer {!r}').format(self.input_layers[0]) )

    def _make_layer(self, text, layers, status):
        input_layer = layers[self.input_layers[0]]
        assert input_layer.ambiguous, 'the input layer is not ambguous'

        parent = input_layer.parent
        enveloping = input_layer.enveloping
        layer = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=text,
                      parent=parent,
                      enveloping=enveloping,
                      ambiguous=False)

        decorator = self.decorator
        for input_span in input_layer:
            layer.add_annotation(input_span.base_span, **decorator(input_span, text.text))

        return layer
