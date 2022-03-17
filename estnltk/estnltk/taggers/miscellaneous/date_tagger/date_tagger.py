import datetime

from estnltk.legacy.dict_taggers.regex_tagger import RegexTagger
from estnltk.taggers.miscellaneous.date_tagger.regexes_v import regexes


class DateTagger(RegexTagger):
    """Tags date and time expressions.

    """

    __slots__ = []

    def __init__(self, output_layer='dates', conflict_resolving_strategy='MAX', overlapped=False):
        regexes_dict = regexes.reset_index().to_dict('records')
        vocabulary = self._create_vocabulary(regexes_dict)

        super().__init__(vocabulary=vocabulary,
                         output_layer=output_layer,
                         output_attributes=['date_text', 'type', 'probability', 'groups', 'extracted_values'],
                         conflict_resolving_strategy=conflict_resolving_strategy,
                         overlapped=overlapped,
                         )

    def _create_vocabulary(self, regexes):
        """Creates _vocabulary for regex_tagger

        """
        vocabulary = []
        for record in regexes:
            rec = {'_regex_pattern_': record['regex'],
                   '_group_': 0,
                   '_priority_': (0, 0),
                   'groups': lambda m: m.groupdict(),
                   'date_text': lambda m: m.group(0),
                   'type': record['type'],
                   'probability': record['probability'],
                   'example': record['example'],
                   'extracted_values': lambda m: self._extract_values(m)
                   }
            vocabulary.append(rec)
        return vocabulary

    @staticmethod
    def _clean_year(yearstring):
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
                    if d['second'] is None:
                        second = 0
                    else:
                        second = int(d['second'])
                    try:
                        t = datetime.datetime(year=year,
                                              month=int(d['MONTH']),
                                              day=day,
                                              hour=int(d['hour']),
                                              minute=int(d['minute']),
                                              second=second)

                        return t
                    except ValueError:
                        return None

                else:
                    try:
                        t = datetime.date(year=year,
                                          month=int(d['MONTH']),
                                          day=day)
                        return t
                    except ValueError:
                        return None
            else:
                return None

        else:
            if 'hour' in d:
                if d['second'] is None:
                    second = 0
                else:
                    second = int(d['second'])
                try:
                    t = datetime.time(hour=int(d['hour']),
                                      minute=int(d['minute']),
                                      second=second)
                    return t
                except ValueError:
                    return None
