import re
from estnltk.text import Layer


class TokenizationHintsTagger:

    def __init__(self, tag_numbers=True, tag_unit=True, tag_email=True):
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


    _PATT_NUMBER = re.compile('-?(\d[\s\.]?)+(,\s?(\d[\s\.]?)+)?')
    _PATT_EMAIL = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    _PATT_UNIT = re.compile(r'''            # PATT_14
                (^|[^a-zõüöäA-ZÕÜÖÄ])       # algus või mittetäht
                (([a-zõüöäA-ZÕÜÖÄ]{1,3})    # kuni 3 tähte
                \s?/\s?                     # kaldkriips
                ([a-zõüöäA-ZÕÜÖÄ]{1,3}))    # kuni kolm tähte
                ([^a-zõüöäA-ZÕÜÖÄ]|$)       # mittetäht või lõpp
                ''', re.X)

    def tag(self, text):
        records = []
        if self._tag_numbers:
            for m in self._PATT_NUMBER.finditer(text.text):
                norm = re.sub('[\s\.]' ,'' , m.group(0))
                records.append({'start': m.span(0)[0],
                                'end': m.span(0)[1],
                                'priority': 1,
                                'normalized': norm})
        if self._tag_emails:
            for m in self._PATT_EMAIL.finditer(text.text):
                records.append({'start': m.span(0)[0],
                                'end': m.span(0)[1],
                                'priority': 2,
                                'normalized': None})

        if self._tag_units:
            for m in self._PATT_UNIT.finditer(text.text):
                norm = re.sub('\s' ,'' , m.group(2))
                records.append({'start': m.span(2)[0],
                                'end': m.span(2)[1],
                                'priority': 0,
                                'normalized': norm})


        records.sort(key=lambda x: x['start']) # TODO: remove conflicts
                
        hints = Layer(name='tokenization_hints',
                      attributes=['normalized', 'priority']).from_records(records)
        text['tokenization_hints'] = hints
        return text
