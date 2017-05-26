import re
from estnltk.text import Layer


class TokenizationHintsTagger:

    def __init__(self, tag_numbers=True, tag_unit=True, tag_email=True, tag_initials=True):
        '''
        tag_numbers: boolean, default: True
            Tag numbers
                23  ->  23
                12 000  -> 12000
                -75 34.4 , 3 4  --> -7534,34
        tag_unit: boolean, default: True
            Tag fractional units of measure. km/h, m / s.
        tag_email: boolean, default: True
            Tag e-mails.
                bla@bla.bl
        '''
        self._tag_numbers = tag_numbers
        self._tag_units = tag_unit
        self._tag_emails = tag_email
        self._tag_initials = tag_initials


    def tag_pattern(self, text, pattern, group=0, attributes=[], **kwargs):
        '''
        text: Text
        pattern: str or sre.SRE_Pattern
        group: int
            The subgroup of the match which is to be tagged.
        attributes: list of str
        
        The value of each attribute in the attributes list is taken from kwargs,
        the default value is None. If the value is callable, it is called with 
        two arguments: the match object and the group number.
        '''
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        records = []
        for m in pattern.finditer(text.text):
            record = {'start': m.span(group)[0],
                      'end':   m.span(group)[1]}
            for a in attributes:
                value = kwargs.get(a)
                if callable(value):
                    record[a] = value(m, group)
                else: 
                    record[a] = value
            records.append(record)
        return records

    def tag(self, text):
        records = []
        if self._tag_initials:
            PATT_20_1 = re.compile(r'''
                ((?!P\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
                \s?\.\s?                 # tühikute vahel järgneda punkt
                ((?!S\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
                \s?\.\s?       # tühikute vahel järgneda punkt
                ((\.[A-ZÕÜÖÄ]\.)?[A-ZÕÜÖÄ][a-zõüöä]+)   # perekonnanimi
            ''', re.X)
            PATT_20_1_REPLACE = r'\1.\2.<+/>\3'.replace('<+/>', ' ')

            recs = self.tag_pattern(text,
                                    pattern=PATT_20_1,
                                    group=0,
                                    attributes=['priority', 'normalized'],
                                    priority=3,
                                    normalized=lambda m, g: m.expand(PATT_20_1_REPLACE)
                                    )
            records.extend(recs)

            PATT_20_2 = re.compile(r'''
                (\s(?!Hr|Pr|Dr|Mrs?|Sm|Nn|Lp|Nt|Jr)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
                \s?\.\s                 # tühikute vahel järgneda punkt
                ((?!Ja|Ei)[A-ZÕÜÖÄ][a-zõüöä]+)   # perekonnanimi
            ''', re.X)
            PATT_20_2_REPLACE = r'\1.<+/>\2'.replace('<+/>', ' ')
            recs = self.tag_pattern(text,
                                    pattern=PATT_20_2,
                                    group=0,
                                    attributes=['priority', 'normalized'],
                                    priority=4,
                                    normalized=lambda m, g: m.expand(PATT_20_2_REPLACE).strip()
                                    )
            records.extend(recs)

        if self._tag_numbers:
            _PATT_NUMBER = re.compile('-?(\d[\s\.]?)+(,\s?(\d[\s\.]?)+)?')
            recs = self.tag_pattern(text,
                                    pattern=_PATT_NUMBER,
                                    group=0,
                                    attributes=['priority', 'normalized'],
                                    priority=1,
                                    normalized=lambda m, g: re.sub('[\s\.]' ,'' , m.group(g))
                                    )
            records.extend(recs)
        if self._tag_emails:
            _PATT_EMAIL = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
            recs = self.tag_pattern(text,
                                    pattern=_PATT_EMAIL,
                                    group=0,
                                    attributes=['priority', 'normalized'],
                                    priority=2,
                                    normalized=None
                                    )
            records.extend(recs)

        if self._tag_units:
            _PATT_UNIT = re.compile(r'''            # PATT_14
                        (^|[^a-zõüöäA-ZÕÜÖÄ])       # algus või mittetäht
                        (([a-zõüöäA-ZÕÜÖÄ]{1,3})    # kuni 3 tähte
                        \s?/\s?                     # kaldkriips
                        ([a-zõüöäA-ZÕÜÖÄ]{1,3}))    # kuni kolm tähte
                        ([^a-zõüöäA-ZÕÜÖÄ]|$)       # mittetäht või lõpp
                        ''', re.X)
            recs = self.tag_pattern(text,
                                    pattern=_PATT_UNIT,
                                    group=2,
                                    attributes=['priority', 'normalized'],
                                    priority=0,
                                    normalized=lambda m, g: re.sub('\s' ,'' , m.group(g))
                                    )
            records.extend(recs)

        records.sort(key=lambda x: x['start']) # TODO: remove conflicts
                
        hints = Layer(name='tokenization_hints',
                      attributes=['normalized', 'priority']).from_records(records)
        text['tokenization_hints'] = hints
        return text
