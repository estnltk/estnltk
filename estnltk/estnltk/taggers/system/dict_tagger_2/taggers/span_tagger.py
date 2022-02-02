import copy
from typing import Sequence, Union

from estnltk.taggers import Tagger
from estnltk.taggers.system.dict_tagger_2 import Ruleset, AmbiguousRuleset
from estnltk import Span
from estnltk import Layer
from estnltk import Annotation
from estnltk_core.layer_operations import resolve_conflicts


class SpanTagger(Tagger):
    """Tags spans on a given layer. Creates a layer for which the input layer is the parent layer.

    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 ruleset: AmbiguousRuleset,
                 output_attributes: Sequence[str] = (),
                 decorator: callable = None,
                 validator_attribute: str = None,
                 priority_attribute: str = None,
                 case_sensitive=True
                 ):
        """Initialize a new TokenListTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param ruleset: dict, str
            A dict that maps attribute values of the input layer to a list of records of the output layer attribute
            values.
            If str, the vocabulary is read from the file 'vocabulary'
        :param output_attributes: Sequence[str]
            Output layer attributes.
        :param decorator: callable
            Global decorator function.
        :param validator_attribute: str
            The name of the attribute that points to the global_validator function in the vocabulary.
        :param priority_attribute
            The name
        """
        self.conf_param = ('input_attribute', '_vocabulary', 'global_decorator', 'validator_attribute',
                           'priority_attribute', 'ambiguous', 'case_sensitive', '_ruleset')
        self.priority_attribute = priority_attribute
        self.output_layer = output_layer
        self.input_attribute = input_attribute

        self.output_attributes = tuple(output_attributes)

        self.validator_attribute = validator_attribute

        if decorator is None:
            decorator = default_decorator
        self.global_decorator = decorator

        self.input_layers = [input_layer]

        self._ruleset = copy.deepcopy(ruleset)
        self.case_sensitive = case_sensitive
        if not self.case_sensitive:
            for rule in self._ruleset.static_rules:
                for i in range(len(rule.pattern)):
                    rule.pattern[i] = rule.pattern[i].lower()

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     parent=self.input_layers[0],
                     ambiguous=not isinstance(self._ruleset, Ruleset))

    def _make_layer(self, text, layers: dict, status: dict):
        raw_text = text.text
        input_layer = layers[self.input_layers[0]]
        layer = self._make_layer_template()
        layer.text_object = text

        ruleset = self._ruleset
        input_attribute = self.input_attribute
        validator_key = self.validator_attribute

        case_sensitive = self.case_sensitive
        if input_layer.ambiguous:
            for parent_span in input_layer:
                attr_list = getattr(parent_span, input_attribute)
                if isinstance(attr_list, str):
                    # If we ask for 'text', then we get str instead of
                    # AttributeList, so we have to package it into list
                    attr_list = [attr_list]
                if case_sensitive:
                    values = set(attr_list)
                else:
                    values = {v.lower() for v in attr_list}
                for value in values:
                    if value in [rule.pattern for rule in ruleset.static_rules]:
                        span = Span(base_span=parent_span.base_span, layer=layer) #TODO check that it's fine with non-ambiguous
                        for rec in [rule.attributes for rule in ruleset.static_rules if rule.pattern==value]:
                            attributes = {attr: rec[attr] for attr in layer.attributes}
                            annotation = Annotation(span, **attributes)
                            annotation = self.global_decorator(raw_text, span, annotation)
                            if validator_key is None or rec[validator_key](raw_text, annotation):
                                span.add_annotation(annotation)

                        if span.annotations:
                            layer.add_span(span)
        else:
            for parent_span in input_layer:
                value = getattr(parent_span, input_attribute)
                if not case_sensitive:
                    value = value.lower()
                if value in [rule.pattern for rule in ruleset.static_rules]:
                    span = Span(base_span=parent_span.base_span, layer=layer)
                    for rec in [rule.pattern for rule in ruleset.static_rules]:
                        attributes = {attr: rec[attr] for attr in layer.attributes}
                        annotation = Annotation(span, **attributes)
                        if self.global_decorator(raw_text, annotation):
                            if validator_key is None or rec[validator_key](raw_text, annotation):
                                span.add_annotation(Annotation(span, **attributes))

                    if span.annotations:
                        layer.add_span(span)

        resolve_conflicts(layer,
                          conflict_resolving_strategy='ALL',
                          priority_attribute=self.priority_attribute)
        return layer


def default_decorator(text, span, annotation):
    return annotation
