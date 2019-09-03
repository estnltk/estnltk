from estnltk.taggers.raw_text_tagging.date_tagger.regexes_v import regexes
from estnltk.taggers import Tagger, RegexTagger
import datetime


regexes = regexes.reset_index().to_dict('records')


class DateTagger(Tagger):
    """Tags date and time expressions.

    """
    conf_param = ['_tagger']

    def __init__(self, layer_name='dates', conflict_resolving_strategy='MAX', overlapped=False):
        self.output_layer = layer_name
        self.output_attributes = ['date_text','type', 'probability', 'groups', 'extracted_values']
        self.input_layers = []

        vocabulary = self._create_vocabulary(regexes)

        self._tagger = RegexTagger(vocabulary=vocabulary,
                                   output_attributes=self.output_attributes,
                                   conflict_resolving_strategy=conflict_resolving_strategy,
                                   overlapped=overlapped,
                                   output_layer=self.output_layer,
                                   )

    def _make_layer(self, text, layers, status=None):
        return self._tagger.make_layer(text, layers, status)

    def _create_vocabulary(self, regexes):
        """Creates _vocabulary for regex_tagger

        """
        vocabulary = []
        for record in regexes:
            rec = {'_regex_pattern_': record['regex'],
                   '_group_': 0,
                   '_priority_': (0,0),
                   'groups': lambda m: str(m.groupdict()), 
                   'date_text': lambda m: m.group(0),
                   'type': record['type'],
                   'probability': record['probability'],
                   'example': record['example'],
                   'extracted_values' : lambda m: self._extract_values(m)
                  }
            vocabulary.append(rec)
        return vocabulary

    def _clean_year(self, yearstring):
        """If year is two digits, adds 1900 or 2000

        """
        year = int(yearstring)
        if year < 100:
            if year < 30:
                year += 2000
            else:
                year += 1900
        return year

    def _extract_values(self, match):
        """Extracts datetime, date or time values from regex matches if possible

        """
        d = match.groupdict()
        if 'YEAR' in d or 'LONGYEAR' in d:
            if 'YEAR' in d:
                year = self._clean_year(d['YEAR'])
            else:
                year = int(d['LONGYEAR'])
            if 'DAY' in d:
                day = int(d['DAY'])
                if 'hour' in d:
                    if d['second'] == None:
                        second = 0
                    else:
                        second = int(d['second'])
                    try:    
                        t = datetime.datetime(year = year,
                                                month = int(d['MONTH']),
                                                day = day,
                                                hour = int(d['hour']),
                                                minute = int(d['minute']),
                                                second = second)
                                        
                        return t
                    except ValueError:
                        return None       
                
                else:
                    try:
                        t = datetime.date(year = year,
                                            month = int(d['MONTH']),
                                            day = day)
                        return t
                    except ValueError:
                        return None 
            else:
                return None
        
        else:
            if 'hour' in d:
                if d['second'] == None:
                    second = 0
                else:
                    second = int(d['second'])
                try:    
                    t = datetime.time(hour = int(d['hour']),
                                        minute = int(d['minute']),
                                        second = second)
                    return t
                except ValueError:
                    return None 
