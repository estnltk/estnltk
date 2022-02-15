from typing import Sequence

from estnltk.taggers import Tagger
from estnltk_core.layer_operations import flatten


class FlattenTagger(Tagger):
    """ Flattens input layer.
    In other words: reduces an enveloping layer or a layer with 
    parent to a simple layer (enveloping=None, parent=None). 
    This means that the output layer is assured to have span 
    level 0 (enveloping layer will always be reduced).
    
    Note #1: the operation preserves ambiguities, and the output 
    layer will always be ambiguous. This is the way the flatten 
    function works. If you want to get unambiguous layer, please 
    apply the flatten function manually with disambiguation_strategy 
    parameter ( the function can be imported from module:
    estnltk_core.layer_operations.flatten ) or apply a 
    Disambiguator on the output layer. 
    
    Note #2: layer's attributes and their names and default values 
    can be changed during the flattening process. Please consult the 
    docstring of the flatten function for details.
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
                     ambiguous=True)

    def _make_layer(self, text, layers, status):
        layer = flatten(input_layer=layers[self.input_layers[0]],
                        output_layer=self.output_layer,
                        output_attributes=self.output_attributes,
                        attribute_mapping=self.attribute_mapping,
                        default_values=self.default_values)
        return layer
