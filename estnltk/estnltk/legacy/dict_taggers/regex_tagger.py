from typing import Sequence, Union

from estnltk.taggers import Tagger
from estnltk import Layer
from estnltk_core.layer_operations import resolve_conflicts
from estnltk.legacy.dict_taggers.vocabulary import Vocabulary


class RegexTagger(Tagger):
    """Tags regular expression matches on the text.

    Searches matches for regular expressions in the text, solves the possible
    conflicts and creates a new layer of the matches.

    """
    __slots__ = ['conflict_resolving_strategy',
                 'overlapped',
                 'priority_attribute',
                 '_internal_attributes',
                 'vocabulary',
                 '_disamb_tagger',
                 'ambiguous']

    def __init__(self,
                 vocabulary: Union[str, dict, list, Vocabulary],
                 vocabulary_key='_regex_pattern_',
                 output_layer: str = 'regexes',
                 output_attributes: Sequence = None,
                 conflict_resolving_strategy: str = 'MAX',
                 overlapped: bool = False,
                 priority_attribute: str = None,
                 ambiguous: bool = False,
                 ignore_case=False
                 ):
        """Initialize a new RegexTagger instance.

        Parameters
        ----------
        vocabulary: list of dicts or pandas.DataFrame or csv file name
            regexes and output_attributes to annotate
        output_layer: str (Default: 'regexes')
            The name of the new layer.
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        overlapped: bool (Default: False)
            If True, the match of a regular expression may overlap with a match
            of the same regular expression.
            Note that this default setting will be overwritten by a pattern-
            specific setting if a pattern defines attribute 'overlapped';
        ambiguous
            If True, then the output layer is ambiguous
            If False, then the output layer is not ambiguous
        """
        self.conf_param = ['conflict_resolving_strategy',
                           'overlapped',
                           'priority_attribute',
                           '_internal_attributes',
                           'vocabulary',
                           '_disamb_tagger',
                           'ambiguous']
        self.input_layers = ()
        self.output_layer = output_layer
        if output_attributes is None:
            self.output_attributes = ()
        else:
            self.output_attributes = tuple(output_attributes)

        # output_attributes needed by tagger
        self._internal_attributes = set(self.output_attributes) | {'_group_', '_priority_'}

        from estnltk.taggers import Disambiguator

        def decorator(span, raw_text):
            return {name: getattr(span.annotations[0], name) for name in self.output_attributes}

        self._disamb_tagger = Disambiguator(output_layer=self.output_layer,
                                            input_layer=self.output_layer,
                                            output_attributes=self.output_attributes,
                                            decorator=decorator)

        def default_validator(s):
            return True

        vocabulary = Vocabulary.parse(vocabulary=vocabulary,
                                      key=vocabulary_key,
                                      attributes=('_regex_pattern_', '_group_', '_validator_', *self.output_attributes),
                                      default_rec={'_group_': 0, '_validator_': default_validator})
        self.vocabulary = vocabulary.to_regex(ignore_case=ignore_case)

        self.overlapped = overlapped
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self.conflict_resolving_strategy = conflict_resolving_strategy
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
        for record in self._match(text.text):
            layer.add_annotation((record['start'], record['end']), **record)
        layer = resolve_conflicts(layer=layer,
                                  conflict_resolving_strategy=self.conflict_resolving_strategy,
                                  priority_attribute=self.priority_attribute,
                                  status=status)

        if not self.ambiguous:
            layer = self._disamb_tagger.make_layer(text=text, layers={self.output_layer: layer}, status=status)
        return layer

    def _match(self, text):
        for reg, records in self.vocabulary.items():
            for matchobj in reg.finditer(text, overlapped=self.overlapped):
                for rec in records:
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
