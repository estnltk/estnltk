from estnltk.taggers import Tagger, read_vocabulary
from estnltk.layer import Layer
from estnltk.layer_operations import resolve_conflicts
from collections import defaultdict
from typing import Sequence, Union


class PhraseTagger(Tagger):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """
    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 vocabulary: Union[str, dict]=None,
                 key: str='_phrase_',
                 output_attributes: Sequence=None,
                 global_validator: callable=None,
                 validator_attribute: str='_validator_',
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None,
                 ambiguous: bool=False
                 ):
        """Initialize a new EventSequenceTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param vocabulary: dict, str
            A vocabulary dict or file name.
        :param global_validator: callable
            Global global_validator function.
        :param validator_attribute: str
            The name of the attribute that points to the global_validator function in the vocabulary.
        :param key: str
            The name of the index column if the vocabulary is read from a csv file.
        :param  conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        """
        self.conf_param = ('input_attribute', 'global_validator', 'validator_attribute', 'conflict_resolving_strategy',
                           'priority_attribute', 'ambiguous', '_vocabulary', '_heads')
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

        self.validator_attribute = validator_attribute
        if global_validator is None:
            self.global_validator = default_validator
        else:
            self.global_validator = global_validator

        self.input_layers = [input_layer]

        self.ambiguous = ambiguous

        if isinstance(vocabulary, str):
            if priority_attribute is None:
                callable_attributes = (key,)
            else:
                callable_attributes = (key, priority_attribute)

            str_attributes = [attr for attr in self.output_attributes if attr not in callable_attributes]

            self._vocabulary = read_vocabulary(vocabulary_file=vocabulary,
                                               key=key,
                                               string_attributes=str_attributes,
                                               callable_attributes=callable_attributes,
                                               default_rec={self.validator_attribute: default_validator})
        else:
            self._vocabulary = vocabulary

        self._heads = defaultdict(list)
        for phrase in self._vocabulary:
            self._heads[phrase[0]].append(phrase[1:])

    def make_layer(self, raw_text: str, layers: dict, status: dict):
        input_layer = layers[self.input_layers[0]]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            enveloping=input_layer.name,
            ambiguous=self.ambiguous)
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
                                        if self.global_validator(raw_text, span) and rec[self.validator_attribute](raw_text, span):
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
                                    if self.global_validator(raw_text, span) and rec[self.validator_attribute](raw_text, span):
                                        for attr in self.output_attributes:
                                            setattr(span, attr, rec[attr])
                                        layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute)
        return layer


def default_validator(text, span):
    return True
