from estnltk.taggers import Retagger


class AnnotationRewriter(Retagger):
    """Applies a modifying function for every annotation.

    """
    conf_param = ['function']

    def __init__(self, layer_name, output_attributes, function):
        self.output_layer = layer_name
        self.input_layers = [layer_name]
        self.output_attributes = output_attributes
        self.function = function

    def _change_layer(self, text, layers, status):
        layer = layers[self.output_layer]
        layer.attributes = layer.attributes + self.output_attributes
        function = self.function

        for span in layer:
            for annotation in span.annotations:
                function(annotation)
        return layer
