from typing import Sequence, Union

from estnltk.taggers import Tagger, Vocabulary
from estnltk.text import Span, Layer
from estnltk.layer_operations import resolve_conflicts


class SpanTagger(Tagger):
    """
    Tags spans on a given layer. Creates a layer for which the input layer is the parent layer.
    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 vocabulary: Union[dict, str, Vocabulary],
                 key: str = '_token_',
                 output_attributes: Sequence[str] = (),
                 global_validator: callable = None,
                 validator_attribute: str = None,
                 priority_attribute: str = None,
                 ambiguous: bool = False,
                 case_sensitive=True
                 ):
        """Initialize a new TokenListTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param vocabulary: dict, str
            A dict that maps attribute values of the input layer to a list of records of the output layer attribute
            values.
            If str, the vocabulary is read from the file 'vocabulary'
        :param output_attributes: Sequence[str]
            Output layer attributes.
        :param key: str
            The name of the index column if the vocabulary is read from a csv file.
        :param global_validator: callable
            Global global_validator function.
        :param validator_attribute: str
            The name of the attribute that points to the global_validator function in the vocabulary.
        :param priority_attribute
            The name
        :param ambiguous: bool
            Whether the output layer should be ambiguous or not.
        """
        self.conf_param = ('input_attribute', '_vocabulary', 'global_validator', 'validator_attribute',
                           'priority_attribute', 'ambiguous', 'case_sensitive')
        self.priority_attribute = priority_attribute
        self.output_layer = output_layer
        self.input_attribute = input_attribute

        self.output_attributes = tuple(output_attributes)

        self.validator_attribute = validator_attribute

        if global_validator is None:
            global_validator = default_validator
        self.global_validator = global_validator

        self.input_layers = [input_layer]

        self.ambiguous = ambiguous

        if isinstance(vocabulary, Vocabulary):
            self._vocabulary = vocabulary
        else:
            self._vocabulary = Vocabulary.parse(vocabulary=vocabulary,
                                                key=key,
                                                attributes=self.output_attributes,
                                                default_rec={self.validator_attribute: default_validator}
                                                )
        self.case_sensitive = case_sensitive
        if not self.case_sensitive:
            self._vocabulary = self._vocabulary.to_lower()

        if not self.ambiguous:
            assert all(len(values) == 1 for values in self._vocabulary.values()),\
                'ambiguous==False but vocabulary contains ambiguous keywords: '\
                + str([k for k, v in self._vocabulary.items() if len(v) > 1])

    def _make_layer(self, text, layers: dict, status: dict):
        raw_text = text.text
        input_layer = layers[self.input_layers[0]]
        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            text_object=text,
            parent=input_layer.name,
            ambiguous=self.ambiguous)
        vocabulary = self._vocabulary
        input_attribute = self.input_attribute
        validator_key = self.validator_attribute

        case_sensitive = self.case_sensitive
        if input_layer.ambiguous:
            for parent_span in input_layer:
                if case_sensitive:
                    values = set(getattr(parent_span, input_attribute))
                else:
                    values = {v.lower() for v in getattr(parent_span, input_attribute)}
                for value in values:
                    if value in vocabulary:
                        for rec in vocabulary[value]:
                            span = Span(base_span=parent_span.base_span, parent=parent_span, layer=layer)
                            for attr in self.output_attributes:
                                setattr(span, attr, rec[attr])
                            if self.global_validator(raw_text, span):
                                if validator_key is None or rec[validator_key](raw_text, span):
                                    layer.add_span(span)
        else:
            for parent_span in input_layer:
                value = getattr(parent_span, input_attribute)
                if not case_sensitive:
                    value = value.lower()
                if value in vocabulary:
                    for rec in vocabulary[value]:
                        span = Span(base_span=parent_span.base_span, parent=parent_span, layer=layer)
                        for attr in self.output_attributes:
                            setattr(span, attr, rec[attr])
                        if self.global_validator(raw_text, span):
                            if validator_key is None or rec[validator_key](raw_text, span):
                                layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy='ALL',
                          priority_attribute=self.priority_attribute)
        return layer


def default_validator(raw_text, span):
    return True
