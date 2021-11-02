from typing import Sequence
from estnltk_core.taggers import Tagger
from estnltk_core.layer_operations import resolve_conflicts


class SequentialTagger(Tagger):
    """
    Runs input taggers sequentially and resolves conflicts.
    The output of the last tagger is returned.
    """
    conf_param = ('_taggers', 'priority_attribute', 'conflict_resolving_strategy')

    def __init__(self,
                 taggers: Sequence[Tagger],
                 conflict_resolving_strategy: str = 'ALL',
                 priority_attribute: str = None):
        assert len(taggers) > 0
        self.output_layer = taggers[-1].output_layer

        intermediate_layers = {tagger.output_layer for tagger in taggers}
        self.input_layers = tuple({layer for tagger in taggers for layer in tagger.input_layers
                                   if layer not in intermediate_layers})

        self._taggers = taggers
        self.output_attributes = taggers[-1].output_attributes
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

    def _make_layer(self, text, layers, status):
        layers = dict(layers)
        for tagger in self._taggers:
            layer = tagger.make_layer(text, layers, status)
            layers[layer.name] = layer

        resolve_conflicts(layer=layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          status=status)
        return layer
