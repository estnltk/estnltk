from typing import Sequence

from estnltk.taggers import Tagger
from estnltk_core.layer_operations import flatten


class FlattenTagger(Tagger):
    """ Flattens input layer.
    """
    conf_param = ['attribute_mapping', 'default_values']

    def __init__(self,
                 input_layer: str,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 attribute_mapping=None,
                 default_values=None
                 ):
        self.input_layers = (input_layer, )
        self.output_layer = output_layer
        self.output_attributes = tuple(output_attributes)
        self.attribute_mapping = attribute_mapping
        self.default_values = default_values

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     parent=None,
                     enveloping=None,
                     ambiguous=False)

    def _make_layer(self, text, layers, status):
        layer = flatten(input_layer=layers[self.input_layers[0]],
                        output_layer=self.output_layer,
                        output_attributes=self.output_attributes,
                        attribute_mapping=self.attribute_mapping,
                        default_values=self.default_values)
        return layer
