from estnltk import Tagger, Layer


class ConllMorphTagger(Tagger):
    """From morph_extended towards conll_syntax"""

    conf_param = []

    def __init__(self, output_layer: str = 'conll_morph', morph_extended_layer: str = 'morph_extended'):
        self.input_layers = [morph_extended_layer]
        self.output_layer = output_layer
        self.output_attributes = ['lemma', 'upostag', 'xpostag', 'feats']

    def _make_layer(self, text, layers, status):
        morph_extended_layer = layers[self.input_layers[0]]

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      parent=morph_extended_layer._base, ambiguous=True)

        for span in morph_extended_layer:
            for annotation in span.annotations:
                layer.add_annotation(span,
                                     lemma=annotation.lemma,
                                     upostag=None,
                                     xpostag=None,
                                     feats=None)

        return layer
