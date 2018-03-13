from typing import Sequence, Union

from estnltk.taggers import TaggerNew, read_vocabulary
from estnltk.text import Span, Layer
from estnltk.layer_operations import resolve_conflicts


class TokenListTagger(TaggerNew):
    """
    Tags tokens on a given layer. Creates a layer for which the input layer is the parent layer.
    """
    description = 'Tags tokes on a given layer. Creates a layer with parent.'

    def __init__(self,
                 layer_name: str,
                 input_layer: str,
                 input_attribute: str,
                 vocabulary: Union[dict, str],
                 attributes: Sequence[str]=None,
                 system_attributes: Sequence[str]=None,
                 key: str= '_token_',
                 validator_attribute: str= '_validator_',
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None,
                 ambiguous: bool=False
                 ):
        """Initialize a new TokenListTagger instance.

        Parameters
        ----------
        layer_name: str
            The name of the new layer.
        input_layer: str
            The name of the input layer.
        input_attribute: str
            The name of the input layer attribute.
        vocabulary: dict, str
            A dict that maps attribute values of the input layer to a list of records of the output layer attribute
            values.
            If str, the vocabulary is read from the file 'vocabulary'
        attributes: Sequence[str]
            Output layer attributes.
        system_attributes: Sequence[str]
            System attributes are read from the vocabulary and are even tagged to the spans, but are not declared as the
            layer attributes. These attributes can be used by validator and conflict resolver.
        key: str
            The name of the index column if the vocabulary is read from a csv file.
        validator_attribute: str
            The name of the attribute that points to the validator function in the vocabulary.
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        ambiguous: bool
            Whether the output layer should be ambiguous or not.
        """
        self.conf_param = ('input_attribute', '_vocabulary', 'validator_attribute', 'all_attributes',
                           'conflict_resolving_strategy', 'priority_attribute', 'ambiguous')
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
        if system_attributes is None:
            self.all_attributes = self.attributes
        else:
            assert set(attributes) & set(system_attributes) == set(),\
                'list of attributes and list of system_attributes intersect'
            self.all_attributes = self.attributes + list(system_attributes)

        self.validator_attribute = validator_attribute

        def default_validator(raw_text, span):
            return True

        self.depends_on = [input_layer]

        self.ambiguous = ambiguous

        if isinstance(vocabulary, str):
            self._vocabulary = read_vocabulary(vocabulary_file=vocabulary,
                                               key=key,
                                               string_attributes=[key] + self.all_attributes,
                                               callable_attributes=[self.validator_attribute],
                                               default_rec={self.validator_attribute: default_validator})
        elif isinstance(vocabulary, dict):
            self._vocabulary = vocabulary
        else:
            assert False, 'vocabulary type not supported: ' + str(type(vocabulary))

    def make_layer(self, raw_text: str, input_layers: dict, status: dict):
        input_layer = input_layers[self.depends_on[0]]
        layer = Layer(
            name=self.layer_name,
            attributes=self.attributes,
            parent=input_layer.name,
            ambiguous=self.ambiguous)
        vocabulary = self._vocabulary
        input_attribute = self.input_attribute
        validator_key = self.validator_attribute

        if input_layer.ambiguous:
            for parent_span in input_layer:
                values = set(getattr(parent_span, input_attribute))
                for value in values:
                    if value in vocabulary:
                        for rec in vocabulary[value]:
                            span = Span(parent=parent_span)
                            for attr in self.all_attributes:
                                setattr(span, attr, rec[attr])
                            if rec[validator_key](raw_text, span):
                                layer.add_span(span)
        else:
            for parent_span in input_layer:
                value = getattr(parent_span, input_attribute)
                if value in vocabulary:
                    for rec in vocabulary[value]:
                        span = Span(parent=parent_span)
                        for attr in self.all_attributes:
                            setattr(span, attr, rec[attr])
                        if rec[validator_key](raw_text, span):
                            layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute)
        return layer
