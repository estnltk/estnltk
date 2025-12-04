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

    Note #2: if the input layer is enveloping and contains 
    discontinuous text spans, then, by default, the output layer 
    will still have continuous text spans, covering all the gaps 
    inside spans. 
    However, if you set gaps_strategy='cut_out', then gaps inside 
    spans (signalled by a non-whitspace string between two sub-spans, 
    as described by gaps_pattern) will be cut out, splitting spans 
    correspondingly. Please consult the docstring of the flatten 
    function for more details.

    Note #3: layer's attributes and their names and default values 
    can be changed during the flattening process. Please consult the 
    docstring of the flatten function for details.
    """
    conf_param = ['attribute_mapping', 'default_values', \
                  'gaps_strategy', 'gaps_pattern']

    def __init__(self,
                 input_layer: str,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 attribute_mapping=None,
                 default_values=None,
                 gaps_strategy=None,
                 gaps_pattern=r'\s*\S.*\s*',
                 ):
        self.input_layers = (input_layer, )
        self.output_layer = output_layer
        self.output_attributes = tuple(output_attributes)
        self.attribute_mapping = attribute_mapping
        self.default_values = default_values
        self.gaps_strategy = gaps_strategy
        self.gaps_pattern = gaps_pattern

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
                        default_values=self.default_values,
                        gaps_strategy=self.gaps_strategy, 
                        gaps_pattern=self.gaps_pattern)
        return layer
