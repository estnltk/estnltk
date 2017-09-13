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
            # ===================================================
            #   Non-ending abbreviations 
            #   (even if followed by a period, usually do not 
            #    end the sentence)
            # ===================================================
            # A) Abbreviations that may be affected by tokenization (split further into tokens)
            #    Note: these are longer patterns and should be checked first
            'ABBREVIATIONS1': '('+\
                               'a\s?\.\s?k\s?\.\s?a|'+\
                               "a['`’ ]la|"+\
                               'k\s?\.\s?a|'+\
                               's\s?\.\s?o|'+\
                               's\s?\.\s?t|'+\
                               'v\s?\.\s?a'+\
                              ')',
            # B) Abbreviations that should come out of tokenization as they are
            #    Note: these are shorter patterns and should be checked secondly
            'ABBREVIATIONS2': '('+\
                               '[Dd]r|[Hh]r|[Hh]rl|[Ii]bid|[Kk]od|[Kk]oost|[Ll]p|'+\
                               'lüh|[Mm]rs?|nn|[Nn]t|[Pp]r|so|st|sealh|sh|[Ss]m|'+\
                               '[Tt]lk|tn|[Tt]oim|[Vv]rd|va|[Vv]t'+\
                              ')',
            # ===================================================
            #   Other abbreviations 
            #   (can end the sentence)
            # ===================================================
            # C) Abbreviations may or may not be affected by tokenization
            #    However, patterns must be ordered by their length: longest patterns first
            'ABBREVIATIONS3': '('+\
                               'e\s?\.\s?m\s?\.\s?a|'+\
                               'm\s?\.\s?a\s?\.\s?j|'+\
                               'e\s?\.\s?Kr|'+\
                               'p\s?\.\s?Kr|'+\
                               'A\s?\.\s?D|'+\
                               'saj|'+\
                               '[Jj]r|'+\
                               'a'+\
                              ')',

         }
MACROS['LETTERS'] = MACROS['LOWERCASE'] + MACROS['UPPERCASE']
MACROS['ALPHANUM'] = MACROS['LETTERS'] + MACROS['NUMERIC']

# =================================================
#     1st level patterns
# =================================================

email_and_www_patterns = [
     # Patterns for detecting (possibly incorrectly tokenized) e-mails & www-addresses
     {'comment': '*) Pattern for detecting common e-mail formats;',
      'example': 'bla@bla.bl',
      'pattern_type': 'e-mail',
      '_group_': 1,
      '_priority_': (0, 0, 1),
      '_regex_pattern_': r'([{ALPHANUM}_.+-]+@[{ALPHANUM}-]+\.[{ALPHANUM}-.]+)'.format(**MACROS),
      'normalized': 'lambda m: None'},
      
     {'comment': '*) Pattern for detecting common e-mail formats;',
      'example': 'sambamees . siim @ pri . ee',
      'pattern_type': 'e-mail',
      '_group_': 1,
      '_priority_': (0, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         ([{ALPHANUM}_+-]+                        # first name
                         \s?\.\s?                                 # period
                         [{ALPHANUM}_+-]+                         # last name
                         \s?                                      # space possibly
                         (\[\s?-at-\s?\]|\(at\)|@)                # @
                         \s?                                      # space possibly
                         [{ALPHANUM}-]+                           # domain
                         \s?\.\s?                                 # period
                         [{ALPHANUM}_.+-]+)                       # domain
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub('\s','', m.group(1) ) },
      
      
     {'comment': '*) Pattern for detecting (possibly incorrectly tokenized) web addresses #1;',
      'example': 'http : //www.offa.org',
      'pattern_type': 'www-address',
      '_group_': 1,
      '_priority_': (0, 0, 3),
      '_regex_pattern_':  re.compile(r'''
                         (http                                    # http
                         \s*:\s*(/+)\s*                           # colon
                         www                                      # www
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_\-]+                         # domain name
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_.\-/]+                       # domain name
                         (\?\S+|\#\S+)?                           # query variables (optional)
                         )
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub('\s','', m.group(1) ) },

     {'comment': '*) Pattern for detecting (possibly incorrectly tokenized) web addresses #2;',
      'example': 'www. esindus.ee/korteriturg',
      'pattern_type': 'www-address',
      '_group_': 1,
      '_priority_': (0, 0, 4),
      '_regex_pattern_':  re.compile(r'''
                         (www                                     # www
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_\-]+                         # domain name
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_.\-/]+                       # domain name
                         (\?\S+|\#\S+)?                           # query variables (optional)
                         )
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub('\s','', m.group(1) ) },
      
            ]
            
emoticon_patterns = [
    { 'comment': '*) Aims to detect most common emoticons;',
      'example': ':=)',
      'pattern_type': 'emoticon',
      '_group_': 0,
      '_priority_': (1, 0, 1),
      '_regex_pattern_': re.compile(r'''
                         ([;:][=-]*[\)|\(ODP]+)                   # potential emoticon
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(0))"},
]

number_patterns = [
    # Heuristic date & time patterns
    # Date and time tokens should be detected before generic numerics in order to reduce
    # false positives ...
    { 'comment': '*) Date patterns in the commonly used form "dd.mm.yyyy";',
      'example': '02.02.2010',
      'pattern_type': 'numeric-date',
      '_group_': 0,
      '_priority_': (2, 0, 1),
      '_regex_pattern_': re.compile(r'''
                         (3[01]|[12][0-9]|0?[0-9])                # day
                         \s?\.\s?                                 # period
                         ([012][0-9]|1[012])                      # month
                         \s?\.\s?                                 # period
                         (1[7-9]\d\d|2[0-2]\d\d)                  # year
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Date patterns in the ISO format "yyyy-mm-dd";',
      'example': '2011-04-22',
      'pattern_type': 'numeric-date',
      '_group_': 0,
      '_priority_': (2, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         (1[7-9]\d\d|2[0-2]\d\d)                  # year
                         -                                        # hypen
                         ([012][0-9]|1[012])                      # month
                         -                                        # hypen
                         (3[01]|[12][0-9]|0?[0-9])                # day
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Date patterns in the commonly used form "dd/mm/yy";',
      'example': '19/09/11',
      'pattern_type': 'numeric-date',
      '_group_': 0,
      '_priority_': (2, 0, 3),
      '_regex_pattern_': re.compile(r'''
                         (0[0-9]|[12][0-9]|3[01])                       # day
                         /                                              # slash
                         ([012][0-9]|1[012])                            # month
                         /                                              # slash
                         (1[7-9]\d\d|2[0-2]\d\d|[7-9][0-9]|[0-3][0-9])  # year
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Time patterns in the commonly used form "HH:mm:ss";',
      'example': '21:14',
      'pattern_type': 'numeric-time',
      '_group_': 0,
      '_priority_': (2, 0, 4),
      '_regex_pattern_': re.compile(r'''
                         (0[0-9]|[12][0-9]|2[0123])               # hour
                         \s?:\s?                                  # colon
                         ([0-5][0-9])                             # minute
                         (\s?:\s?                                 # colon
                         ([0-5][0-9]))?                           # second
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s]' ,'' , m.group(0))"},
      
    # Patterns for generic numerics
    { 'comment': '*) A generic pattern for detecting long numbers (5 groups).',
      'example': '21 134 567 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 0),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\s\.]+\d+[\s\.]+\d+[\s\.]+\d+[\s\.]+\d+     # 5 groups of numbers
                         (\s,\s\d+|,\d+)?                                # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (4 groups).',
      'example': '34 567 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 1),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\s\.]+\d+[\s\.]+\d+[\s\.]+\d+       # 4 groups of numbers
                         (\s,\s\d+|,\d+)?                        # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (3 groups).',
      'example': '67 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 2),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\s\.]+\d+[\s\.]+\d+       # 3 groups of numbers
                         (\s,\s\d+|,\d+)?              # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (2 groups).',
      'example': '67 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 3),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\s\.]+\d+       # 2 groups of numbers
                         (\s,\s\d+|,\d+)?    # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (1 group).',
      'example': '12,456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 4),
      '_regex_pattern_': re.compile(r'''                             
                         \d+                    # 1 group of numbers
                         (\s,\s\d+|,\d+|\s*\.)  # + comma-separated numbers or period-ending
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub('[\s\.]' ,'' , m.group(0))"},

    # Remark on the decimal numerals (numerals with the decimal separator ','):
    #   *) form where the separator is between two spaces (' , ') is common to Koondkorpus 
    #      (which has been tokenized previously);
    #   *) form where the separator is has no spaces (',') is common to regular / untokenized 
    #      texts;
    #   *) other forms (', ' and ' ,') more likely cause false detections rather than correct
    #      numeric expressions;

    #
    # Old pattern:
    #
    # '_regex_pattern_': r'-?([{NUMERIC}][\s\.]?)+(,\s?([{NUMERIC}][\s\.]?)+)?'.format(**MACROS),
    #
    #  The old pattern was problematic, e.g. failed to detect multiple expressions like in
    #      "Hukkus umbes 90 000 inimest ja põgenes üle 70 000,"
    #

    { 'comment': '*) First 10 Roman numerals ending with period, but not ending the sentence.',
      'example': 'II. peatükis',
      'pattern_type': 'roman_numerals',
      '_group_': 2,
      '_priority_': (2, 2, 0),
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
     '_priority_': (3, 1),
     'normalized': "lambda m: re.sub('\s' ,'' , m.group(2))",
    },
                 ]

initial_patterns = [
    { 'comment': '*) Negative pattern: filters out "P.S." (post scriptum) before it is annotated as a pair of initials;',
      'pattern_type':   'negative:ps-abbreviation',  # prefix "negative:" instructs to delete this pattern afterwards
      'example': 'P. S.',
      '_regex_pattern_': re.compile(r'''
                        (P\s?.\s?S\s?.)                 # P.S. -- likely post scriptum, not initial
                        '''.format(**MACROS), re.X),
     '_group_': 1,
     '_priority_': (4, 0, 1),
     'normalized': lambda m: re.sub('\s','', m.group(1)),
     },
    { 'comment': '*) Negative pattern: filters out "degree + temperature unit" before it is annotated as an initial;',
      'pattern_type':   'negative:temperature-unit', # prefix "negative:" instructs to delete this pattern afterwards
      'example': 'ºC',
      '_regex_pattern_': re.compile(r'''
                        ([º˚\u00B0]+\s*[CF])            # degree + temperature unit -- this shouldn't be an initial
                        '''.format(**MACROS), re.X),
     '_group_': 1,
     '_priority_': (4, 0, 2),
     'normalized': lambda m: re.sub('\s','', m.group(1)),
     },
    { 'comment': '*) Names starting with 2 initials;',
      'pattern_type': 'name',
      'example': 'A. H. Tammsaare',
      '_regex_pattern_': re.compile(r'''
                        ([{UPPERCASE}][{LOWERCASE}]?)                     # first initial
                        \s?\.\s?-?                                        # period (and hypen potentially)
                        ([{UPPERCASE}][{LOWERCASE}]?)                     # second initial
                        \s?\.\s?                                          # period
                        ((\.[{UPPERCASE}]\.)?[{UPPERCASE}][{LOWERCASE}]+) # last name
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (4, 1),
     'normalized': lambda m: re.sub('\1.\2. \3' ,'' , m.group(0)),
     },
    { 'comment': '*) Names starting with one initial;',
      'pattern_type': 'name',
      'example': 'A. Hein',
      '_regex_pattern_': re.compile(r'''
                        ([{UPPERCASE}])                 # first initial
                        \s?\.\s?                        # period
                        ([{UPPERCASE}][{LOWERCASE}]+)   # last name
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (4, 2),
     'normalized': lambda m: re.sub('\1. \2' ,'' , m.group(0)),
     }
                    ]

abbreviation_patterns = [
    # --------------------------------------------------
    # 1) Abbreviations that usually do not end sentences
    # --------------------------------------------------
    { 'comment': '*) Abbreviations that end with period, and usually do not end the sentence;',
      'example': 'sealh.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}) # non-ending abbreviation
                        \s?\.)                               # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 1, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
     },
    { 'comment': '*) Abbreviations not ending with period, and usually do not end the sentence;',
      'example': 'Lp',
      'pattern_type': 'non_ending_abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS1}|{ABBREVIATIONS2})  # non-ending abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 2, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
      #'overlapped': True,
     },
    { 'comment': '*) Month name abbreviations (detect to avoid sentence breaks after month names);',
      'example': '6 dets.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        [0-9]\.?\s*                                                                         # date 
                        (([Jj]aan|[Vv]eebr?|Mär|[Aa]pr|Jun|Jul|[Aa]ug|[Ss]ept|[Oo]kt|[Nn]ov|[Dd]ets)\s?\.)  # month abbreviation + period
                        \s*([{LOWERCASE}]|\d\d\d\d)                                                         # lowercase word  or year number (sentence continues)
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 3, 0),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
     },
    # --------------------------------------------------
    # 2) Abbreviations that can end sentences
    # --------------------------------------------------
    { 'comment': '*) Abbreviations that end with period, and that can end the sentence;',
      'example': 'p.Kr.',
      'pattern_type': 'abbreviation',
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS3}          # abbreviation
                        \s?\.)                     # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 4, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
     },
    { 'comment': '*) Abbreviations not ending with period, and that can end the sentence;',
      'example': 'saj',
      'pattern_type': 'abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS3})         # abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 5, 0),
      'normalized': "lambda m: re.sub('\.\s','.', re.sub('\s\.','.', m.group(1)))",
      #'overlapped': True,
     },
    { 'comment': '*) Abbreviations of type <uppercase letter> + <numbers>;',
      'example': 'E 251',
      'pattern_type': 'abbreviation',
      '_regex_pattern_': re.compile(r'''
                        ([{UPPERCASE}]        # uppercase letter
                        (\s|\s?-\s?)          # space or hypen
                        [0-9]+)               # numbers
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 6, 0),
      'normalized': "lambda m: re.sub('\s' ,'' , m.group(1))",
     },
                    ]

# =================================================
#     2nd level patterns
# =================================================
case_endings_patterns = [

    # (38)
    # four:   -isse, -lise, -line
    # three:  -iks, -ile, -ilt, -iga, -ist, -sse, -ide, -ina, -ini, -ita
    # two:    -il, -it, -le, -lt, -ga, -st, -is, -ni, -na, -id, -ed, -ta, -te, -ks, -se, -ne, -es
    # one:    -i, -l, -s, -d, -u, -e, -t,
    
    { 'comment': '*) Words and their separated case endings;',
      'example': 'LinkedIn -ist',
      'pattern_type': 'case_ending',
      'left_strict': False,   # left side is loose, e.g can be in the middle of a token
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                        ([{ALPHANUM}]                                                    # word or number
                        [.%"]?                                                           # possible punctuation
                        \s?                                                              # potential space
                        [\-\'′’´]                                                        # separator character
                        \s?                                                              # potential space
                        (isse|li[sn]e|list|                                              # case ending
                         iks|ile|ilt|iga|ist|sse|ide|ina|ini|ita|                        # case ending
                         il|it|le|lt|ga|st|is|ni|na|id|ed|ta|te|ks|se|ne|es|             # case ending
                         i|l|s|d|u|e|t))                                                 # case ending
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 1),
      'normalized': "lambda m: re.sub('\s','',  m.group(1))",
     },
    { 'comment': '*) Numeric + "%" or "." + separated case ending;',
      'example': '20%ni',
      'pattern_type': 'case_ending',
      'left_strict': False,   # left side is loose, e.g can be in the middle of a token
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                        ([{NUMERIC}]                                                    # word or number
                        \s?                                                             # potential space
                        [.%]                                                            # % or .
                        \s?                                                             # potential space
                        (isse|li[sn]e|list|                                             # case ending
                         iks|ile|ilt|iga|ist|sse|ide|ina|ini|ita|                       # case ending
                         il|it|le|lt|ga|st|is|ni|na|id|ed|ta|te|ks|se|ne|es|            # case ending
                         i|l|s|d|u|e|t))                                                # case ending
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 2),
      'normalized': "lambda m: re.sub('\s','',  m.group(1))",
     },
                    ]

number_fixes_patterns = [
    { 'comment': '*) Add sign (+ or -) to the number;',
      'example': '-20,5',
      'pattern_type': 'sign',
      'left_strict':  True, 
      'right_strict': False,
      '_regex_pattern_': re.compile(r'''
                        (^|[^{NUMERIC}. ])                         # beginning or (not number, period nor space)
                        \s*                                        # potential space
                        ((\+/-|[\-+±–])                            # + or -
                        [{NUMERIC}])                               # number
                        '''.format(**MACROS), re.X),
      '_group_': 2,
      '_priority_': (7, 0, 1),
      'normalized': "lambda m: re.sub('\s','',  m.group(2))",
     },
    { 'comment': '*) Add sign % to the number;',
      'example': '-20,5%',
      'pattern_type': 'percentage',
      'left_strict':  False, 
      'right_strict': True,
      '_regex_pattern_': re.compile(r'''
                        ([{NUMERIC}]                     # number
                        \s*                              # potential space
                        (-protsendi[^\s]+|%))            # percentage sgn or word
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (7, 0, 2),
      'normalized': "lambda m: re.sub('\s','',  m.group(1))",
     },
                    ]