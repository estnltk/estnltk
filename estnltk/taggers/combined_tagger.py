from typing import Sequence
from estnltk.taggers import Tagger
from estnltk.layer_operations import merge_layers, resolve_conflicts


class CombinedTagger(Tagger):
    """Runs input taggers in parallel and resolves conflicts."""
    conf_param = ('taggers', 'priority_attribute', 'conflict_resolving_strategy')

    def __init__(self,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 taggers: Sequence[Tagger],
                 conflict_resolving_strategy: str='ALL',
                 priority_attribute: str = None
                 ):
        self.output_layer = output_layer
        self.input_layers = tuple({layer for tagger in taggers for layer in tagger.input_layers})
        self.taggers = taggers
        self.output_attributes = output_attributes
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

    def _make_layer(self, raw_text, input_layers, status):
        layers = [tagger.make_layer(raw_text, input_layers, status) for tagger in self.taggers]
        layer = merge_layers(layers=layers,
                             output_layer=self.output_layer,
                             output_attributes=self.output_attributes)
        resolve_conflicts(layer=layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          status=status)
        return layer
