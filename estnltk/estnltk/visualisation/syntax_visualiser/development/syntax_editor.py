from estnltk.taggers import AttributeComparator


class SyntaxEditor:
    def __init__(self, layers, input_attributes, attributes_to_compare, output_layer="curated_syntax_layer"):
        input_layers = [layer.name for layer in layers]
        text = layers[0].text_object
        layers_dict = {layer.name: layer for layer in layers}
        tagger = AttributeComparator(output_layer, input_layers, input_attributes, attributes_to_compare)
        self.layer = tagger.make_layer(text, layers_dict)
