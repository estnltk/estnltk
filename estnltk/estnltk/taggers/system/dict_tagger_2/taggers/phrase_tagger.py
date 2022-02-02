import copy
from collections import defaultdict
from typing import Sequence

from estnltk import Annotation, EnvelopingBaseSpan
from estnltk import EnvelopingSpan
from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk.taggers.system.dict_tagger_2.extraction_rules.ambiguous_ruleset import AmbiguousRuleset
from estnltk.taggers.system.dict_tagger_2.extraction_rules.ruleset import Ruleset
from estnltk_core.layer_operations import resolve_conflicts


class PhraseTagger(Tagger):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 ruleset: AmbiguousRuleset,
                 key: str = '_phrase_',
                 output_attributes: Sequence = None,
                 decorator=None,
                 conflict_resolving_strategy: str = 'MAX',
                 priority_attribute: str = None,
                 ignore_case=False
                 ):
        """Initialize a new EventSequenceTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param ruleset: AmbiguousRuleset
            Ruleset of type Ruleset or AmbiguousRuleset
        :param key: str
            The name of the vocabulary index if the input vocabulary is a list of records, a dict or a csv file.
        :param decorator: Callable
            Decorator function for spans
        :param output_attributes
            Names of the output layer attributes.
        :param  conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        :param priority_attribute: str
            Name of the attribute that is used to resolve conflicts.
        """
        self.conf_param = ('input_attribute', 'ruleset', 'decorator',
                           'conflict_resolving_strategy', 'priority_attribute', '_heads',
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

        self.extend_ruleset(ruleset, key)


        self.ignore_case = ignore_case

        if ignore_case:
            for rule in self.ruleset.static_rules:
                for i in range(len(rule.pattern)):
                    rule.pattern[i] = rule.pattern[i].lower()

        # assert key is None or key == self.vocabulary.key,\
        #    'mismatching key and vocabulary.key: {}!={}'.format(key, self.vocabulary.key)
        ## key can not be tested like this anymore because ruleset does not have the key attribute
        # assert set(self.output_attributes) <= set(self.vocabulary.attributes),\
        #    'some output_attributes missing in vocabulary attributes: {}'.format(
        #        set(self.output_attributes)-set(self.vocabulary.attributes))
        # assert self.priority_attribute is None or self.priority_attribute in self.vocabulary.attributes,\
        #    'priority attribute is not among the vocabulary attributes: ' + str(self.priority_attribute)

        # TODO would be better if this was a dict instead of defaultdict for safety and memory
        self._heads = defaultdict(set)
        for phrase in self.ruleset.static_rules:
            self._heads[phrase.pattern[0]].add(phrase.pattern[1:])

    def extend_ruleset(self, ruleset, key):
        self.ruleset = copy.deepcopy(ruleset)

        addable_attributes = []
        for attribute in self.output_attributes:
            if attribute not in self.ruleset.static_rules[0].attributes:
                addable_attributes.append(attribute)
        for rule in self.ruleset.static_rules:
            for attribute in addable_attributes:
                if attribute == key:
                    rule.attributes[attribute] = rule.pattern
                else:
                    rule.attributes[attribute] = None

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     enveloping=self.input_layers[0],
                     ambiguous=not isinstance(self.ruleset, Ruleset))

    def _make_layer(self, text, layers: dict, status=None):
        input_layer = layers[self.input_layers[0]]
        layer = self._make_layer_template()
        layer.text_object = text

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
                            records = [rule.attributes for rule in self.ruleset.static_rules if rule.pattern == phrase]
                            for record in records:
                                annotation = Annotation(span, **{attr: record[attr]
                                                             for attr in output_attributes})
                                annotation = self.decorator(text,span,annotation)
                                if annotation is None:
                                    continue
                                span.add_annotation(annotation)
                            if span.annotations:
                                layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy=self.conflict_resolving_strategy,
                          priority_attribute=self.priority_attribute,
                          keep_equal=True)
        return layer


def default_decorator(text, span, annotation):
    return annotation
