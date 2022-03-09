import copy
from collections import defaultdict
from typing import Sequence, List, Tuple, Iterator, Generator, Dict, Callable, Any

from estnltk import Annotation, EnvelopingBaseSpan
from estnltk import EnvelopingSpan
from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk.taggers.system.rule_taggers.extraction_rules.ambiguous_ruleset import AmbiguousRuleset
from estnltk.taggers.system.rule_taggers.extraction_rules.ruleset import Ruleset
from estnltk.taggers.system.rule_taggers.helper_methods.helper_methods import keep_maximal_matches, keep_minimal_matches
from estnltk_core import ElementaryBaseSpan


class PhraseTagger(Tagger):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """

    def __init__(self,
                 output_layer: str,
                 input_layer: str,
                 input_attribute: str,
                 ruleset: AmbiguousRuleset,
                 conflict_resolver: str = 'KEEP_MAXIMAL',
                 output_attributes: Sequence = None,
                 key: str = '_phrase_',
                 decorator=None,
                 priority_attribute: str = None,
                 ignore_case=False
                 ):
        """Initialize a new PhraseTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param input_layer: str
            The name of the input layer.
        :param input_attribute: str
            The name of the input layer attribute.
        :param ruleset: AmbiguousRuleset
            Ruleset of type Ruleset or AmbiguousRuleset
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
        :param key: str
            The name of the ruleset index
        :param decorator: Callable
            Decorator function for spans
        :param output_attributes
            Names of the output layer attributes.
        :param priority_attribute: str
            Name of the attribute that is used to resolve conflicts.
        :param ignore_case: bool
            If True, matches will be searched for using lowercased rule patterns
        """
        self.conf_param = ('input_attribute', 'ruleset', 'decorator',
                           'priority_attribute', '_heads',
                           'ignore_case', 'conflict_resolver',
                           'static_ruleset_map', 'dynamic_ruleset_map')

        self.output_layer = output_layer
        self.input_layers = [input_layer]
        self.input_attribute = input_attribute

        output_attributes = output_attributes or []
        if priority_attribute is not None and priority_attribute not in output_attributes:
            output_attributes.append(priority_attribute)
        self.output_attributes = tuple(output_attributes)
        self.decorator = decorator

        self.conflict_resolver = conflict_resolver
        self.priority_attribute = priority_attribute

        # Validate ruleset. It must exist
        if not isinstance(ruleset, AmbiguousRuleset):
            raise ValueError('Argument ruleset must be of type Ruleset or AmbiguousRuleset')
        if not (set(ruleset.output_attributes) <= set(self.output_attributes)):
            raise ValueError('Output attributes of a ruleset must match the output attributes of a tagger')

        self.extend_ruleset(ruleset, key)

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
            if self.ignore_case:
                subindex = dynamic_ruleset_map.get(rule.pattern.lower(), dict())
                if (rule.group, rule.priority) in subindex:
                    raise AttributeError('There are multiple rules with the same pattern, group and priority')
                subindex[rule.group, rule.priority] = rule.decorator
                dynamic_ruleset_map[rule.pattern.lower()] = subindex
                # create corresponding static rule if it does not exist yet
                if static_ruleset_map.get(rule.pattern.lower(), None) is None:
                    self.static_ruleset_map[rule.pattern.lower()] = [(rule.group, rule.priority, dict())]
                elif len([item for item in static_ruleset_map.get(rule.pattern.lower())
                          if item[0] == rule.group and item[1] == rule.priority]) == 0:
                    self.static_ruleset_map[rule.pattern.lower()] = [(rule.group, rule.priority, dict())]
            else:
                subindex = dynamic_ruleset_map.get(rule.pattern, dict())
                if (rule.group, rule.priority) in subindex:
                    raise AttributeError('There are multiple rules with the same pattern, group and priority')
                subindex[rule.group, rule.priority] = rule.decorator
                dynamic_ruleset_map[rule.pattern] = subindex
                # create corresponding static rule if it does not exist yet
                if static_ruleset_map.get(rule.pattern, None) is None:
                    static_ruleset_map[rule.pattern] = [(rule.group, rule.priority, dict())]
                elif len([item for item in static_ruleset_map.get(rule.pattern)
                          if item[0] == rule.group and item[1] == rule.priority]) == 0:
                    static_ruleset_map[rule.pattern.lower()] = [(rule.group, rule.priority, dict())]

        self.dynamic_ruleset_map = dynamic_ruleset_map

        self.ignore_case = ignore_case

        if ignore_case:
            for rule in self.ruleset.static_rules:
                for i in range(len(rule.pattern)):
                    rule.pattern[i] = rule.pattern[i].lower()

        self._heads = {}
        for phrase in self.ruleset.static_rules:
            current_phrase = self._heads.get(phrase.pattern[0], set())
            current_phrase.add(phrase.pattern[1:])
            self._heads[phrase.pattern[0]] = current_phrase

    def extend_ruleset(self, ruleset, key):
        self.ruleset = copy.copy(ruleset)

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
        layer = self._make_layer_template()
        layer.text_object = text
        raw_text = text.text
        all_matches = self.extract_annotations(raw_text,layers)

        if self.conflict_resolver == 'KEEP_ALL':
            layer = self.add_decorated_annotations_to_layer(layer, iter(all_matches))
        elif self.conflict_resolver == 'KEEP_MAXIMAL':
            layer = self.add_decorated_annotations_to_layer(layer, keep_maximal_matches(all_matches))
        elif self.conflict_resolver == 'KEEP_MINIMAL':
            layer = self.add_decorated_annotations_to_layer(layer, keep_minimal_matches(all_matches))
        elif callable(self.conflict_resolver):
            layer = self.conflict_resolver(layer, self.iterate_over_decorated_annotations(layer, iter(all_matches)))
        else:
            raise ValueError("Data field conflict_resolver is inconsistent")

        return layer

    def extract_annotations(self, text: str, layers: dict) -> List[Tuple[EnvelopingBaseSpan, str, Any]]:
        match_tuples = []
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
                            base_span = EnvelopingBaseSpan(s.base_span
                                                           for s in input_layer[i:i + len(tail) + 1])
                            phrase = (value, *tail)
                            match_tuples.append((base_span, text[base_span.start:base_span.end], phrase))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    def add_decorated_annotations_to_layer(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]) -> Layer:

        text = layer.text_object

        for base_span, _, phrase in sorted_tuples:
            span = EnvelopingSpan(base_span=base_span, layer=layer)
            static_rulelist = self.static_ruleset_map.get(phrase, None)
            for group, priority, annotation in static_rulelist:
                if self.decorator is not None:
                    annotation = self.decorator(text, base_span, annotation)
                    if not isinstance(annotation, dict):
                        continue
                subindex = self.dynamic_ruleset_map.get(phrase, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                if decorator is None:
                    layer.add_annotation(base_span, annotation)
                    continue
                annotation = decorator(text, span, annotation)
                if annotation is not None:
                    layer.add_annotation(base_span, annotation)

        return layer

    def iterate_over_decorated_annotations(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]
    ) -> Generator[Tuple[Annotation, int, int], None, None]:
        text = layer.text_object

        for base_span, _, phrase in sorted_tuples:
            span = EnvelopingSpan(base_span=base_span, layer=layer)
            static_rulelist = self.static_ruleset_map.get(phrase, None)
            for group, priority, annotation in static_rulelist:
                if self.decorator is not None:
                    annotation = self.decorator(text, base_span, annotation)
                    if not isinstance(annotation, dict):
                        continue
                subindex = self.dynamic_ruleset_map.get(phrase, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                if decorator is None:
                    yield annotation, group, priority
                    continue
                annotation = decorator(text, span, annotation)
                if annotation is not None:
                    yield annotation, group, priority
