import regex as re
from pandas import DataFrame, read_csv

from estnltk.text import Layer
from estnltk.text import Span, SpanList


class SpanConflict(Span):

    def __init__(self, *args, **kwargs):
        self.conflicting = [] # placeholder for the list of conflicting spans of the same layer
        super().__init__(*args, **kwargs)

    @property
    def length(self):
        return self.end - self.start


class LayerConflict(Layer):

    def __init__(self,
                 conflict_resolving_strategy='MAX',
                 *args, **kwargs):
        assert conflict_resolving_strategy in {'MAX', 'MIN', 'ALL'}, 'unknown conflict_resolving_strategy: ' + conflict_resolving_strategy
        self._conflict_resolving_strategy = conflict_resolving_strategy
        super().__init__(*args, **kwargs)

    # copy of Layer.from_records where Span is replaced by SpanConflict
    def from_records(self, records, rewriting=False) -> 'Layer':
        if self.parent is not None and not self._bound:
            self._is_lazy = True

        if self.ambiguous:
            if rewriting:
                self.spans = SpanList(ambiguous=True, layer=self)
                tmpspans = []
                for record_line in records:
                    if record_line is not None:
                        spns = SpanList(layer=self, ambiguous=False)
                        spns.spans = [SpanConflict(**{**record, **{'layer':self}}, legal_attributes=self.attributes) 
                                      for record in record_line]
                        tmpspans.append(spns)
                        self.spans.classes[(spns.spans[0].start, spns.spans[0].end)] = spns
                self.spans.spans = tmpspans
            else:
                for record_line in records:
                    self._add_spans([SpanConflict(**record, legal_attributes=self.attributes) for record in record_line])
        else:
            if rewriting:
                spns = SpanList(layer=self, ambiguous=False)
                spns.spans = [SpanConflict(**{**record, **{'layer': self}}, legal_attributes=self.attributes) for record in records if record is not None]

                self.spans = spns
            else:
                for record in records:
                    self.add_span(SpanConflict(
                        **record,
                        legal_attributes=self.attributes
                    ))
        return self

    def _delete_conflicting_spans(self, priority_key, delete_equal):
        '''
        If delete_equal is False, two spans are in conflict and one of them has
        a strictly lower priority determined by the priority_key, then that span
        is removed from the span list self.spans.spans
        If delete_equal is True, then one of the conflicting spans is removed
        even if the priorities are equal.
        Returns
            True, if some conflicts remained unsolved,
            False, otherwise.
        '''
        conflicts_exist = False
        span_removed = False
        span_list = sorted(self.spans.spans, key=priority_key)
        for obj in span_list:
            for c in obj.conflicting:
                if delete_equal or priority_key(obj) < priority_key(c):
                    # üldjuhul ebaefektiivne
                    try:
                        span_list.remove(c)
                        span_removed = True
                    except ValueError:
                        pass
                elif priority_key(obj) == priority_key(c) and c in span_list:
                    conflicts_exist = True
        if span_removed:
            self.spans.spans = sorted(span_list)
        return conflicts_exist


    def resolve_conflicts(self):
        priorities = set()
        self._number_of_conflicts = 0
        span_conflict_list = self.spans.spans
        for i, obj in enumerate(span_conflict_list):
            if '_priority_' in self.attributes:
                priorities.add(obj._priority_)
            for j in range(i+1, len(span_conflict_list)):
                if obj.end <= span_conflict_list[j].start:
                    break
                self._number_of_conflicts += 1
                obj.conflicting.append(span_conflict_list[j])
                span_conflict_list[j].conflicting.append(obj)
        if self._number_of_conflicts == 0:
            return self

        conflicts_exist = True
        if len(priorities) > 1:
            priority_key = lambda x: x._priority_
            conflicts_exist = self._delete_conflicting_spans(priority_key, delete_equal=False)

        if not conflicts_exist or self._conflict_resolving_strategy=='ALL':
            return self
        
        if self._conflict_resolving_strategy == 'MAX':
            priority_key = lambda x: (-x.length,x.start)
        elif self._conflict_resolving_strategy == 'MIN':
            priority_key = lambda x: (x.length,x.start)

        self._delete_conflicting_spans(priority_key, delete_equal=True)
        return self


class RegexTagger:
    """
    Searches matches for regular expressions in the text, solves the possible
    conflicts and creates a new layer of the matches.
    """
    def __init__(self,
                 vocabulary,
                 attributes=[],
                 conflict_resolving_strategy='MAX',
                 overlapped=False,
                 return_layer=False,
                 layer_name='regexes',
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
        return_layer: bool
            If True, RegexTagger.tag(text) returns a layer. 
            If False, RegexTagger.tag(text) annotates the text object with the
            layer and returns None.
        layer_name: str (Default: 'regexes')
            The name of the new layer.
        """
        self._illegal_keywords = {'start', 'end'}

        # attributes in output layer
        self._attributes = set(attributes)
        # attributes needed by tagger 
        self._internal_attributes = self._attributes|{'_group_', '_priority_'}
        
        self._vocabulary = self._read_expression_vocabulary(vocabulary)
        self._overlapped = overlapped
        self._return_layer = return_layer
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self._conflict_resolving_strategy = conflict_resolving_strategy
        self._layer_name = layer_name


    def _read_expression_vocabulary(self, expression_vocabulary):
        if isinstance(expression_vocabulary, list):
            vocabulary = expression_vocabulary
        elif isinstance(expression_vocabulary, DataFrame):
            vocabulary = expression_vocabulary.to_dict('records')
        elif isinstance(expression_vocabulary, str):
            vocabulary = read_csv(expression_vocabulary, na_filter=False, index_col=False).to_dict('records')
        else:
            raise TypeError(str(type(expression_vocabulary)) + " not supported as expression vocabulary")
        records = []
        for record in vocabulary:
            if set(record) & self._illegal_keywords:
                raise KeyError('Illegal keys in expression vocabulary: ' + str(set(record)&self._illegal_keywords))
            if self._internal_attributes-set(record):
                raise KeyError('Missing keys in expression vocabulary: ' + str(self._internal_attributes-set(record)))
            
            _regex_pattern_ = record['_regex_pattern_']
            if isinstance(_regex_pattern_, str):
                _regex_pattern_ = re.compile(_regex_pattern_)

            rec = {'_regex_pattern_': _regex_pattern_,
                   '_group_': record.get('_group_', 0),
                   '_priority_': record.get('_priority_', 0)
                   }
            for key in self._attributes:
                if key not in record:
                    raise KeyError('Missing key in expression vocabulary: ' + key)
                value = record[key]
                if isinstance(value, str) and value.startswith('lambda m:'):
                    value = eval(value)
                rec[key] = value
            records.append(rec)

        return records


    def tag(self, text):
        """Retrieves list of regex_matches in text.
        Parameters
        ----------
        text: Text
            The estnltk text object to search for matches.
        Returns
        -------
        Layer, if return_layer is True,
        None, otherwise.
        """
        layer = LayerConflict(name=self._layer_name,
                              attributes=self._attributes,
                              conflict_resolving_strategy=self._conflict_resolving_strategy
                              )
        records = self._match(text.text)
        layer = layer.from_records(records)
        layer.resolve_conflicts()
        if self._return_layer:
            return layer
        else:
            text[self._layer_name] = layer


    def _match(self, text):
        matches = []
        for voc in self._vocabulary:
            for matchobj in voc['_regex_pattern_'].finditer(text, overlapped=self._overlapped):
                record = {
                    'start': matchobj.span(voc['_group_'])[0],
                    'end': matchobj.span(voc['_group_'])[1],
                }
                for a in self._internal_attributes:
                    v = voc[a]
                    if callable(v):
                        v = v(matchobj)
                    record[a] = v
                matches.append(record)
        return matches
