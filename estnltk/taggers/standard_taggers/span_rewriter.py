from estnltk import Annotation
from estnltk.taggers import Retagger


class SpanRewriter(Retagger):
    """Rewrites span annotations.

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
        attributes = layer.attributes

        for span in layer:
            records = span.to_records()
            records = self.function(records)

            span.clear_annotations()
            for record in records:
                span.add_annotation(Annotation(span, **{attr: record[attr] for attr in attributes}))
        return layer
