import re
from pandas import DataFrame

class RegexTagger:
    """ 
    """
    def __init__(self, regex_sequence=None, conflict_resolving_strategy='MAX', return_layer=False,
                 layer_name='regexes'):
        """Initialize a new RegexTagger instance.
        
        Parameters
        ----------
        regex_sequence: list-like or dict-like
            sequence of regexes to annotate
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN'
            Strategy to choose between overlapping events (default: 'MAX').
        return_layer: bool
            if True, KeywordTagger.tag(text) returns a layer. If False, KeywordTagger.tag(text) annotates the text object with the layer instead.
        layer_name: str
            if return_layer is False, KeywordTagger.tag(text) annotates to this layer of the text object. Default 'keywords'
        """
        if regex_sequence is None:
            raise ValueError("Can't really do something without keywords")
        if isinstance(regex_sequence, DataFrame):
            # I think we got a dataframe
            restricted_words = set(['groups', 'start', 'end', 'regex'])
            columns = set(regex_sequence.columns)
            if columns.intersection(restricted_words):
                banned = ', '.join(list(columns.intersection(restricted_words)))
                raise ValueError('Illegal column names in dataframe: {}'.format(banned))


            self.header = regex_sequence.index.name
            self.map = regex_sequence.to_dict('index')
            self.regex_sequence = list(self.map.keys())
            self.mapping = True
        else:
            self.regex_sequence = regex_sequence
            self.mapping = False
        self.layer_name = layer_name
        self.return_layer = return_layer
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self.conflict_resolving_strategy = conflict_resolving_strategy

    def tag(self, text):
        """Retrieves list of regex_matches in text.
        Parameters
        ----------
        text: Text
            The estnltk text object to search for events.
        Returns
        -------
        list of matches
        """
        matches = self._match(text.text)
        matches = self._resolve_conflicts(matches)

        if self.return_layer:
            return matches
        else:
            text[self.layer_name] = matches

    def _match(self, text):
        matches = []
        if self.mapping:
            seq = self.map.keys()
        else:
            seq = self.regex_sequence

        for r in seq:
            for matchobj in re.finditer(r, text, overlapped=True):
                groups = (matchobj.groupdict())
                result = {
                    'start': matchobj.start(),
                    'end': matchobj.end(),
                    'regex': r,
                    'groups':groups
                }

                if self.mapping:
                    for k, v in self.map[r].items():
                        if k not in result.keys():
                            result[k] = v

                matches.append(
                    result
                )

        return matches
