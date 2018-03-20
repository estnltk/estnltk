from typing import Sequence
from estnltk.taggers import Tagger
from estnltk.layer_operations import resolve_conflicts


class SequentialTagger(Tagger):
    """Runs input taggers sequentially and resolves conflicts.
    The output of the last tagger is returned.
    """
    conf_param = ('_taggers', 'priority_attribute', 'conflict_resolving_strategy')

    def __init__(self,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 taggers: Sequence[Tagger],
                 conflict_resolving_strategy: str='ALL',
                 priority_attribute: str = None
                 ):
        self.output_layer = output_layer
        self.input_layers = tuple({layer for tagger in taggers for layer in tagger.input_layers})
        self._taggers = taggers
        self.output_attributes = output_attributes
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

    def _make_layer(self, raw_text, input_layers, status):
        assert self._taggers[-1].output_layer == self.output_layer
        assert self._taggers[-1].output_attributes == self.output_attributes,\
            'unexpected output_attributes: ' + str(self._taggers[-1].output_attributes)

        input_layers = dict(input_layers)
        for tagger in self._taggers:
            layer = tagger.make_layer(raw_text, input_layers, status)
            input_layers[layer.name] = layer

        resolve_conflicts(layer=layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          status=status)
        return layer
