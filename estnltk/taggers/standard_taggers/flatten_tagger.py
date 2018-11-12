from typing import Sequence

from estnltk.taggers import Tagger
from estnltk.layer_operations import flatten


class FlattenTagger(Tagger):
    """ Flattens input layer.
    """
    conf_param = []

    def __init__(self,
                 input_layer: str,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 ):
        self.input_layers = (input_layer, )
        self.output_layer = output_layer

        self.output_attributes = tuple(output_attributes)

    def _make_layer(self, raw_text, layers, status):
        layer = flatten(layer=layers[self.input_layers[0]],
                        layer_name=self.output_layer,
                        attributes=self.output_attributes)
        return layer
