from typing import Sequence, Union, Generator, Tuple, Iterator, List, Callable, Dict, Any, Optional

from estnltk.taggers import Tagger
from estnltk import Layer, Text
from estnltk.taggers.system.rule_taggers.helper_methods.helper_methods import keep_maximal_matches, keep_minimal_matches
from estnltk_core import Annotation, ElementaryBaseSpan, Span
from estnltk_core.layer_operations import resolve_conflicts
from estnltk.taggers.system.rule_taggers import Ruleset


class RegexTagger(Tagger):
    """Tags regular expression matches on the text.

    Searches matches for regular expressions in the text, solves the possible
    conflicts and creates a new layer of the matches.

    """
    __slots__ = ['conflict_resolver',
                 'overlapped',
                 'priority_attribute',
                 '_illegal_keywords',
                 '_internal_attributes',
                 'ruleset',
                 '_disamb_tagger',
                 'ambiguous',
                 'global_decorator']

    def __init__(self,
                 ruleset: Union[str, dict, list, Ruleset],
                 output_layer: str = 'regexes',
                 output_attributes: Sequence = None,
                 conflict_resolver: str = 'KEEP_MAXIMAL',
                 overlapped: bool = False,
                 priority_attribute: str = None,
                 ambiguous: bool = False,
                 ignore_case: bool = False,
                 decorator: Callable[
                     [Text, ElementaryBaseSpan, Dict[str, Any]], Optional[Dict[str, Any]]] = None
                 ):
        """Initialize a new RegexTagger instance.

        Parameters
        ----------
        ruleset: list of dicts or pandas.DataFrame or csv file name
            regexes and output_attributes to annotate
        output_layer: str (Default: 'regexes')
            The name of the new layer.
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
        ambiguous
            If True, then the output layer is ambiguous
            If False, then the output layer is not ambiguous
        decorator: callable
            Global decorator function.
        """
        self.conf_param = ['conflict_resolver',
                           'overlapped',
                           'priority_attribute',
                           '_illegal_keywords',
                           '_internal_attributes',
                           'ruleset',
                           '_disamb_tagger',
                           'ambiguous',
                           'global_decorator']
        self.input_layers = ()
        self.output_layer = output_layer
        if output_attributes is None:
            self.output_attributes = ()
        else:
            self.output_attributes = tuple(output_attributes)

        self._illegal_keywords = {'start', 'end'}

        if decorator is None:
            decorator = default_decorator
        self.global_decorator = decorator

        # output_attributes needed by tagger
        self._internal_attributes = set(self.output_attributes) | {'_group_', '_priority_'}

        from estnltk.taggers import Disambiguator

        def disamb_decorator(span, raw_text):
            return {name: getattr(span.annotations[0], name) for name in self.output_attributes}

        self._disamb_tagger = Disambiguator(output_layer=self.output_layer,
                                            input_layer=self.output_layer,
                                            output_attributes=self.output_attributes,
                                            decorator=disamb_decorator)

        self.ruleset = ruleset

        if ignore_case:
            for rule in self.ruleset.static_rules:
                for i in range(len(rule.pattern)):
                    rule.pattern[i] = rule.pattern[i].lower()


        self.overlapped = overlapped
        self.conflict_resolver = conflict_resolver
        self.priority_attribute = priority_attribute
        self.ambiguous = ambiguous

    def _make_layer_template(self):
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     ambiguous=True)

    def _make_layer(self, text, layers=None, status=None):
        layer = self._make_layer_template()
        layer.text_object=text
        #for record in self._match(text.text):
        #    layer.add_annotation((record['start'], record['end']), **record)
        #layer = resolve_conflicts(layer=layer,
        #                          conflict_resolving_strategy=self.conflict_resolving_strategy,
         #                         priority_attribute=self.priority_attribute,
        #                          status=status)

        all_matches = self.extract_annotations(text.text)

        if self.conflict_resolver == 'KEEP_ALL':
            layer = self.add_redecorated_annotations_to_layer(layer, iter(all_matches))
        elif self.conflict_resolver == 'KEEP_MAXIMAL':
            layer = self.add_redecorated_annotations_to_layer(layer, keep_maximal_matches(all_matches))
        elif self.conflict_resolver == 'KEEP_MINIMAL':
            layer = self.add_redecorated_annotations_to_layer(layer, keep_minimal_matches(all_matches))
        elif callable(self.conflict_resolver):
            layer = self.conflict_resolver(layer, self.iterate_over_redecorated_annotations(layer, iter(all_matches)))
        else:
            raise ValueError("Data field conflict_resolver is inconsistent")

        if not self.ambiguous:
            layer = self._disamb_tagger.make_layer(text=text, layers={self.output_layer: layer}, status=status)

        return layer

    def _match(self, text):
        for rule in self.ruleset.static_rules:
            reg = rule.pattern
            rec = rule.attributes
            for matchobj in reg.finditer(text, overlapped=self.overlapped):
                start, end = matchobj.span(rec['_group_'])
                if start == end:
                    continue
                if not rec['_validator_'](matchobj):
                    continue
                record = {
                    'start': start,
                    'end': end
                }
                for a in self._internal_attributes:
                    v = rec.get(a, 0)
                    if callable(v):
                        v = v(matchobj)
                    record[a] = v
                yield record

    def extract_annotations(self, text: str) -> List[Tuple[ElementaryBaseSpan, str]]:
        match_tuples = []
        for rule in self.ruleset.static_rules:
            reg = rule.pattern
            rec = rule.attributes
            for matchobj in reg.finditer(text, overlapped=self.overlapped):
                start, end = matchobj.span(rec['_group_'])
                if start == end:
                    continue
                if not rec['_validator_'](matchobj):
                    continue
                match_tuples.append((ElementaryBaseSpan(start=start, end=end), text[start:end]))

        return sorted(match_tuples, key=lambda x: (x[0].start, x[0].end))

    def add_redecorated_annotations_to_layer(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]) -> Layer:

        raw_text = layer.text_object

        for element in sorted_tuples:
            span = Span(base_span=element[0], layer=layer)
            for rule in self.ruleset.static_rules:
                reg = rule.pattern
                for matchobj in reg.finditer(raw_text.text, overlapped=self.overlapped):
                    rec = rule.attributes
                    record = {
                        'start': element[0].start,
                        'end': element[0].end
                    }
                    for a in self._internal_attributes:
                        v = rec.get(a, 0)
                        if callable(v):
                            v = v(matchobj)
                        record[a] = v

                    annotation = self.global_decorator(raw_text, element[0], record)
                    span.add_annotation(annotation)
            layer.add_span(span)

        return layer


    def iterate_over_redecorated_annotations(
            self,
            layer: Layer,
            sorted_tuples: Iterator[Tuple[ElementaryBaseSpan, str]]
    ) -> Generator[Tuple[Annotation, int, int], None, None]:

        pass


def default_decorator(text, span, annotation):
    return annotation