from estnltk import Layer
from estnltk.taggers import Retagger


def default_decorator(span, raw_text):
    return {}


class Disambiguator(Retagger):
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
    
    Note: Disambiguator works either as a tagger or 
    as a retagger, depending on whether the input 
    layer is different than the output layer. 
    If output_layer == input_layer, then Disambiguator
    works as a retagger and the layer can be changed 
    by calling tagger's retag(...) or change_layer(...)
    methods.
    If output_layer != input_layer, then Disambiguator
    works as a tagger and new layer can be made by 
    calling tagger's tag(...) or make_layer(...)
    methods.
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
        assert self.input_layers[0] != self.output_layer, \
            ('cannot make new layer: input_layer and output_layer have the same name: {!r}. '+\
             'call retag() or change_layer() instead.').format(self.output_layer)
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
            annotation = decorator(input_span, text.text)
            layer.add_annotation(input_span.base_span, annotation)

        return layer

    def _change_layer(self, text, layers, status):
        input_layer = layers[self.input_layers[0]]
        assert input_layer.ambiguous, 'the input layer is not ambguous'
        assert self.input_layers[0] == self.output_layer, \
            ('cannot modify layer: input_layer {!r} has different name than output_layer {!r}. '+\
             'call tag() or make_layer() instead.').format(self.input_layers[0], self.output_layer)
        input_layer.attributes = self.output_attributes
        decorator = self.decorator
        for input_span in input_layer:
            annotation = decorator(input_span, text.text)
            input_span.clear_annotations()
            input_span.add_annotation( annotation )
        input_layer.ambiguous = False

