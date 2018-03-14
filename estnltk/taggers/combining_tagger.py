from typing import Sequence
from estnltk.taggers import TaggerNew
from estnltk.layer_operations import merge_layers


class CombiningTagger(TaggerNew):
    """Runs input taggers in parallel and resolves conflicts."""
    description = 'Runs input taggers in parallel and resolves conflicts.'
    conf_param = ('_taggers', 'priority_attribute')

    def __init__(self,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 taggers: Sequence[TaggerNew],
                 priority_attribute: str = None
                 ):
        self.output_layer = output_layer
        self.input_layers = tuple({layer for tagger in taggers for layer in tagger.input_layers})
        self._taggers = taggers
        self.output_attributes = output_attributes
        self.priority_attribute = priority_attribute

    def make_layer(self, raw_text, input_layers, status):
        layers = [tagger.make_layer(raw_text, input_layers, status) for tagger in self._taggers]
        return merge_layers(layers=layers,
                            output_layer=self.output_layer,
                            output_attributes=self.output_attributes)
