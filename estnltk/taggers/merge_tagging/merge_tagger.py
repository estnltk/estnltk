from estnltk.layer import Layer
from estnltk.taggers import Tagger
from estnltk.layer_operations import merge_layers


class MergeTagger(Tagger):
    """ Merges input layers.
    """
    description = 'Merges input layers.'
    layer_name = ''
    attributes = ()
    depends_on = []
    configuration = {}

    def __init__(self, layer_name, input_layers, attributes=()):
        self.depends_on = input_layers
        assert len(self.depends_on) > 0
        self.layer_name = layer_name
        self.attributes = tuple(attributes)

    def _make_layer(self, text, layers):
        layers = [layers[name] for name in self.depends_on]
        return merge_layers(layers, self.layer_name, self.attributes)

    def tag(self, text):
        layer = self._make_layer(text.text, text.layers)
        assert isinstance(layer, Layer), 'make_layer must return a Layer instance'
        text[self.layer_name] = layer
