from copy import copy
from ahocorasick import Automaton

from estnltk import Text, Layer, Tagger
from estnltk import ElementaryBaseSpan, Span, Annotation
from typing import Tuple, List, Dict, Sequence, Union, Any, Callable, Iterator, Generator, Optional

from estnltk.taggers.system.rule_taggers import Ruleset
from estnltk.taggers.system.rule_taggers.extraction_rules.ambiguous_ruleset import AmbiguousRuleset
from estnltk.taggers.system.rule_taggers.helper_methods.helper_methods import keep_maximal_matches, keep_minimal_matches


class SubstringTagger(Tagger):
    """
    Tags occurrences of substrings on the text, solves possible conflicts and creates a new layer of the matches.
    Uses Aho-Corasick algorithm to efficiently match many substrings simultaneously.

    Static extraction rules are in the form string --> dict where the dict contains the annotation for the match, e.g.
        Washington    --> {type: capital, country: US},
        Tartu         --> {type: town, country: Estonia}
        St. Mary Mead --> {type: village, country: UK}

    Dynamic extraction rules are in the form string --> function where the function recomputes annotations.
    The function takes in the match as Span and must output a dictionary specifying a new annotation or None.
    The output None signals that extracted match is not valid and should be dropped.

    For convenience each extraction rule can be split into static and dynamic parts where the static rule determines
    non-variable annotations and dynamic rule is used to re-compute values of context sensitive attributes.
    The dynamic part itself can be split into, two as well.
    First a global decorator that is applied for all matches and then pattern specific decorators.
    Decorators can return None to filter out unsuitable matches.

    Annotations are added to extracted matches based on the right-hand-side of the matching rules:
    * First statical rules are applied to specify fixed attributes. No spans are dropped!
    * Next the global decorator is applied to update the annotation.
    * A span is dropped when the resulting annotation is not a dictionary of attribute values.
    * Finally decorators from dynamical rules are applied to update the annotation.
    * A span is dropped when the resulting annotation is not a dictionary of attribute values.

    Each rule may additionally have priority and group attributes.
    These can used in custom conflict resolver to choose between overlapping spans.

    Rules can be specified during the initialisation and cannot be changed afterwards.
    Use the class AmbiguousRuleset or Ruleset to load static rules from csv files before initialising the tagger.

    """

    # noinspection PyMissingConstructor,PyUnresolvedReferences
    def __init__(self,
                 ruleset: AmbiguousRuleset,
                 token_separators: str = '',
                 output_layer: str = 'terms',
                 ambiguous_output_layer: bool = True,
                 output_attributes: Sequence = None,
                 global_decorator: Callable[
                     [Text, ElementaryBaseSpan, Dict[str, Any]], Optional[Dict[str, Any]]] = None,
                 conflict_resolver: Union[str, Callable[[Layer], Layer]] = 'KEEP_MAXIMAL',
                 ignore_case: bool = False
                 ):
        """
        Initialize a new SubstringTagger instance.

        Parameters
        ----------
        ruleset:
            Can be of type AmbiguousRuleset or Ruleset depending on if there are multiple rules
            with the same left-hand side.
            A list of substrings together with their annotations.
            Can be imported before creation of a tagger from CSV file with load method of the Ruleset.
        token_separators:
            A list of characters that determine the end of token.
            If token separators are unspecified then all substring matches are considered.
            Otherwise, a match is ignored if it ends or starts inside of a token.
            To mach a multi-token string the extraction pattern must contain correct separator.
        output_layer:
            The name of the new layer (default: 'terms').
        ambiguous_output_layer: bool (default: True)
            Determines if the output layer will be ambiguous or not.
            Error will be thrown if False is chosen but there are two rules with the same pattern in the ruleset.
            If ignore_case=True, patterns that are identical when ignoring case are also considered the same
        global_decorator:
            A global decorator that is applied for all matches and can update attribute values or invalidate match.
            It must take in three arguments:
            * text: a text object that is processed
            * span: a span for which the attributes are recomputed.
            * annotation: annotation for which the attributes are recomputed
            The function should return a dictionary of updated attribute values or None to invalidate the match.
        conflict_resolver: 'KEEP_ALL', 'KEEP_MAXIMAL', 'KEEP_MINIMAL' (default: 'KEEP_MAXIMAL')
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
        ignore_case:
            If True, then matches do not depend on capitalisation of letters
            If False, then capitalisation of letters is important

        Extraction rules are in the form string --> dict where the dict contains the annotation for the match, e.g.
            Washington    --> {type: capital, country: US},
            Tartu         --> {type: town, country: Estonia}
            St. Mary Mead --> {type: village, country: UK}
        Each rule may additionally have priority and group attributes.
        These can used in custom conflict resolver to choose between overlapping spans.

        Token separators define token boundaries. If they are set then the pattern must match the entire token, e.g.
        separators = '|' implies that the second match in '|Washington| Tartu |St. Mary Mead' is dropped.
        The last match is valid as the separator does not have to be at the end of the entire text.

        Extraction rules work for multi-token strings, however, the separators between tokens are fixed by the pattern.
        For multiple separator symbols, all pattern variants must be explicitly listed.

        """

        self.conf_param = [
            'ruleset',
            'token_separators',
            'conflict_resolver',
            'global_decorator',
            'ignore_case',
            'dynamic_ruleset_map',
            'static_ruleset_map',
            'ambiguous_output_layer']

        self.input_layers = ()
        self.output_layer = output_layer
        self.output_attributes = output_attributes or ()

        # Validate ruleset. It must exist
        if not isinstance(ruleset, AmbiguousRuleset):
            raise ValueError('Argument ruleset must be of type Ruleset or AmbiguousRuleset')
        if not (set(ruleset.output_attributes) <= set(self.output_attributes)):
            raise ValueError('Output attributes of a ruleset must match the output attributes of a tagger')

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

        # No errors were detected
        self.dynamic_ruleset_map = dynamic_ruleset_map

        self.ruleset = copy(ruleset)
        self.token_separators = token_separators
        self.global_decorator = global_decorator
        self.conflict_resolver = conflict_resolver
        self.ambiguous_output_layer = ambiguous_output_layer

        # We bypass restrictions of Tagger class to set some private attributes
        super(Tagger, self).__setattr__('_automaton', Automaton())

        # Configures automaton to match the patters in the ruleset
        # Each pattern is here exactly once
        if self.ignore_case:
            for rule in ruleset.static_rules:
                pattern = rule.pattern
                self._automaton.add_word(pattern.lower(), len(pattern))
        else:
            for rule in ruleset.static_rules:
                pattern = rule.pattern
                self._automaton.add_word(pattern, len(pattern))

        self._automaton.make_automaton()

    def _make_layer(self, text: Text, layers=None, status=None):

        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            text_object=text,
            ambiguous=self.ambiguous_output_layer
        )

        raw_text = text.text.lower() if self.ignore_case else text.text
        all_matches = self.extract_matches(raw_text, self.token_separators)

        if self.conflict_resolver == 'KEEP_ALL':
            return self.add_decorated_annotations_to_layer(layer, iter(all_matches))
        elif self.conflict_resolver == 'KEEP_MAXIMAL':
            return self.add_decorated_annotations_to_layer(layer, keep_maximal_matches(all_matches))
        elif self.conflict_resolver == 'KEEP_MINIMAL':
            return self.add_decorated_annotations_to_layer(layer, keep_minimal_matches(all_matches))
        elif callable(self.conflict_resolver):
            return self.conflict_resolver(layer, self.iterate_over_decorated_annotations(layer, iter(all_matches)))

        raise ValueError("Data field conflict_resolver is inconsistent")

    # noinspection PyUnresolvedReferences
    def extract_matches(self, text: str, separators: str) -> List[Tuple[ElementaryBaseSpan, str]]:
        """
        Returns a list of matches of the defined by the list of extraction rules that are canonically ordered:
            span[i].start <= span[i+1].start
            span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end

        All matches are returned when no separator characters are specified.
        Given a list of separator symbols returns matches that do not contain of incomplete tokens.
        That is, the symbol before the match and the symbol after the match is a separator symbol.

        In both cases, matches can overlap and do not have to be maximal -- a span may be enclosed by another span.
        """

        match_tuples = []
        if len(separators) == 0:
            for loc, value in self._automaton.iter(text):
                match_tuples.append(
                    (ElementaryBaseSpan(start=loc - value + 1, end=loc + 1), text[loc - value + 1: loc + 1]))
        else:
            n = len(text)
            for loc, value in self._automaton.iter(text):
                end = loc + 1
                start = loc - value + 1

                # Check that a preceding symbol is a separator
                if start > 0 and text[start - 1] not in separators:
                    continue

                # Check that a succeeding symbol is a separator
                if end < n and text[end] not in separators:
                    continue

                match_tuples.append((ElementaryBaseSpan(start=start, end=end), text[start:end]))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    # noinspection PyUnresolvedReferences
    def add_decorated_annotations_to_layer(
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

        text_object = layer.text_object
        base_span, pattern = next(sorted_tuples, (None, None))
        while base_span is not None:
            span = Span(base_span=base_span, layer=layer)
            static_rulelist = self.static_ruleset_map.get(pattern, None)
            for group, priority, annotation in static_rulelist:
                # apply global decorator
                # Drop annotations for which the global decorator fails
                if self.global_decorator is not None:
                    annotation = self.global_decorator(text_object, base_span, annotation)
                    if not isinstance(annotation, dict):
                        continue

                # apply dynamic_decorator --- it must be unique or have matching priority and group
                # No dynamic rules to change the annotation
                subindex = self.dynamic_ruleset_map.get(pattern, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                if decorator is None:
                    layer.add_annotation(base_span,annotation)
                    continue
                annotation = decorator(text_object, span, annotation)
                if annotation is not None:
                    layer.add_annotation(base_span,annotation)

            base_span, pattern = next(sorted_tuples, (None, None))

        return layer

    # noinspection PyUnresolvedReferences
    def iterate_over_decorated_annotations(
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

        text_object = layer.text_object
        base_span, pattern = next(sorted_tuples, (None, None))
        # This hack is needed as EstNLTK wants complete attribute assignment for each annotation
        while base_span is not None:
            span = Span(base_span=base_span, layer=layer)
            # This hack is needed as EstNLTK wants complete attribute assignment for each annotation
            static_rulelist = self.static_ruleset_map.get(pattern, None)
            for group, priority, annotation_dict in static_rulelist:
                # apply global decorator
                # Drop annotations for which the global decorator fails
                if self.global_decorator is not None:
                    annotation_dict = self.global_decorator(text_object, base_span, annotation_dict)
                    if not isinstance(annotation_dict, dict):
                        continue

                # apply dynamic_decorator
                subindex = self.dynamic_ruleset_map.get(pattern, None)
                decorator = subindex[(group, priority)] if subindex is not None else None
                # No dynamic rules to change the annotation
                if decorator is not None:
                    annotation_dict = decorator(text_object, base_span, annotation_dict)
                if isinstance(annotation_dict, dict):
                    annotation = Annotation(span, annotation_dict)
                    yield annotation, group, priority

            base_span, pattern = next(sorted_tuples, (None, None))
