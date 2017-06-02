import regex as re

email_patterns = [
     {'_group_': 1,
      '_priority_': (0, 0),
      '_regex_pattern_': '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)',
      'comment': 'e-mail',
      'example': 'bla@bla.bl',
      'normalized': 'lambda m: None'}
            ]

number_patterns = [
    {'_group_': 0,
      '_priority_': (1, 0),
      '_regex_pattern_': '-?(\\d[\\s\\.]?)+(,\\s?(\\d[\\s\\.]?)+)?',
      'comment': 'number',
      'example': '-34 567 000 123 , 456',
      'normalized': "lambda m: re.sub('[\\s\\.]' ,'' , m.group(0))"},
            ]

unit_patterns = [
    {
     '_regex_pattern_': re.compile(r'''            # PATT_14
                        (^|[^a-zõüöäA-ZÕÜÖÄ])       # algus või mittetäht
                        (([a-zõüöäA-ZÕÜÖÄ]{1,3})    # kuni 3 tähte
                        \s?/\s?                     # kaldkriips
                        ([a-zõüöäA-ZÕÜÖÄ]{1,3}))    # kuni kolm tähte
                        ([^a-zõüöäA-ZÕÜÖÄ]|$)       # mittetäht või lõpp
                        ''', re.X),
     '_group_': 2,
     '_priority_': (2, 0),
     'normalized': "lambda m: re.sub('\s' ,'' , m.group(2))",
     'comment': 'unit of measure',
     'example': 'km / h',
      },

                 ]

initial_patterns = [
    {
     '_regex_pattern_': re.compile(r'''
                        ((?!P\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
                        \s?\.\s?                 # tühikute vahel järgneda punkt
                        ((?!S\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
                        \s?\.\s?       # tühikute vahel järgneda punkt
                        ((\.[A-ZÕÜÖÄ]\.)?[A-ZÕÜÖÄ][a-zõüöä]+)   # perekonnanimi
                        ''', re.X),
     '_group_': 0,
     '_priority_': (3, 0),
     'normalized': lambda m: re.sub('\1.\2. \3' ,'' , m.group(0)),
     'comment': 'initials',
     'example': 'A. H. Tammsaare',
     }
                    ]
