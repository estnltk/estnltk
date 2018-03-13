from typing import Sequence

from estnltk.taggers import TaggerNew
from estnltk.layer_operations import merge_layers


class MergeTagger(TaggerNew):
    """ Merges input layers.
    """
    description = 'Merges input layers.'
    conf_param = ()

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 output_attributes: Sequence[str]=()):
        self.input_layers = input_layers
        assert len(self.input_layers) > 0
        self.output_layer = output_layer
        self.output_attributes = tuple(output_attributes)

    def make_layer(self, text, input_layers, status):
        layers = list(input_layers.values())
        return merge_layers(layers, self.output_layer, self.output_attributes)
