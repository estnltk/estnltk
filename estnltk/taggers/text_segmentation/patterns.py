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
            # A) Abbreviations that may be affected by tokenization (split further into tokens)
            #    Note: these are longer patterns and should be checked first
            'ABBREVIATIONS1': '('+\
                               'A\s?\.\s?D|'+\
                               'a\s?\.\s?k\s?\.\s?a|'+\
                               "a['`’ ]la|"+\
                               "a/a|"+\
                               'e\s?\.\s?m\s?\.\s?a|'+\
                               'e\s?\.\s?Kr|'+\
                               'k\s?\.\s?a|'+\
                               'm\s?\.\s?a\s?\.\s?j|'+\
                               'p\s?\.\s?Kr|'+\
                               's\s?\.\s?o|'+\
                               's\s?\.\s?t|'+\
                               'v\s?\.\s?a'+\
                              ')',
            # B) Abbreviations that should come out of tokenization as they are
            #    Note: these are shorter patterns and should be checked secondly
            'ABBREVIATIONS2': '('+\
                               'a|[Dd]r|[Hh]r|[Hh]rl|[Ii]bid|[Jj]r|[Kk]od|[Kk]oost|[Ll]p|'+\
                               'lüh|[Mm]rs?|nn|[Nn]t|[Pp]r|so|st|saj|sealh|sh|[Ss]m|'+\
                               '[Tt]lk|tn|[Tt]oim|[Vv]rd|va|[Vv]t'+\
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
    { 'comment': '2.1) A generic pattern for units of measure;',
      'example': 'km / h',
      'pattern_type': 'unit',
      '_regex_pattern_': re.compile(r'''        # PATT_14
                         (^|[^{LETTERS}])       # algus või mittetäht
                         (([{LETTERS}]{1,3})    # kuni 3 tähte
                         \s?/\s?                # kaldkriips
                         ([{LETTERS}]{1,3}))    # kuni kolm tähte
                         ([^{LETTERS}]|$)       # mittetäht või lõpp
                         '''.format(**MACROS), re.X),
     '_group_': 2,
     '_priority_': (2, 1),
     'normalized': "lambda m: re.sub('\s' ,'' , m.group(2))",
    },
    { 'comment': '2.2) Degree sign + temperature unit;',
      'example': 'ºC',
      'pattern_type': 'unit',
      '_regex_pattern_': re.compile(r'''
                        ([\*º\u00B0]+\s*[CF])   # degree + temperature sign
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (2, 2),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
    },
                 ]

initial_patterns = [
    { 'comment': '3.1) Names starting with 2 initials;',
      'pattern_type': 'name',
      'example': 'A. H. Tammsaare',
      '_regex_pattern_': re.compile(r'''
                        ((?!P\.)[{UPPERCASE}][{LOWERCASE}]?)              # first initial
                        \s?\.\s?-?                                        # period (and hypen potentially)
                        ((?!S\.)[{UPPERCASE}][{LOWERCASE}]?)              # second initial
                        \s?\.\s?                                          # period
                        ((\.[{UPPERCASE}]\.)?[{UPPERCASE}][{LOWERCASE}]+) # last name
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (3, 0),
     'normalized': lambda m: re.sub('\1.\2. \3' ,'' , m.group(0)),
     },
    { 'comment': '3.2) Names starting with one initial;',
      'pattern_type': 'name',
      'example': 'A. Hein',
      '_regex_pattern_': re.compile(r'''
                        ([{UPPERCASE}])                 # first initial
                        \s?\.\s?                        # period
                        ([{UPPERCASE}][{LOWERCASE}]+)   # last name
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (3, 0),
     'normalized': lambda m: re.sub('\1. \2' ,'' , m.group(0)),
     }
                    ]

abbreviation_patterns = [
    { 'comment': '4.1) Abbreviations that end with period;',
      'example': 'sealh.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}) # abbreviation
                        \s?\.)                               # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 1, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
     },
    { 'comment': '4.2) Abbreviations not ending with period;',
      'example': 'Lp',
      'pattern_type': 'non_ending_abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS1}|{ABBREVIATIONS2})  # abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 2, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
      #'overlapped': True,
     },
    { 'comment': 'A.3) Month name abbreviations (detect to avoid sentence breaks after month names);',
      'example': '6 dets.',
      'pattern_type': 'month_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        [0-9]\.?\s*                                     # date 
                        ((jaan|veebr?|apr|aug|sept|okt|nov|dets)\s?\.)  # month abbreviation + period
                        \s*([{LOWERCASE}]|\d\d\d\d)                     # lowercase word  or year number (sentence continues)
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 3, 0),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
     },
                    ]
