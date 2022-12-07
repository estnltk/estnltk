import datetime
import regex

from estnltk.taggers.miscellaneous.date_tagger.regexes_v import regexes as REGEXES_VOC

from estnltk.taggers.system.rule_taggers import RegexTagger, Ruleset
from estnltk.taggers.system.rule_taggers import StaticExtractionRule


def _global_decorator(text, base_span, annotation):
    assert 'match' in annotation and annotation['match'] is not None
    # Fill in dynamic attributes
    annotation['groups'] = annotation['groups']( annotation['match'] )
    annotation['date_text'] = annotation['date_text']( annotation['match'] )
    annotation['extracted_values'] = annotation['extracted_values']( annotation['match'] )
    return annotation


class DateTagger(RegexTagger):
    """Tags date and time expressions (experimental)."""

    __slots__ = []

    def __init__(self, output_layer='dates', conflict_resolver: str='KEEP_MAXIMAL', overlapped: bool=False):
        ruleset = DateTagger._create_extraction_rules( REGEXES_VOC )
        super().__init__(ruleset=ruleset, 
                         output_layer=output_layer,
                         output_attributes=('date_text', 'type', 'probability', 'groups', 'extracted_values'),
                         conflict_resolver=conflict_resolver,
                         decorator=_global_decorator,
                         overlapped=overlapped)

    @staticmethod
    def _create_extraction_rules(vocabulary):
        """Creates extraction rules for regex_tagger."""
        rules = []
        for voc_item in vocabulary:
            rule = StaticExtractionRule( pattern=regex.Regex( voc_item['regex'] ), 
                                         group=0, 
                                         attributes={ 'date_text': lambda m: m.group(0), 
                                                      'type': voc_item['type'], 
                                                      'probability': voc_item['probability'], 
                                                      'groups': lambda m: m.groupdict(), 
                                                      'extracted_values': lambda m: DateTagger._extract_values(m)
                                                      } )
            rules.append(rule)
        ruleset = Ruleset()
        ruleset.add_rules(rules)
        return ruleset

    @staticmethod
    def _clean_year(yearstring):
        """If year is two digits, adds 1900 or 2000."""
        year = int(yearstring)
        if year < 100:
            if year < 30:
                year += 2000
            else:
                year += 1900
        return year

    @staticmethod
    def _extract_values(match):
        """Extracts datetime, date or time values from regex matches if possible."""
        d = match.groupdict()
        if 'YEAR' in d or 'LONGYEAR' in d:
            if 'YEAR' in d:
                year = DateTagger._clean_year(d['YEAR'])
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
