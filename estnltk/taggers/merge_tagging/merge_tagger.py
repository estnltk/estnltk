from estnltk.layer import Layer
from estnltk.taggers import TaggerNew
from estnltk.layer_operations import merge_layers


class MergeTagger(TaggerNew):
    """ Merges input layers.
    """
    description = 'Merges input layers.'
    conf_param = ()

    def __init__(self, layer_name, input_layers, attributes=()):
        self.depends_on = input_layers
        assert len(self.depends_on) > 0
        self.layer_name = layer_name
        self.attributes = tuple(attributes)

    def make_layer(self, text, input_layers, status):
        layers = list(input_layers.values())
        return merge_layers(layers, self.layer_name, self.attributes)
