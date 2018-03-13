from estnltk.taggers import TaggerNew, read_vocabulary
from estnltk.layer import Layer
from estnltk.layer_operations import resolve_conflicts
from collections import defaultdict
from typing import Sequence, Union


class PhraseTagger(TaggerNew):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """
    description = 'Tags phrases on a given layer. Creates an enveloping layer.'

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 vocabulary: Union[str, dict]=None,
                 key: str='_phrase_',
                 output_attributes: Sequence=None,
                 validator: callable=None,
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None
                 ):
        """Initialize a new EventSequenceTagger instance.

        Parameters
        ----------
        output_layer: str
            The name of the new layer.
        input_layer: str
            The name of the input layer.
        input_attribute: str
            The name of the input layer attribute.
        vocabulary: dict, str
            A vocablary dict or file name.
        key: str
            The name of the index column if the vocabulary is read from a csv file.
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        """
        self.conf_param = ('input_attribute', 'validator',
                           'conflict_resolving_strategy', 'priority_attribute',
                           '_vocabulary', '_heads')
        if conflict_resolving_strategy not in {'ALL', 'MIN', 'MAX'}:
            raise ValueError('Unknown conflict_resolving_strategy: ' + str(conflict_resolving_strategy))
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute
        self.output_layer = output_layer
        self.input_attribute = input_attribute
        if output_attributes is None:
            self.output_attributes = []
        else:
            self.output_attributes = list(output_attributes)

        if validator is None:
            self.validator = default_validator
        else:
            self.validator = validator

        self.input_layers = [input_layer]

        if isinstance(vocabulary, str):
            if priority_attribute is None:
                callable_attributes = (key,)
            else:
                callable_attributes = (key, priority_attribute)

            str_attributes = [attr for attr in self.output_attributes if attr not in callable_attributes]

            self._vocabulary = read_vocabulary(vocabulary_file=vocabulary,
                                               key=key,
                                               string_attributes=str_attributes,
                                               callable_attributes=callable_attributes)
        else:
            self._vocabulary = vocabulary

        self._heads = defaultdict(list)
        for phrase in self._vocabulary:
            self._heads[phrase[0]].append(phrase[1:])

    def make_layer(self, raw_text: str, input_layers: dict, status: dict):
        input_layer = input_layers[self.input_layers[0]]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
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
                                    for rec in self._vocabulary[phrase]:
                                        span = input_layer.spans[i:i + len(tail) + 1]
                                        if self.validator(raw_text, span):
                                            for attr in self.output_attributes:
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
                                for rec in self._vocabulary[phrase]:
                                    span = input_layer.spans[i:i + len(tail) + 1]
                                    if self.validator(raw_text, span):
                                        for attr in self.output_attributes:
                                            setattr(span, attr, rec[attr])
                                        layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute)
        return layer


def default_validator(text, span):
    return True
