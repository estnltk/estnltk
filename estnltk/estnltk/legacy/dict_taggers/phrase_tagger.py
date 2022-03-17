from collections import defaultdict
from typing import Sequence, Union

from estnltk import Annotation, EnvelopingBaseSpan
from estnltk import EnvelopingSpan
from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk.legacy.dict_taggers.vocabulary import Vocabulary
from estnltk_core.layer_operations import resolve_conflicts


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
                 decorator=None,
                 conflict_resolving_strategy: str='MAX',
                 priority_attribute: str=None,
                 output_ambiguous: bool=False,
                 ignore_case=False
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
        self.conf_param = ('input_attribute', 'vocabulary', 'decorator',
                           'conflict_resolving_strategy', 'priority_attribute', 'output_ambiguous', '_heads',
                           'ignore_case')

        self.output_layer = output_layer
        self.input_layers = [input_layer]
        self.input_attribute = input_attribute

        output_attributes = output_attributes or []
        if priority_attribute is not None and priority_attribute not in output_attributes:
            output_attributes.append(priority_attribute)
        self.output_attributes = tuple(output_attributes)

        self.decorator = decorator or default_decorator

        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

        self.output_ambiguous = output_ambiguous

        self.vocabulary = Vocabulary.parse(vocabulary=vocabulary,
                                           key=key,
                                           attributes=list({key, *self.output_attributes}),
                                           default_rec={**{attr: None for attr in self.output_attributes}}
                                           )

        self.ignore_case = ignore_case
        if ignore_case:
            self.vocabulary = self.vocabulary.to_lower()

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

    def _make_layer_template(self):
        return Layer( name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=None,
                      enveloping=self.input_layers[0],
                      ambiguous=self.output_ambiguous )

    def _make_layer(self, text, layers: dict, status=None):
        input_layer = layers[self.input_layers[0]]
        layer = self._make_layer_template()
        layer.text_object=text

        if self.ignore_case:
            if self.input_attribute == 'text':
                get_value = lambda annotation: annotation.text.lower()
            else:
                get_value = lambda annotation: annotation[self.input_attribute].lower()
        else:
            if self.input_attribute == 'text':
                get_value = lambda annotation: annotation.text
            else:
                get_value = lambda annotation: annotation[self.input_attribute]

        value_list = [{get_value(annotation) for annotation in span.annotations} for span in input_layer]

        heads = self._heads
        output_attributes = self.output_attributes
        for i, values in enumerate(value_list):
            for value in values:
                if value not in heads:
                    continue
                for tail in heads[value]:
                    if i + len(tail) < len(value_list):
                        for a, b in zip(tail, value_list[i + 1:i + len(tail) + 1]):
                            if a not in b:
                                break
                        else:  # no break
                            phrase = (value, *tail)
                            base_span = EnvelopingBaseSpan(s.base_span
                                                           for s in input_layer[i:i + len(tail) + 1])
                            span = EnvelopingSpan(base_span=base_span, layer=layer)
                            for record in self.vocabulary[phrase]:
                                #print(record)
                                #print(output_attributes)
                                annotation = Annotation(span, **{attr: record[attr]
                                                                 for attr in output_attributes})
                                is_valid =  self.decorator(span, annotation)
                                assert isinstance(is_valid, bool), is_valid
                                if not is_valid:
                                    continue
                                span.add_annotation(annotation)
                            if span.annotations:
                                layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          keep_equal=True)
        return layer


def default_decorator(span, annotation: Annotation) -> bool:
    return True
