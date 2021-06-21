from typing import Sequence

from estnltk.taggers import Tagger
from estnltk.layer_operations import merge_layers


class MergeTagger(Tagger):
    """ Merges input layers.
    """
    conf_param = ()

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 output_attributes: Sequence[str]=()):
        self.input_layers = input_layers
        assert len(self.input_layers) > 0
        self.output_layer = output_layer
        self.output_attributes = tuple(output_attributes)

    def _make_layer_template(self):
        raise NotImplementedError( '(!) Unable to create the template layer. '+\
                                  ('Exact configuration of the new layer depends on the input layer {!r}').format(self.input_layers[0]) )

    def _make_layer(self, text, layers, status):
        layers = [layers[layer] for layer in self.input_layers]
        return merge_layers(layers=layers,
                            output_layer=self.output_layer,
                            output_attributes=self.output_attributes,
                            text=text)
