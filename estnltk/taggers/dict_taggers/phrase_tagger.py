from estnltk import EnvelopingSpan, Layer
from estnltk.taggers import Tagger, Vocabulary
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
                 vocabulary: Union[str, list, dict, Vocabulary],
                 key: str=None,
                 output_attributes: Sequence=None,
                 global_validator: callable=None,
                 validator_attribute: str='_validator_',
                 decorator=None,
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None,
                 output_ambiguous: bool=False,
                 case_sensitive=True
                 ):
        """Initialize a new EventSequenceTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param vocabulary: list, dict, str, Vocabulary
            A vocabulary list of records, dict, file name or Vocabulary object.
        :param key: str
            The name of the vocabulary index if the input vocabulary is a list of records, a dict or a csv file.
        :param output_attributes
            Names of the output layer attributes.
        :param global_validator: callable
            Global validator function.
        :param validator_attribute: str
            The name of the attribute that points to the validator function in the vocabulary.
        :param default_values: dict
            Default values for the input vocabulary records.
        :param  conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        :param priority_attribute: str
            Name of the attribute that is used to resolve conflicts.
        :param ambiguous: bool
            Whether the output layer is ambiguous.
        """
        self.conf_param = ('input_attribute', 'vocabulary', 'global_validator', 'validator_attribute', 'decorator',
                           'conflict_resolving_strategy', 'priority_attribute', 'output_ambiguous', '_heads',
                           'case_sensitive')

        self.output_layer = output_layer
        self.input_layers = [input_layer]
        self.input_attribute = input_attribute

        output_attributes = output_attributes or []
        if priority_attribute is not None and priority_attribute not in output_attributes:
            output_attributes.append(priority_attribute)
        self.output_attributes = tuple(output_attributes)

        self.global_validator = global_validator or default_validator

        self.validator_attribute = validator_attribute

        self.decorator = decorator or default_decorator

        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

        self.output_ambiguous = output_ambiguous

        self.vocabulary = Vocabulary(vocabulary=vocabulary,
                                     key=key,
                                     default_rec={self.validator_attribute: default_validator})
        if not case_sensitive:
            self.vocabulary.to_lower()

        assert key is None or key == self.vocabulary.key,\
            'mismatching key and vocabulary.key: {}!={}'.format(key, self.vocabulary.key)
        #assert self.validator_attribute in self.vocabulary.attributes,\
        #    'validator attribute is not among the vocabulary attributes: ' + str(self.validator_attribute)
        #assert set(self.output_attributes) <= set(self.vocabulary.attributes),\
        #    'some output_attributes missing in vocabulary attributes: {}'.format(
        #        set(self.output_attributes)-set(self.vocabulary.attributes))
        #assert self.priority_attribute is None or self.priority_attribute in self.vocabulary.attributes,\
        #    'priority attribute is not among the vocabulary attributes: ' + str(self.priority_attribute)
        assert self.output_ambiguous or all(len(values) == 1 for values in self.vocabulary.values()),\
            'output_ambiguous is False but vocabulary is ambiguous'

        self._heads = defaultdict(list)
        for phrase in self.vocabulary:
            self._heads[phrase[0]].append(phrase[1:])

        self.case_sensitive = case_sensitive

    def _make_layer(self, text, layers: dict, status: dict):
        raw_text = text.text
        input_layer = layers[self.input_layers[0]]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            text_object=text,
            enveloping=input_layer.name,
            ambiguous=self.output_ambiguous)
        heads = self._heads
        value_list = getattr(input_layer, self.input_attribute)
        if input_layer.ambiguous:
            if not self.case_sensitive:
                value_list = [{k.lower() for k in v} for v in value_list]
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
                                    for record in self.vocabulary[phrase]:
                                        span = EnvelopingSpan(spans=input_layer[i:i + len(tail) + 1].spans)
                                        if self.global_validator(span, raw_text) and record[self.validator_attribute](span, raw_text):
                                            rec = {**record, **self.decorator(span, raw_text)}
                                            for attr in self.output_attributes:
                                                attr_value = rec[attr]
                                                if callable(attr_value):
                                                    setattr(span, attr, attr_value(span, raw_text))
                                                else:
                                                    setattr(span, attr, attr_value)
                                            layer.add_span(span)
        else:
            if not self.case_sensitive:
                value_list = [v.lower() for v in value_list]
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
                                for record in self.vocabulary[phrase]:
                                    spans = input_layer.span_list[i:i + len(tail) + 1]
                                    span = EnvelopingSpan(spans=spans)
                                    if self.global_validator(span, raw_text) and record[self.validator_attribute](self, raw_text):
                                        rec = {**record, **self.decorator(span, raw_text)}
                                        for attr in self.output_attributes:
                                            attr_value = rec[attr]
                                            if callable(attr_value):
                                                setattr(span, attr, attr_value(span, raw_text))
                                            else:
                                                setattr(span, attr, attr_value)
                                        layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          keep_equal=True)
        return layer


def default_decorator(span: EnvelopingSpan, raw_text: str) -> dict:
    return {}


def default_validator(span: EnvelopingSpan, raw_text: str) -> bool:
    return True
