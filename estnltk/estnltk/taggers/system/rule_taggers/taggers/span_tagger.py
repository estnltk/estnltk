import copy
from typing import Sequence, Callable, Dict, Any, Optional, Tuple, List, Union, Iterator, Generator

from estnltk.taggers import Tagger
from estnltk.taggers.system.rule_taggers.extraction_rules.ruleset import Ruleset
from estnltk.taggers.system.rule_taggers.extraction_rules.ambiguous_ruleset import AmbiguousRuleset
from estnltk.taggers.system.rule_taggers.helper_methods.helper_methods import keep_minimal_matches, keep_maximal_matches
from estnltk import Span, Text
from estnltk import Layer
from estnltk import Annotation
from estnltk_core import ElementaryBaseSpan


class SpanTagger(Tagger):
    """Tags spans on a given layer. Creates a layer for which the input layer is the parent layer.

    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 ruleset: AmbiguousRuleset,
                 output_attributes: Sequence[str] = (),
                 decorator: Callable[
                     [Text, ElementaryBaseSpan, Dict[str, Any]], Optional[Dict[str, Any]]] = None,
                 validator_attribute: str = None,
                 priority_attribute: str = None,
                 case_sensitive=True,
                 conflict_resolver: Union[str, Callable[[Layer], Layer]] = 'KEEP_MAXIMAL'
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
        :param output_attributes: Sequence[str]
            Output layer attributes.
        :param decorator: callable
            Global decorator function.
        :param validator_attribute: str
            The name of the attribute that points to the global_validator function in the vocabulary.
        :param priority_attribute
            The name
        :param conflict_resolver: 'KEEP_ALL', 'KEEP_MAXIMAL', 'KEEP_MINIMAL' (default: 'KEEP_MAXIMAL')
            Strategy to choose between overlapping matches.
            Specify your own layer assembler if none of the predefined strategies does not work.
            A custom function must be take in two arguments:
            * layer: a layer to which spans must be added
            * triples: a list of (annotation, group, priority) triples
            and must output the updated layer which hopefully containing some spans.
            These triples can come in canonical order which means:
                span[i].start <= span[i+1].start
                span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end
            where the span is annotation.span
        """
        self.conf_param = ('input_attribute', '_vocabulary', 'global_decorator', 'validator_attribute',
                           'priority_attribute', 'ambiguous', 'case_sensitive', '_ruleset', 'dynamic_ruleset_map',
                           'conflict_resolver')
        self.priority_attribute = priority_attribute
        self.output_layer = output_layer
        self.input_attribute = input_attribute

        self.output_attributes = tuple(output_attributes)

        self.validator_attribute = validator_attribute

        if decorator is None:
            decorator = default_decorator
        self.global_decorator = decorator

        self.conflict_resolver = conflict_resolver

        self.input_layers = [input_layer]

        # Lets index dynamic rulesets in optimal way
        self.dynamic_ruleset_map: Dict[str, Dict[Tuple[int, int], Callable]]

        dynamic_ruleset_map = dict()
        for rule in ruleset.dynamic_rules:
            subindex = dynamic_ruleset_map.get(rule.pattern, dict())
            if (rule.group, rule.priority) in subindex:
                raise AttributeError('There are multiple rules with the same pattern, group and priority')
            subindex[rule.group, rule.priority] = rule.decorator
            dynamic_ruleset_map[rule.pattern] = subindex

        # No errors were detected
        self.dynamic_ruleset_map = dynamic_ruleset_map

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

    def extract_annotations(self, text: str, layers: dict) -> List[Tuple[ElementaryBaseSpan, str]]:
        layer = self._make_layer_template()
        layer.text_object = text

        ruleset = self._ruleset
        input_attribute = self.input_attribute

        case_sensitive = self.case_sensitive
        input_layer = layers[self.input_layers[0]]
        match_tuples = []

        if input_layer.ambiguous:
            for parent_span in input_layer:
                attr_list = getattr(parent_span, input_attribute)  # TODO get rid of getattr
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
                        match_tuples.append((parent_span.base_span, value))
        else:
            for parent_span in input_layer:
                value = getattr(parent_span, input_attribute)  # TODO get rid of getattr
                if not case_sensitive:
                    value = value.lower()
                if value in [rule.pattern for rule in ruleset.static_rules]:
                    match_tuples.append((parent_span.base_span, value))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    def add_redecorated_annotations_to_layer(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]) -> Layer:

        ruleset = self._ruleset

        raw_text = layer.text_object

        for tuple in sorted_tuples:
            value = tuple[1]
            span = Span(base_span=tuple[0], layer=layer)
            for rule in ruleset.static_rules:
                if rule.pattern == value:
                    rec = rule.attributes
                    attributes = {attr: rec[attr] for attr in layer.attributes}
                    annotation = self.global_decorator(raw_text, tuple[0], attributes)
                    annotation = Annotation(span, annotation)

                    subindex = self.dynamic_ruleset_map.get(rule.pattern, None)
                    group = rule.group
                    priority = rule.priority
                    decorator = subindex[(group, priority)] if subindex is not None else None
                    if decorator is None:
                        span.add_annotation(annotation)
                        continue
                    annotation = decorator(layer.text_object, span, annotation)
                    span.add_annotation(annotation)

            if span.annotations:
                layer.add_span(span)

        return layer

    def iterate_over_redecorated_annotations(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]
    ) -> Generator[Tuple[Annotation, int, int], None, None]:
        ruleset = self._ruleset

        raw_text = layer.text_object

        for element in sorted_tuples:
            value = element[1]
            span = Span(base_span=element[0], layer=layer)
            for rule in ruleset.static_rules:
                if rule.pattern == value:
                    rec = rule.attributes
                    attributes = {attr: rec[attr] for attr in layer.attributes}
                    annotation = self.global_decorator(raw_text, element[0], attributes)
                    annotation = Annotation(span, annotation)

                    subindex = self.dynamic_ruleset_map.get(rule.pattern, None)
                    group = rule.group
                    priority = rule.priority
                    decorator = subindex[(group, priority)] if subindex is not None else None
                    if decorator is None:
                        yield annotation, group, priority
                        continue
                    annotation = decorator(layer.text_object, span, annotation)
                    yield annotation, group, priority

    def _make_layer(self, text, layers: dict, status: dict):
        raw_text = text.text
        layer = self._make_layer_template()
        layer.text_object = text

        all_matches = self.extract_annotations(raw_text, layers)

        if self.conflict_resolver == 'KEEP_ALL':
            return self.add_redecorated_annotations_to_layer(layer, iter(all_matches))
        elif self.conflict_resolver == 'KEEP_MAXIMAL':
            return self.add_redecorated_annotations_to_layer(layer, keep_maximal_matches(all_matches))
        elif self.conflict_resolver == 'KEEP_MINIMAL':
            return self.add_redecorated_annotations_to_layer(layer, keep_minimal_matches(all_matches))
        elif callable(self.conflict_resolver):
            return self.conflict_resolver(layer, self.iterate_over_redecorated_annotations(layer, iter(all_matches)))

        raise ValueError("Data field conflict_resolver is inconsistent")



def default_decorator(text, span, annotation):
    return annotation