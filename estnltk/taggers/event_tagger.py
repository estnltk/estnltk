from __future__ import unicode_literals

import ahocorasick
from sys import version_info

import regex as re

import six
if six.PY2:
    try:
        import unicodecsv as csv
    except ImportError as e:
        #event tagger depends on unicodecsv on python2
        #it is not in setup.py/requirements/meta.yaml, because it would have to be installed on python3 as well
        raise e
else:
    import csv


from estnltk.names import START, END
from pandas import DataFrame

TERM = 'term'
WSTART_RAW = 'wstart_raw'
WEND_RAW = 'wend_raw'
WSTART = 'wstart'
CSTART = 'cstart'

DEFAULT_METHOD = 'ahocorasick' if version_info.major >= 3 else 'naive'


class KeywordTagger(object):
    """A class that finds a list of keywords from Text object based on user-provided vocabulary.
    """

    def __init__(self, keyword_sequence=None, search_method=DEFAULT_METHOD, conflict_resolving_strategy='MAX',
                 return_layer=False, layer_name='keywords'):
        """Initialize a new KeywordTagger instance.

        Parameters
        ----------
        keyword_sequence: list-like or dict-like
            sequence of keywords to annotate
        search_method: 'naive', 'ahocorasick'
            Method to find events in text (default: 'naive' for python2 and 'ahocorasick' for python3).
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN'
            Strategy to choose between overlapping events (default: 'MAX').
        return_layer: bool
            if True, KeywordTagger.tag(text) returns a layer. If False, KeywordTagger.tag(text) annotates the text object with the layer instead.
        layer_name: str
            if return_layer is False, KeywordTagger.tag(text) annotates to this layer of the text object. Default 'keywords'
        """
        if keyword_sequence is None:
            raise ValueError("Can't really do something without keywords")
        if hasattr(keyword_sequence, 'get'):
            # I think we got a dict-like
            self.keyword_sequence = list(keyword_sequence.keys())
            self.mapping = True
            self.map = keyword_sequence
        else:
            self.keyword_sequence = keyword_sequence
            self.mapping = False
        self.layer_name = layer_name
        self.return_layer = return_layer
        if search_method not in ['naive', 'ahocorasick']:
            raise ValueError("Unknown search_method '%s'." % search_method)
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        if search_method == 'ahocorasick' and version_info.major < 3:
            raise ValueError(
                "search_method='ahocorasick' is not supported by Python %s. Try 'naive' instead." % version_info.major)
        self.search_method = search_method
        self.ahocorasick_automaton = None
        self.conflict_resolving_strategy = conflict_resolving_strategy

    def _find_keywords_naive(self, text):
        events = []
        for entry in self.keyword_sequence:
            start = text.find(entry)
            while start > -1:
                events.append({START: start, END: start + len(entry)})
                start = text.find(entry, start + 1)
        return events

    def _find_keywords_ahocorasick(self, text):
        events = []
        if self.ahocorasick_automaton == None:
            self.ahocorasick_automaton = ahocorasick.Automaton(ahocorasick.STORE_LENGTH)
            for index, entry in enumerate(self.keyword_sequence):
                self.ahocorasick_automaton.add_word(entry)
            self.ahocorasick_automaton.make_automaton()
        for end, length in self.ahocorasick_automaton.iter(text):
            events.append(
                {START: end - length + 1, END: end + 1}
            )
        return events

    def _resolve_conflicts(self, events):
        events.sort(key=lambda event: event[END])
        events.sort(key=lambda event: event[START])
        if self.conflict_resolving_strategy == 'ALL':
            return events
        elif self.conflict_resolving_strategy == 'MAX':
            if len(events) < 2:
                return events
            bookmark = 0
            while bookmark < len(events) - 1 and events[0][START] == events[bookmark + 1][START]:
                bookmark += 1
            new_events = [events[bookmark]]
            for i in range(bookmark + 1, len(events) - 1):
                if events[i][END] > new_events[-1][END] and events[i][START] != events[i + 1][START]:
                    new_events.append(events[i])
            if events[-1][END] > new_events[-1][END]:
                new_events.append(events[-1])
            return new_events
        elif self.conflict_resolving_strategy == 'MIN':
            if len(events) < 2:
                return events
            while len(events) > 1 and events[-1][START] == events[-2][START]:
                del events[-1]
            for i in range(len(events) - 2, 0, -1):
                if events[i][START] == events[i - 1][START] or events[i][END] >= events[i + 1][END]:
                    del events[i]
            if len(events) > 1 and events[0][END] >= events[1][END]:
                del events[0]
            return events

    def tag(self, text):
        """Retrieves list of keywords in text.

        Parameters
        ----------
        text: Text
            The text to search for events.

        Returns
        -------
        list of vents sorted by start, end
        """
        if self.search_method == 'ahocorasick':
            events = self._find_keywords_ahocorasick(text.text)
        elif self.search_method == 'naive':
            events = self._find_keywords_naive(text.text)

        events = self._resolve_conflicts(events)
        if self.mapping:
            for item in events:
                item['type'] = self.map[
                    text.text[item['start']:item['end']]
                ]

        if self.return_layer:
            return events
        else:
            text[self.layer_name] = events


class RegexTagger(KeywordTagger):
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


class EventTagger(KeywordTagger):
    """A class that finds a list of events from Text object based on 
    user-provided vocabulary. The events are tagged by several metrics (start, 
    end, cstart, wstart, wstart_raw, wend_raw) and user-provided classificators.
    
    The word start ``wstart`` and char start ``cstart`` of an event are 
    calculated as if all the events consist of one character.  ``cstart`` and 
    ``wstart`` are calculated only if there is no overlapping events.
    
    ``wstart_raw``, ``wend_raw`` show at which word the event starts and ends
    considering the real length of events.
    """
    
    def __init__(self, event_vocabulary, 
                 search_method=DEFAULT_METHOD, case_sensitive=True, 
                 conflict_resolving_strategy='MAX', 
                 return_layer=False, layer_name='events'):
        """Initialize a new EventTagger instance.

        Parameters
        ----------
        event_vocabulary: list of dict, str, pandas.DataFrame
            Vocabulary of events. There must be one key (column) called 'term' 
            in ``event_vocabulary``. That refers to the strings searched from 
            the text. Other keys ('type' in the following examples) are optional. 
            No key may have name 'start', 'end', 'cstart', 'wstart', 
            'wstart_raw' or 'wend_raw'.

            If ``list of dict``, then every dict in the list is a vocabulary entry. 

            Example::

                event_vocabulary = [{'term': 'Harv',    'type': 'sagedus'}, 
                                    {'term': 'peavalu', 'type': 'sümptom'}]
                                        
            If ``str``, then event vocabulary is read from csv file named
            ``event_vocabulary``.

            Example::

                term,type
                Harv,sagedus
                peavalu,sümptom
                                
            If ``pandas.DataFrame``, then the vocabulary of events is created 
            from the ``pandas.DataFrame``.

            Example::
            
                event_vocabulary = DataFrame([['Harv',    'sagedus'], 
                                              ['peavalu', 'sümptom']], 
                                      columns=['term',    'type'])
                                          
        search_method: 'naive', 'ahocorasic'
            (default: 'naive' for python2 and 'ahocorasick' for python3)
            
            Method to find events in text.
        case_sensitive: bool (default: True)        
            If ``True``, then the terms are searched from the text case sensitive.

            If ``False``, then the terms are searched from the text case insensitive.
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlaping events.

            If 'ALL' returns all events.

            If 'MAX' returns all the events that are not contained by any other event.

            If 'MIN' returns all the events that don't contain any other event.
        return_layer: bool
            If ``True``, EventTagger.tag(text) returns a layer. 
            If ``False``, EventTagger.tag(text) annotates the text object with the layer instead.
        layer_name: str (default: 'events')
            If ``return_layer`` is ``False``, EventTagger.tag(text) annotates 
            to this layer of the text object. 
        """
        self.layer_name = layer_name
        self.return_layer = return_layer
        if search_method not in ['naive', 'ahocorasick']:
            raise ValueError("Unknown search_method '%s'." % search_method)
        self.case_sensitive = case_sensitive
        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown onflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        if search_method == 'ahocorasick' and version_info.major < 3:
            raise ValueError(
                "search_method='ahocorasick' is not supported by Python %s. Try 'naive' instead." % version_info.major)
        self.event_vocabulary = self._read_event_vocabulary(event_vocabulary)
        self.search_method = search_method
        self.ahocorasick_automaton = None
        self.conflict_resolving_strategy = conflict_resolving_strategy

    @staticmethod
    def _read_event_vocabulary(event_vocabulary):
        if isinstance(event_vocabulary, list):
            event_vocabulary = event_vocabulary
        elif isinstance(event_vocabulary, DataFrame):
            event_vocabulary = event_vocabulary.to_dict('records')
        elif isinstance(event_vocabulary, str):
            with open(event_vocabulary, 'rb') as file:
                reader = csv.DictReader(file)
                event_vocabulary = []
                for row in reader:
                    event_vocabulary.append(row)
        else:
            raise TypeError("%s not supported as event_vocabulary" % type(event_vocabulary))
        if len(event_vocabulary) == 0:
            return []
        if (START in event_vocabulary[0] or
                    END in event_vocabulary[0] or
                    WSTART in event_vocabulary[0] or
                    CSTART in event_vocabulary[0] or
                    WSTART_RAW in event_vocabulary[0] or
                    WEND_RAW in event_vocabulary[0]):
            raise KeyError('Illegal key in event vocabulary.')
        if TERM not in event_vocabulary[0]:
            raise KeyError("Missing key '" + TERM + "' in event vocabulary.")
        return event_vocabulary

    def _find_events_naive(self, text):
        _text = text if self.case_sensitive else text.lower()
        events = []
        for entry in self.event_vocabulary:
            term = entry[TERM] if self.case_sensitive else entry[TERM].lower()
            start = _text.find(term)
            while start > -1:
                events.append(entry.copy())
                events[-1].update({START: start, END: start + len(entry[TERM])})
                start = _text.find(term, start + 1)
        return events

    def _find_events_ahocorasick(self, text):
        events = []
        if self.ahocorasick_automaton == None:
            self.ahocorasick_automaton = ahocorasick.Automaton()
            for entry in self.event_vocabulary:
                term = entry[TERM] if self.case_sensitive else entry[TERM].lower()
                self.ahocorasick_automaton.add_word(term, entry)
            self.ahocorasick_automaton.make_automaton()
        _text = text if self.case_sensitive else text.lower()
        for item in self.ahocorasick_automaton.iter(_text):
            events.append(item[1].copy())
            events[-1].update({START: item[0] + 1 - len(item[1][TERM]), END: item[0] + 1})
        return events

    def _event_intervals(self, events, text):
        bookmark = 0
        overlapping_events = False
        last_end = 0
        for event in events:
            if last_end > event[START]:
                overlapping_events = True
            last_end = event[END]
            event[WSTART_RAW] = len(text.word_spans)
            event[WEND_RAW] = 0
            for i in range(bookmark, len(text.word_spans) - 1):
                if text.word_spans[i][0] <= event[START] < text.word_spans[i + 1][0]:
                    event[WSTART_RAW] = i
                    bookmark = i
                if text.word_spans[i][0] < event[END] <= text.word_spans[i + 1][0]:
                    event[WEND_RAW] = i + 1
                    break
        if not overlapping_events:
            w_shift = 0
            c_shift = 0
            for event in events:
                event[WSTART] = event[WSTART_RAW] - w_shift
                w_shift += event[WEND_RAW] - event[WSTART_RAW] - 1

                event[CSTART] = event[START] - c_shift
                c_shift += event[END] - event[START] - 1
        return events

    def tag(self, text):
        """Retrieves list of events in text.
        
        Parameters
        ----------
        text: Text
            The text to search for events.
            
        Returns
        -------
        list of events sorted by start, end
        """
        if self.search_method == 'ahocorasick':
            events = self._find_events_ahocorasick(text.text)
        elif self.search_method == 'naive':
            events = self._find_events_naive(text.text)

        events = self._resolve_conflicts(events)

        self._event_intervals(events, text)

        if self.return_layer:
            return events
        else:
            text[self.layer_name] = events
