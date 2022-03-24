import copy
from typing import Sequence, Union, Generator, Tuple, Iterator, List, Callable, Dict, Any, Optional

from estnltk.taggers import Tagger
from estnltk import Layer, Text
from estnltk.taggers.system.rule_taggers.helper_methods.helper_methods import keep_maximal_matches, keep_minimal_matches
from estnltk_core import Annotation, ElementaryBaseSpan, Span
from estnltk.taggers.system.rule_taggers import Ruleset, StaticExtractionRule
from typing.re import Match


class RegexTagger(Tagger):
    """Tags regular expression matches on the text.

    Searches matches for regular expressions in the text, resolves the possible
    conflicts based on 'conflict_resolver' and creates a new layer of the matches.
    The new created layer will be ambiguous. Disambiguator tagger can be used to
    make it a non-ambiguous layer.

    The regular expressions to look for are given as patterns in the ruleset and
    the annotation is built based on the same rule. To validate the annotation,
    a global decorator can be used. The match object is an attribute of the
    annotation so the decorator can use it to modify the annotation.

    """
    __slots__ = ['conflict_resolver',
                 'overlapped',
                 '_internal_attributes',
                 'ruleset',
                 '_disamb_tagger',
                 'global_decorator',
                 'match_attribute',
                 'static_ruleset_map',
                 'dynamic_ruleset_map',
                 'lowercase_text']

    def __init__(self,
                 ruleset: Union[str, dict, list, Ruleset],
                 output_layer: str = 'regexes',
                 output_attributes: Sequence = None,
                 conflict_resolver: str = 'KEEP_MAXIMAL',
                 overlapped: bool = False,
                 lowercase_text: bool = False,
                 decorator: Callable[
                     [Text, ElementaryBaseSpan, Dict[str, Any]], Optional[Dict[str, Any]]] = None,
                 match_attribute: str = 'match'
                 ):
        """Initialize a new RegexTagger instance. Note that previously it was possible to
        have callables as attributes in the ruleset. This functionality is now replaced by
        dynamic rules. The new created layer will be ambiguous. Disambiguator tagger can be
        used downstream to make it a non-ambiguous layer.

        Parameters
        ----------
        ruleset: list of dicts or pandas.DataFrame or csv file name
            regexes and output_attributes to annotate
        output_layer: str (Default: 'regexes')
            The name of the new layer.
        output_attributes: Sequence[str]
            New layer attributes.
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
        overlapped: bool (Default: False)
            If True, the match of a regular expression may overlap with a match
            of the same regular expression.
            Note that this default setting will be overwritten by a pattern-
            specific setting if a pattern defines attribute 'overlapped';
        lowercase_text: bool (Default: False)
            If True, the regex patterns are matched to the lowercase version of the input text
        decorator: callable
            Global decorator function.
        match_attribute: str (Default: 'match')
            Name of the attribute in which the match object of the annotation is stored.
            The attribute can be used by the decorator or dynamic rules to change the annotation.
        """
        self.conf_param = ['conflict_resolver',
                           'overlapped',
                           '_internal_attributes',
                           'ruleset',
                           '_disamb_tagger',
                           'global_decorator',
                           'match_attribute',
                           'static_ruleset_map',
                           'dynamic_ruleset_map',
                           'lowercase_text']
        self.input_layers = ()
        self.output_layer = output_layer
        if output_attributes is None:
            self.output_attributes = ()
        else:
            self.output_attributes = tuple(output_attributes)

        self.global_decorator = decorator

        self.static_ruleset_map: Dict[str, List[Tuple[int, int, Dict[str, any]]]]

        static_ruleset_map = dict()

        for rule in ruleset.static_rules:
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

        self.match_attribute = match_attribute
        if not isinstance(match_attribute, str):
            raise AttributeError("Match attribute must be str")

        self.ruleset = copy.copy(ruleset)

        self.lowercase_text = lowercase_text

        self.overlapped = overlapped
        self.conflict_resolver = conflict_resolver

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     ambiguous=True)

    def _make_layer(self, text, layers=None, status=None):
        layer = self._make_layer_template()
        layer.text_object = text

        if self.lowercase_text:
            raw_text = text.text.lower()
        else:
            raw_text = text.text

        all_matches = self.extract_annotations(raw_text)

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

    def extract_annotations(self, text: str) -> List[Tuple[ElementaryBaseSpan, Match, StaticExtractionRule]]:
        """
        Returns a list of matches of the defined by the list of extraction rules that are canonically ordered:
            span[i].start <= span[i+1].start
            span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end

        Matches can overlap and do not have to be maximal -- a span may be enclosed by another span.

        The matches are given as a tuple of base span, match object and the rule based on which the match was found.
        """
        match_tuples = []
        for rule in self.ruleset.static_rules:
            reg = rule.pattern
            for matchobj in reg.finditer(text, overlapped=self.overlapped):
                start, end = matchobj.span(rule.group)
                if start == end:
                    continue
                match_tuples.append((ElementaryBaseSpan(start=start, end=end), matchobj, rule))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    def add_decorated_annotations_to_layer(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, Match, StaticExtractionRule]]) -> Layer:
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

        for element in sorted_tuples:
            span = Span(base_span=element[0], layer=layer)
            rule = element[2]
            matchobj = element[1]
            annotation_dict = rule.attributes
            annotation_dict[self.match_attribute] = matchobj

            if self.global_decorator is not None:
                annotation_dict = self.global_decorator(raw_text, element[0], annotation_dict)
            if rule.pattern in self.dynamic_ruleset_map:
                dynamic_decorator = self.dynamic_ruleset_map[rule.pattern].get((rule.group, rule.priority), None)
                if dynamic_decorator is not None:
                    annotation_dict = dynamic_decorator(layer.text_object, span, annotation_dict)
            if annotation_dict is not None:
                layer.add_annotation(element[0], annotation_dict)

        return layer

    def iterate_over_decorated_annotations(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str, StaticExtractionRule]]
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
            span = Span(base_span=element[0], layer=layer)
            rule = element[2]
            matchobj = element[1]
            annotation_dict = rule.attributes
            annotation_dict[self.match_attribute] = matchobj

            if self.global_decorator is not None:
                annotation_dict = self.global_decorator(raw_text, element[0], annotation_dict)
            if rule.pattern in self.dynamic_ruleset_map:
                dynamic_decorator = self.dynamic_ruleset_map[rule.pattern].get((rule.group, rule.priority), None)
                if dynamic_decorator is not None:
                    annotation_dict = dynamic_decorator(layer.text_object, span, annotation_dict)
            if annotation_dict is not None:
                yield annotation_dict, rule.group, rule.priority