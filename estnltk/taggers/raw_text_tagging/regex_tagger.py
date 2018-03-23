import regex as re
from pandas import DataFrame, read_csv

from estnltk.taggers import Tagger
from estnltk.layer import Layer
from estnltk.layer_operations import resolve_conflicts


class RegexTagger(Tagger):
    """
    Tags regular expression matches on the text.
    Searches matches for regular expressions in the text, solves the possible
    conflicts and creates a new layer of the matches.
    """
    input_layers = ()
    conf_param = ('_conflict_resolving_strategy',
                  'priority_attribute',
                  '_illegal_keywords',
                  'attributes',
                  '_internal_attributes',
                  '_vocabulary',
                  '_overlapped',
                  'layer_name')

    def __init__(self,
                 vocabulary,
                 attributes=None,
                 conflict_resolving_strategy='MAX',
                 overlapped=False,
                 layer_name='regexes',
                 priority_attribute=None,
                 ):
        """Initialize a new RegexTagger instance.

        Parameters
        ----------
        vocabulary: list of dicts or pandas.DataFrame or csv file name
            regexes and attributes to annotate
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        overlapped: bool (Default: False)
            If True, the match of a regular expression may overlap with a match
            of the same regular expression.
            Note that this default setting will be overwritten by a pattern-
            specific setting if a pattern defines attribute 'overlapped';
        layer_name: str (Default: 'regexes')
            The name of the new layer.
        """
        self.output_layer = layer_name
        if attributes is None:
            self.output_attributes = []
        else:
            self.output_attributes = attributes
        self.input_layers = ()

        self._illegal_keywords = {'start', 'end'}

        # attributes in output layer
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes
        # attributes needed by tagger
        self._internal_attributes = set(self.attributes)|{'_group_', '_priority_'}

        self._vocabulary = self._read_expression_vocabulary(vocabulary)
        self._overlapped = overlapped
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self._conflict_resolving_strategy = conflict_resolving_strategy
        self.priority_attribute = priority_attribute
        self.layer_name = layer_name

    def _read_expression_vocabulary(self, expression_vocabulary):
        if isinstance(expression_vocabulary, list):
            vocabulary = expression_vocabulary
        elif isinstance(expression_vocabulary, DataFrame):
            vocabulary = expression_vocabulary.to_dict('records')
        elif isinstance(expression_vocabulary, str):
            vocabulary = read_csv(expression_vocabulary, na_filter=False, index_col=False).to_dict('records')
        else:
            raise TypeError(str(type(expression_vocabulary)) + " not supported as vocabulary")
        records = []
        for record in vocabulary:
            if set(record) & self._illegal_keywords:
                raise KeyError('Illegal keys in vocabulary: ' + str(set(record)&self._illegal_keywords))
            _regex_pattern_ = record['_regex_pattern_']
            if isinstance(_regex_pattern_, str):
                _regex_pattern_ = re.compile(_regex_pattern_)

            _validator_ = record.get('_validator_')
            if isinstance(_validator_, str) and _validator_.startswith('lambda m:'):
                _validator_ = eval(_validator_)
            elif _validator_ is None:
                _validator_ = lambda m: True
            elif not callable(_validator_):
                raise ValueError("_validator_ must be a callable or a string starting with 'lambda m:'")

            rec = {'_regex_pattern_': _regex_pattern_,
                   '_group_': record.get('_group_', 0),
                   '_priority_': record.get('_priority_', 0),
                   '_validator_': _validator_
                   }
            # Whether the overlapped flag should be switched on or off
            overlapped = record.get('overlapped', None)
            if overlapped and type(overlapped) == bool:
                rec['overlapped'] = overlapped
            for key in self.attributes:
                if key not in record:
                    raise KeyError('Missing key in vocabulary: ' + key)
                value = record[key]
                if isinstance(value, str) and value.startswith('lambda m:'):
                    value = eval(value)
                rec[key] = value
            records.append(rec)

        return records

    def _make_layer(self, raw_text, input_layers=None, status=None):
        layer = Layer(name=self.layer_name,
                      attributes=tuple(self._internal_attributes),
                      )
        records = self._match(raw_text)
        layer = layer.from_records(records)
        layer = resolve_conflicts(layer,
                                  conflict_resolving_strategy=self._conflict_resolving_strategy,
                                  priority_attribute=self.priority_attribute,
                                  status=status)
        layer.attributes = self.attributes
        return layer

    def _match(self, text):
        matches = []
        for voc in self._vocabulary:
            # Whether the overlapped flag should be switched on or off
            overlapped_flag = voc.get('overlapped', self._overlapped)
            for matchobj in voc['_regex_pattern_'].finditer(text, overlapped=overlapped_flag):
                start, end = matchobj.span(voc['_group_'])
                if start == end:
                    continue
                if not voc['_validator_'](matchobj):
                    continue
                record = {
                    'start': start,
                    'end': end
                }
                for a in self._internal_attributes:
                    v = voc.get(a, 0)
                    if callable(v):
                        v = v(matchobj)
                    record[a] = v
                matches.append(record)
        return matches
