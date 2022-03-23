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

    Takes as input a layer ('input_layer'), an attribute ('input_attribute')
    and a ruleset ('ruleset'). The pattern of each rule in the ruleset is the
    value of the input attribute so for example if the attribute : for example if
    the attribute is 'lemma' then the pattern should be a lemma. These lemmas are
    then searched for in the input layer and if the lemma is found
    in the layer, an annotation is created based on the rule. A global
    decorator ('decorator') can be used to validate the annotations.
    Overlapping spans are resolved based on the choice of 'conflict_resolver'.

    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 ruleset: AmbiguousRuleset,
                 output_attributes: Sequence[str] = (),
                 decorator: Callable[
                     [Text, ElementaryBaseSpan, Dict[str, Any]], Optional[Dict[str, Any]]] = None,
                 ignore_case=False,
                 conflict_resolver: Union[str, Callable[[Layer], Layer]] = 'KEEP_MAXIMAL'
                 ):
        """Initialize a new SpanTagger instance.

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
        :param ignore_case
            If True, then matches do not depend on capitalisation of letters
            If False, then capitalisation of letters is important
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
        self.conf_param = ('input_attribute', '_vocabulary', 'global_decorator',
                           'ambiguous', 'ignore_case', '_ruleset', 'dynamic_ruleset_map',
                           'conflict_resolver', 'static_ruleset_map')
        self.output_layer = output_layer
        self.input_attribute = input_attribute

        self.output_attributes = tuple(output_attributes)

        self.global_decorator = decorator

        self.conflict_resolver = conflict_resolver

        self.input_layers = [input_layer]

        self.static_ruleset_map: Dict[str, List[Tuple[int, int, Dict[str, any]]]]

        static_ruleset_map = dict()

        self.ignore_case = ignore_case

        for rule in ruleset.static_rules:
            if self.ignore_case:
                subindex = static_ruleset_map.get(rule.pattern.lower(), [])
                subindex.append((rule.group, rule.priority, rule.attributes))
                static_ruleset_map[rule.pattern.lower()] = subindex
            else:
                subindex = static_ruleset_map.get(rule.pattern, [])
                subindex.append((rule.group, rule.priority, rule.attributes))
                static_ruleset_map[rule.pattern] = subindex

        self.static_ruleset_map = static_ruleset_map

        # Lets index dynamic rulesets in optimal way
        self.dynamic_ruleset_map: Dict[str, Dict[Tuple[int, int], Callable]]

        dynamic_ruleset_map = dict()
        for rule in ruleset.dynamic_rules:
            subindex = dynamic_ruleset_map.get(rule.pattern, dict())
            if (rule.group, rule.priority) in subindex:
                raise AttributeError('There are multiple rules with the same pattern, group and priority')
            subindex[rule.group, rule.priority] = rule.decorator
            dynamic_ruleset_map[rule.pattern] = subindex
            # create corresponding static rule if it does not exist yet
            if static_ruleset_map.get(rule.pattern.lower(), None) is None:
                self.static_ruleset_map[rule.pattern.lower()] = [(rule.group, rule.priority, dict())]
            elif len([item for item in static_ruleset_map.get(rule.pattern.lower())
                      if item[0] == rule.group and item[1] == rule.priority]) == 0:
                self.static_ruleset_map[rule.pattern.lower()] = [(rule.group, rule.priority, dict())]

        # No errors were detected
        self.dynamic_ruleset_map = dynamic_ruleset_map

        self._ruleset = copy.copy(ruleset)

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     parent=self.input_layers[0],
                     ambiguous=not isinstance(self._ruleset, Ruleset))

    def extract_annotations(self, text: str, layers: dict) -> List[Tuple[ElementaryBaseSpan, str]]:
        """
        Returns a list of matches of the defined by the list of extraction rules that are canonically ordered:
            span[i].start <= span[i+1].start
            span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end

        Matches can overlap and do not have to be maximal -- a span may be enclosed by another span.
        """
        layer = self._make_layer_template()
        layer.text_object = text

        input_attribute = self.input_attribute

        input_layer = layers[self.input_layers[0]]
        match_tuples = []

        for parent_span in input_layer:
            for annotation in parent_span.annotations:
                value = getattr(annotation,input_attribute)
                if self.ignore_case:
                    value = value.lower()
                if value in self.static_ruleset_map.keys():
                    match_tuples.append((parent_span.base_span, value))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    def add_redecorated_annotations_to_layer(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]) -> Layer:
        """
        Adds annotations to extracted matches and assembles them into a layer.
        Annotations are added to extracted matches based on the right-hand-side of the matching extraction rule:
        * First statical rules are applied to specify fixed attributes. No spans are dropped!
        * Next the global decorator is applied to update the annotation.
        * A span is dropped when the resulting annotation is not a dictionary of attribute values.
        * Finally decorators from dynamical rules are applied to update the annotation.
        * A span is dropped when the resulting annotation is not a dictionary of attribute values.
        """

        raw_text = layer.text_object

        for tuple in sorted_tuples:
            pattern = tuple[1]
            span = Span(base_span=tuple[0], layer=layer)
            static_rulelist = self.static_ruleset_map.get(pattern, None)
            for group, priority, annotation in static_rulelist:
                rec = annotation
                attributes = {attr: rec[attr] for attr in layer.attributes}
                if self.global_decorator is not None:
                    annotation = self.global_decorator(raw_text, tuple[0], attributes)

                subindex = self.dynamic_ruleset_map.get(pattern, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                if decorator is None:
                    annotation = Annotation(span, annotation)
                    span.add_annotation(annotation)
                    continue
                annotation = decorator(layer.text_object, span, annotation)
                annotation = Annotation(span, annotation)
                span.add_annotation(annotation)

            if span.annotations:
                layer.add_span(span)

        return layer

    def iterate_over_redecorated_annotations(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]
    ) -> Generator[Tuple[Annotation, int, int], None, None]:
        """
        Returns a triple (annotation, group, priority) for each match that passes validation test.

        Group and priority information is lifted form the matching extraction rules.
        By construction a dynamic and static rule must have the same group and priority attributes.

        Annotations are added to extracted matches based on the right-hand-side of the matching extraction rule:
        * First statical rules are applied to specify fixed attributes. No spans are dropped!
        * Next the global decorator is applied to update the annotation.
        * A span is dropped when the resulting annotation is not a dictionary of attribute values.
        * Finally decorators from dynamical rules are applied to update the annotation.
        * A span is dropped when the resulting annotation is not a dictionary of attribute values.
        """

        raw_text = layer.text_object

        for element in sorted_tuples:
            pattern = element[1]
            span = Span(base_span=element[0], layer=layer)
            static_rulelist = self.static_ruleset_map.get(pattern, None)
            for group, priority, annotation in static_rulelist:
                rec = annotation
                attributes = {attr: rec[attr] for attr in layer.attributes}
                annotation = self.global_decorator(raw_text, element[0], attributes)

                subindex = self.dynamic_ruleset_map.get(pattern, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                if decorator is None:
                    annotation = Annotation(span, annotation)
                    yield annotation, group, priority
                    continue
                annotation = decorator(layer.text_object, span, annotation)
                annotation = Annotation(span, annotation)
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
