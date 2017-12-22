from estnltk.spans import Span
from estnltk.layer import Layer
from estnltk.taggers import Tagger
from estnltk.taggers.gaps_tagging.gaps_tagger import GapsTagger


class MergeTagger(Tagger):
    """ Merges input layers.
    """
    description = 'Merges input layers.'
    layer_name = ''
    attributes = ()
    depends_on = []
    configuration = {}

    def __init__(self, layer_name, input_layers, attributes=(), tag_gaps=False):
        self.depends_on = input_layers
        assert len(self.depends_on) > 0
        self.layer_name = layer_name
        self.attributes = tuple(attributes)
        self.configuration['tag_gaps'] = tag_gaps
        self.gaps_tagger = GapsTagger('_gaps_', self.depends_on)

    def make_layer(self, text, layers):
        layers = [layers[name] for name in self.depends_on]
        parent = layers[0].parent
        enveloping = layers[0].enveloping
        ambiguous = layers[0].ambiguous
        assert all(layer.parent == parent for layer in layers)
        assert all(layer.enveloping == enveloping for layer in layers)
        assert all(layer.ambiguous == ambiguous for layer in layers)
        attributes = self.attributes
        if self.configuration['tag_gaps']:
            gaps_layer = self.gaps_tagger.make_layer(text, layers)
            layers['_gaps_'] = gaps_layer

        new_layer = Layer(
            name=self.layer_name,
            attributes=attributes,
            parent=parent,
            enveloping=enveloping,
            ambiguous=ambiguous
            )

        for layer in layers:
            layer_attributes = layer.attributes
            none_attributes = [attr for attr in attributes if attr not in layer_attributes]
            for span in layer:
                new_span = Span(span.start, span.end, legal_attributes=attributes)
                for attr in layer_attributes:
                    setattr(new_span, attr, getattr(span, attr))
                for attr in none_attributes:
                    setattr(new_span, attr, None)
                new_layer.add_span(new_span)

        return new_layer

    def tag(self, text):
        layer = self.make_layer(text.text, text.layers)
        assert isinstance(layer, Layer), 'make_layer must return a Layer instance'
        text[self.layer_name] = layer
