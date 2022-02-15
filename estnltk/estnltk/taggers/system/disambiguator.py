from estnltk import Layer
from estnltk.taggers import Tagger


def default_decorator(span, raw_text):
    return {}


class Disambiguator(Tagger):
    """Disambiguates ambiguous layer.
    In other words: assigns a single annotation 
    to each span of the layer.
    
    Note: this is a system level tagger for 
    creating a disambiguator. Not to be confused 
    with concrete linguistic disambiguators, 
    such as VabamorfDisambiguator.

    Disambiguation is done by a decorator function, 
    which is applied on every span of the input 
    layer.
    The decorator function takes 2 input parameters: 
    span and raw_text corresponding to the span. 
    The function is expected to pick one of the span's 
    annotations (or, alternatively, create a new 
    annotation based on existing ones) and return 
    as the result of the disambiguation. 
    Returned annotation should be in form of a 
    dictionary containing attributes & values. 
   
    If the decorator function is not specified, 
    default_decorator is used, which returns {} 
    on any input. This means that each annotation 
    obtains default values of the layer (None 
    values, if defaults are not set).
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
