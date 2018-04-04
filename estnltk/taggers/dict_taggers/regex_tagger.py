import regex as re
from pandas import DataFrame
from typing import Sequence, Union

from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
from estnltk.layer_operations import resolve_conflicts
from estnltk.taggers import Vocabulary


class RegexTagger(Tagger):
    """
    Tags regular expression matches on the text.
    Searches matches for regular expressions in the text, solves the possible
    conflicts and creates a new layer of the matches.
    """
    input_layers = ()
    conf_param = ('conflict_resolving_strategy',
                  'overlapped',
                  'priority_attribute',
                  '_illegal_keywords',
                  '_internal_attributes',
                  'vocabulary',
                  )

    def __init__(self,
                 vocabulary: Union[str, dict, list, DataFrame, Vocabulary],
                 output_layer: str = 'regexes',
                 output_attributes: Sequence = None,
                 conflict_resolving_strategy: str = 'MAX',
                 overlapped: bool = False,
                 priority_attribute: str = None,
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
        """
        self.output_layer = output_layer
        if output_attributes is None:
            self.output_attributes = []
        else:
            self.output_attributes = output_attributes

        self._illegal_keywords = {'start', 'end'}

        # output_attributes needed by tagger
        self._internal_attributes = set(self.output_attributes)|{'_group_', '_priority_'}

        if isinstance(vocabulary, Vocabulary):
            self.vocabulary = vocabulary
        else:
            self.vocabulary = Vocabulary(vocabulary=vocabulary,
                                         key='_regex_pattern_',
                                         regex_attributes=['_regex_pattern_'],
                                         default_rec={'_group_': 0, '_validator_': lambda s: True}
                                         )
        self.overlapped = overlapped
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self.conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute

    def _make_layer(self, raw_text, layers=None, status=None):
        layer = Layer(name=self.output_layer,
                      attributes=tuple(self._internal_attributes),
                      )
        records = self._match(raw_text)
        layer = layer.from_records(records)
        layer = resolve_conflicts(layer=layer,
                                  conflict_resolving_strategy=self.conflict_resolving_strategy,
                                  priority_attribute=self.priority_attribute,
                                  status=status)
        layer.attributes = self.output_attributes
        return layer

    def _match(self, text):
        matches = []
        for reg, records in self.vocabulary.items():
            # Whether the overlapped flag should be switched on or off
            #overlapped_flag = records.get('overlapped', self.overlapped)
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
                    matches.append(record)
        return matches
