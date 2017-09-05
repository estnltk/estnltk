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
            'PUNCT1' : '[.?!"\'()+,-/:;<=>]',
            'PUNCT2' : '[?!"\'()+,-/:;<=>]',
            'NUMERIC': '0-9',
            '1,3': '{1,3}',
            '2,': '{2,}',
            # A) Abbreviations that should come out of tokenization as they are
            'ABBREVIATIONS1': '('+\
                               'a|[Dd]r|[Hh]r|[Hh]rl|[Ii]bid|[Jj]r|[Kk]od|[Kk]oost|[Ll]p|'+\
                               'lüh|[Mm]rs?|nn|[Nn]t|[Pp]r|so|st|saj|sealh|sh|[Ss]m|'+\
                               '[Tt]lk|tn|[Tt]oim|[Vv]rd|va|[Vv]t'+\
                              ')',
            # B) Abbreviations that may be affected by tokenization (split further into tokens)
            'ABBREVIATIONS2': '('+\
                               'A\s?\.\s?D|'+\
                               'a\s?\.\s?k\s?\.\s?a|'+\
                               'e\s?\.\s?m\s?\.\s?a|'+\
                               'e\s?\.\s?Kr|'+\
                               'k\s?\.\s?a|'+\
                               'm\s?\.\s?a\s?\.\s?j|'+\
                               'p\s?\.\s?Kr|'+\
                               's\s?\.\s?o|'+\
                               's\s?\.\s?t|'+\
                               'v\s?\.\s?a'+\
                              ')',
            # C) Abbreviations that can appear at the beginning of text (e.g titles)
            'ABBREVIATIONS3': '('+\
                               '[Dd]r|[Hh]r|[Kk]od|[Ll]g?p|[Mm]rs?|[Pp]r|[Ss]m|[Nn]t|'+\
                               '[Tt]oim|[Vv]rd|[Vv]t'+\
                              ')',
         }
MACROS['LETTERS'] = MACROS['LOWERCASE'] + MACROS['UPPERCASE']
MACROS['ALPHANUM'] = MACROS['LETTERS'] + MACROS['NUMERIC']

email_patterns = [
     {'pattern_type': 'e-mail',
      '_group_': 1,
      '_priority_': (0, 0),
      '_regex_pattern_': r'([{ALPHANUM}_.+-]+@[{ALPHANUM}-]+\.[{ALPHANUM}-.]+)'.format(**MACROS),
      'comment': 'e-mail',
      'example': 'bla@bla.bl',
      'normalized': 'lambda m: None'}
            ]

number_patterns = [
    { 'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (1, 0),
      '_regex_pattern_': r'-?([{NUMERIC}][\s\.]?)+(,\s?([{NUMERIC}][\s\.]?)+)?'.format(**MACROS),
      'comment': 'number',
      'example': '-34 567 000 123 , 456',
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) First 10 Roman numerals ending with period, but not ending the sentence.',
      'example': 'II. peatükis',
      'pattern_type': 'roman_numerals',
      '_group_': 2,
      '_priority_': (1, 0),
      '_regex_pattern_': re.compile(r'''                          # 
                         (^|\s)                                   # beginning or space
                         ((I|II|III|IV|V|VI|VII|VIII|IX|X)\s*\.)  # roman numeral + period
                         \s*([{LOWERCASE}]|\d\d\d\d)              # lowercase word or year number (sentence continues)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(2))"},
              ]

unit_patterns = [
    { 'pattern_type': 'unit',
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
    { 'pattern_type': 'name',
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

abbreviation_patterns = [
    { 'comment': 'A.1.1) Abbreviations that end with period;',
      'example': 'sealh.',
      'pattern_type': 'non_ending_abbreviation',  # TODO: why name "non_ending_abbreviation"?
      '_regex_pattern_': re.compile(r'''
                        \s                                   # space
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}) # abbreviation
                        \s?\.)                               # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 1, 1),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.1.2) Abbreviations that appear at the beginning of text, and end with period;',
      'example': 'Lp.',
      'pattern_type': 'non_ending_abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ^                     # beginning of text
                        ({ABBREVIATIONS3}     # abbreviation
                        \s?\.)                # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 1, 2),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.1.3) Abbreviations that end with punctuation (excl period);',
      'example': 'e.m.a,',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        \s                                       # space
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}))    # abbreviation
                        {PUNCT2}                                 # punctuation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 1, 3),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.2) Abbreviations that do not have ending punctuation;',
      'example': 'Hr',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        \s                                   # space
                        ({ABBREVIATIONS1}|{ABBREVIATIONS2})  # abbreviation
                        \s                                   # space
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 2),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.3.1) Abbreviations that are preceded by punctuation symbols, and end with period;',
      'example': '(k.a.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        {PUNCT1}                                       # punctuation
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2})\s?\.)     # abbreviation + period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 3, 1),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.3.2) Abbreviations that are preceded by punctuation symbols, and end with punctuation (excl period);',
      'example': '1999.a.,',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        {PUNCT1}                                          # punctuation
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}))             # abbreviation
                        {PUNCT2}                                          # punctuation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 3, 2),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.4) Abbreviations that are preceded by punctuation symbols, and do not have ending punctuation;',
      'example': '(v.a',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        {PUNCT1}                              # punctuation
                        ({ABBREVIATIONS1}|{ABBREVIATIONS2})   # abbreviation
                        \s                                    # space
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 4),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
    { 'comment': 'A.5) Month name abbreviations (detect to avoid sentence breaks after month names);',
      'example': '6 dets.',
      'pattern_type': 'month_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        [0-9]\.?\s*                                     # date 
                        ((jaan|veebr?|apr|aug|sept|okt|nov|dets)\s?\.)  # month abbreviation + period
                        \s*([{LOWERCASE}]|\d\d\d\d)                     # lowercase word  or year number (sentence continues)
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 5),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
      'overlapped': True,  # switched on to detect consecutive abbreviations like : "II—I saj. e. m. a."
     },
                    ]
