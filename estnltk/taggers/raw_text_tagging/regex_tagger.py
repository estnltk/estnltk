import regex as re
from pandas import DataFrame, read_csv

from estnltk.text import Layer


class SpanConflict:
    _id = 0
    
    def __init__(self, rec):
        self.rec = rec
        self.length = rec['end'] - rec['start']
        self.conflicting = []
        self.id = SpanConflict._id
        SpanConflict._id += 1

    def __lt__(self, other):
        return (self.rec['start'], self.rec['end']) < (other.rec['start'], other.rec['end'])

    def __repr__(self):
        return repr(self.rec)+', with '+str(len(self.conflicting))+' conflicts'


class RegexTagger:
    """ 
    """
    def __init__(self,
                 vocabulary=None,
                 vocabularies=None,
                 attributes=[],
                 conflict_resolving_strategy='MAX',
                 overlapped=False,
                 return_layer=False,
                 layer_name='regexes',
                 ):
        """Initialize a new RegexTagger instance.
        
        Parameters
        ----------
        vocabulary: list-like or dict-like or pandas.DataFrame
            regexes and attributes to annotate
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN'
            Strategy to choose between overlapping events (default: 'MAX').
        return_layer: bool
            if True, RegexTagger.tag(text) returns a layer. If False, RegexTagger.tag(text) annotates the text object with the layer instead.
        layer_name: str
            if RegexTagger.tag(text) annotates to this layer of the text object. Default 'regexes'
        """
        self._illegal_keywords = {'start', 'end'}

        # attributes in output layer
        self._attributes = set(attributes)
        # attributes needed by tagger 
        self._internal_attributes = self._attributes|{'_group_', '_priority_'}
        
        if vocabularies:
            if vocabulary:
                raise ValueError("Both, vocabulary and vocabularies given.")
            self._vocabulary = []
            for v in vocabularies:
                self._vocabulary.extend(self._read_expression_vocabulary(v))
        elif vocabulary:
            self._vocabulary = self._read_expression_vocabulary(vocabulary)
        self._overlapped = overlapped
        self._return_layer = return_layer
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self._conflict_resolving_strategy = conflict_resolving_strategy
        self._layer_name = layer_name


    def _delete_conflicting_spans(self, span_conflict_list, priority_key):
        '''
        If two spans are in conflict and one of them has a strictly lower 
        priority determined by the priority_key, then that span is removed from
        the span_conflict_list.
        '''
        conflicts_exist = False
        span_conflict_list = sorted(span_conflict_list, key=priority_key)
        for obj in span_conflict_list:
            for c in obj.conflicting:
                if priority_key(obj) < priority_key(c):
                    # üldjuhul ebaefektiivne
                    try:
                        span_conflict_list.remove(c)
                    except ValueError:
                        pass
                elif c in span_conflict_list:
                    conflicts_exist = True
        return span_conflict_list, conflicts_exist


    def _resolve_conflicts(self, records):
        priorities = set()
        self._number_of_conflicts = 0
        span_conflict_list = sorted([SpanConflict(rec) for rec in records])
        for i, obj in enumerate(span_conflict_list):
            priorities.add(obj.rec['_priority_'])
            for j in range(i+1, len(span_conflict_list)):
                if obj.rec['end'] <= span_conflict_list[j].rec['start']:
                    break
                self._number_of_conflicts += 1
                obj.conflicting.append(span_conflict_list[j])
                span_conflict_list[j].conflicting.append(obj)
        if self._number_of_conflicts == 0:
            return [obj.rec for obj in span_conflict_list]

        conflicts_exist = True
        if len(priorities) > 1:
            priority_key = lambda x: x.rec['_priority_']
            conflicts_exist, span_conflict_list = self._delete_conflicting_spans(span_conflict_list, priority_key)

        if not conflicts_exist or self._conflict_resolving_strategy=='ALL':
            return [obj.rec for obj in sorted(span_conflict_list)]
        
        if self._conflict_resolving_strategy == 'MAX':
            priority_key = lambda x: (-x.length,x.rec['start'],x.id)
            _, span_conflict_list = self._delete_conflicting_spans(span_conflict_list, priority_key)
            return [obj.rec for obj in sorted(span_conflict_list)]

        if self._conflict_resolving_strategy == 'MIN':
            priority_key = lambda x: (x.length,x.rec['start'],x.id)
            _, span_conflict_list = self._delete_conflicting_spans(span_conflict_list, priority_key)
            return [obj.rec for obj in sorted(span_conflict_list)]


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


    def tag(self, text, status={}):
        """Retrieves list of regex_matches in text.
        Parameters
        ----------
        text: Text
            The estnltk text object to search for events.
        status: dict
            A pointer to conflict info. The total number of conflicts before
            conflict resolving is saved to status['conflicts'].
        Returns
        -------
        list of matches
        """
        records = self._match(text.text)
        records = self._resolve_conflicts(records)
        status['conflicts'] = self._number_of_conflicts
        layer = Layer(name=self._layer_name,
                      attributes=self._attributes).from_records(records)
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
