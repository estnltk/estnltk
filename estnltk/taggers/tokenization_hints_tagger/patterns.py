import regex as re

"""
This is a vocabulary file for the TokenizationHintsTagger.
The entries here are lists of records in RegexTagger vocabulary format.
Each record must contain '_regex_pattern_' and 'normalized' keyword, other
kewords are optional. The names of the entries need to be declared in
TokenizationHintsTagger.
"""


MACROS = {
            'LOWERCASE': 'a-zšžõäöü',
            'UPPERCASE': 'A-ZŠŽÕÄÖÜ',
            'NUMERIC': '0-9',
            '1,3': '{1,3}'
         }
MACROS['LETTERS'] = MACROS['LOWERCASE'] + MACROS['UPPERCASE']
MACROS['ALPHANUM'] = MACROS['LETTERS'] + MACROS['NUMERIC']

email_patterns = [
     {'_group_': 1,
      '_priority_': (0, 0),
      '_regex_pattern_': r'([{ALPHANUM}_.+-]+@[{ALPHANUM}-]+\.[{ALPHANUM}-.]+)'.format(**MACROS),
      'comment': 'e-mail',
      'example': 'bla@bla.bl',
      'normalized': 'lambda m: None'}
            ]

number_patterns = [
    {'_group_': 0,
      '_priority_': (1, 0),
      '_regex_pattern_': r'-?([{NUMERIC}][\s\.]?)+(,\s?([{NUMERIC}][\s\.]?)+)?'.format(**MACROS),
      'comment': 'number',
      'example': '-34 567 000 123 , 456',
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
            ]

unit_patterns = [
    {
     '_regex_pattern_': re.compile(r'''        # PATT_14
                        (^|[^{LETTERS}])       # algus või mittetäht
                        (([{LETTERS}]{1,3})    # kuni 3 tähte
                        \s?/\s?                # kaldkriips
                        ([{LETTERS}]{1,3}))    # kuni kolm tähte
                        ([^{LETTERS}]|$)       # mittetäht või lõpp
                        '''.format(**MACROS), re.X),
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
                        ((?!P\.)[{UPPERCASE}][{LOWERCASE}]?)              # initsiaalid, millele võib
                        \s?\.\s?                                          # tühikute vahel järgneda punkt
                        ((?!S\.)[{UPPERCASE}][{LOWERCASE}]?)              # initsiaalid, millele võib
                        \s?\.\s?                                          # tühikute vahel järgneda punkt
                        ((\.[{UPPERCASE}]\.)?[{UPPERCASE}][{LOWERCASE}]+) # perekonnanimi
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (3, 0),
     'normalized': lambda m: re.sub('\1.\2. \3' ,'' , m.group(0)),
     'comment': 'initials',
     'example': 'A. H. Tammsaare',
     }
                    ]
