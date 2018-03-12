from estnltk.taggers import TaggerNew, read_vocabulary
from estnltk.layer import Layer
from estnltk.layer_operations import resolve_conflicts
from collections import defaultdict
from typing import Sequence


class PhraseListTagger(TaggerNew):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """
    description = 'Tags phrases on a given layer. Creates an enveloping layer.'

    def __init__(self,
                 layer_name: str,
                 input_layer: str,
                 input_attribute: str,
                 vocabulary: dict=None,
                 attributes: Sequence=None,
                 validator: callable=None,
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None
                 ):
        """Initialize a new EventSequenceTagger instance.

        Parameters
        ----------
        layer_name: str
            The name of the new layer.
        input_layer: str
            The name of the input layer.
        input_attribute: str
            The name of the input layer attribute.
        phrase_list: list of tuples
            input layer attribute value tuples to annotate
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        """
        self.conf_param = ('input_attribute', 'validator',
                           'conflict_resolving_strategy', 'priority_attribute',
                           'vocabulary', '_heads', 'all_attributes')
        if conflict_resolving_strategy not in {'ALL', 'MIN', 'MAX'}:
            raise ValueError('Unknown conflict_resolving_strategy: ' + str(conflict_resolving_strategy))
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute
        self.layer_name = layer_name
        self.input_attribute = input_attribute
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = list(attributes)

        def default_validator(text, span, phrase):
            return True

        if validator is None:
            self.validator = default_validator
        else:
            self.validator = validator

        self.depends_on = [input_layer]

        self.all_attributes = set(self.attributes)
        if priority_attribute is not None:
            self.all_attributes.add(priority_attribute)
        self.all_attributes = tuple(self.all_attributes)

        if isinstance(vocabulary, str):
            if priority_attribute is not None:
                eval_attributes = ('_phrase_', priority_attribute)
            else:
                eval_attributes = ('_phrase_',)

            self.vocabulary = read_vocabulary(vocabulary_file=vocabulary,
                                              index='_phrase_',
                                              str_attributes=self.attributes,
                                              eval_attributes=eval_attributes)
        else:
            self.vocabulary = vocabulary

        self._heads = defaultdict(list)
        for phrase in self.vocabulary:
            self._heads[phrase[0]].append(phrase[1:])

    def make_layer(self, raw_text: str, input_layers: dict, status: dict):
        input_layer = input_layers[self.depends_on[0]]
        layer = Layer(
            name=self.layer_name,
            attributes=self.attributes,
            enveloping=input_layer.name,
            ambiguous=False)
        heads = self._heads
        value_list = getattr(input_layer, self.input_attribute)
        if input_layer.ambiguous:
            for i, values in enumerate(value_list):
                for value in set(values):
                    if value in heads:
                        for tail in heads[value]:
                            if i + len(tail) < len(value_list):
                                match = True
                                for a, b in zip(tail, value_list[i + 1:i + len(tail) + 1]):
                                    if a not in b:
                                        match = False
                                        break
                                if match:
                                    phrase = (value,) + tail
                                    for rec in self.vocabulary[phrase]:
                                        span = input_layer.spans[i:i + len(tail) + 1]
                                        if self.validator(raw_text, span, phrase):
                                            for attr in self.all_attributes:
                                                setattr(span, attr, rec[attr])
                                            layer.add_span(span)
        else:
            for i, value in enumerate(value_list):
                if value in heads:
                    for tail in heads[value]:
                        if i + len(tail) < len(value_list):
                            match = True
                            for a, b in zip(tail, value_list[i + 1:i + len(tail) + 1]):
                                if a != b:
                                    match = False
                                    break
                            if match:
                                phrase = (value,) + tail
                                for rec in self.vocabulary[phrase]:
                                    span = input_layer.spans[i:i + len(tail) + 1]
                                    if self.validator(raw_text, span, phrase):
                                        for attr in self.attributes:
                                            setattr(span, attr, rec[attr])
                                        layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute)
        return layer
