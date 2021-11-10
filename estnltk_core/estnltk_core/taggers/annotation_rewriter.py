from estnltk_core.taggers import Retagger


class AnnotationRewriter(Retagger):
    """Applies a modifying function for every annotation.

    """
    conf_param = ['check_output_consistency', 'function']

    def __init__(self, layer_name, output_attributes, function, check_output_consistency=False):
        self.output_layer = layer_name
        self.input_layers = [layer_name]
        self.output_attributes = output_attributes
        self.function = function
        self.check_output_consistency = check_output_consistency

    def _change_layer(self, text, layers, status):
        layer = layers[self.output_layer]
        layer_attributes = layer.attributes
        layer.attributes = [*layer_attributes,
                            *(attr for attr in self.output_attributes if attr not in layer_attributes)]
        function = self.function

        for span in layer:
            for annotation in span.annotations:
                function(annotation)
        return layer
