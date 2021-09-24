import regex as re

"""
This is a vocabulary file for two tokenization hint taggers of 
the CompoundTokenTagger. The entries here are lists of records in 
RegexTagger vocabulary format.

In 1st level patterns, each record must contain keywords 
'_regex_pattern_', 'pattern_type' and 'normalized'. 

In 2nd level patterns, each record must contain keywords
'_regex_pattern_', 'pattern_type', 'normalized', 'left_strict', 
'right_strict'. 

The names of the entries need to be declared in CompoundTokenTagger.
"""


MACROS = {
            # ===================================================
            #   Primitives
            # ===================================================
            'LOWERCASE': 'a-zšžõäöü',
            'UPPERCASE': 'A-ZŠŽÕÄÖÜ',
            'NUMERIC': '0-9',
            '1,3': '{1,3}',
            '1,2': '{1,2}',
            '2,': '{2,}',
            '1,25': '{1,25}',
            # ===================================================
            #   Non-ending abbreviations 
            #   (even if followed by a period, usually do not 
            #    end the sentence)
            # ===================================================
            # A) Abbreviations that may be affected by tokenization (split further into tokens)
            #    Note: these are longer patterns and should be checked first
            'ABBREVIATIONS1': '('+\
                               r'a\s?\.\s?k\s?\.\s?a|'+\
                               r'n\s?\.\s?-\s?ö|'+\
                               "a['`’ ]la|"+\
                               r'k\s?\.\s?a|'+\
                               r'n\s?\.\s?ö|'+\
                               r'n\s?\.\s?n|'+\
                               r's\s?\.\s?o|'+\
                               r's\s?\.\s?t|'+\
                               r's\s?\.\s?h|'+\
                               r'v\s?\.\s?a'+\
                              ')',
            # B) Abbreviations that should come out of tokenization as they are
            #    Note: these are shorter patterns and should be checked secondly
            'ABBREVIATIONS2': '('+\
                               'ca|[Dd]r|[Hh]r|[Hh]rl|[Ii]bid|[Kk]od|[Kk]oost|[Ll]p|'+\
                               'lüh|[Mm]rs?|nn|[Nn]r|[Nn]t|nö|[Pp]r|sealh|so|st|sh|'+\
                               '[Ss]m|[Tt]lk|tn|[Tt]oim|[Vv]rd|va|[Vv]t'+\
                              ')',
            # ===================================================
            #   Other abbreviations 
            #   (can end the sentence)
            # ===================================================
            # C) Abbreviations may or may not be affected by tokenization
            #    However, patterns must be ordered by their length: longest patterns first
            # C.1) Patterns that will be checked for ending period 
            #      (so we can allow a single letter pattern)
            'ABBREVIATIONS3A': '('+\
                               r'e\s?\.\s?m\s?\.\s?a|'+\
                               r'm\s?\.\s?a\s?\.\s?j|'+\
                               r'e\s?\.\s?Kr|'+\
                               r'p\s?\.\s?Kr|'+\
                               r'A\s?\.\s?D|'+\
                               r'õ\s?\.\s?a|'+\
                               'saj|'+\
                               '[Jj]r|'+\
                               'j[mt]|'+\
                               'a|'+\
                               'u'+\
                              ')',
            # C.2) Patterns that won't be checked for ending period
            #      (single letter patterns disallowed)
            'ABBREVIATIONS3B': '('+\
                               r'e\s?\.\s?m\s?\.\s?a|'+\
                               r'm\s?\.\s?a\s?\.\s?j|'+\
                               r'e\s?\.\s?Kr|'+\
                               r'p\s?\.\s?Kr|'+\
                               r'A\s?\.\s?D|'+\
                               r'õ\s?\.\s?a|'+\
                               'saj|'+\
                               '[Jj]r|'+\
                               'j[mt]'+\
                              ')',
            # Note: distinguishing between C.1 and C.2 provides a major 
            #       optimization for processing speed
            # ===================================================
            # Common unit combinations
            # ===================================================
            'UNITS': '('+\
                        r'l\s?/\s?(min|sek)|'+\
                        r'm\s?/\s?(min|sek|[st])|'+\
                        r'km\s?/\s?[hst]'+\
                       ')',
         }
MACROS['LETTERS'] = MACROS['LOWERCASE'] + MACROS['UPPERCASE']
MACROS['ALPHANUM'] = MACROS['LETTERS'] + MACROS['NUMERIC']

# =================================================
#     1st level patterns
#     ("strict tokenization hints")
# =================================================

xml_patterns = [
    # Note: XML tags should be detected before www and email addresses,
    #        because XML tags can contain www and email addresses
    { 'comment': '*) Detect XML tags from the text (content limit: max 25 characters);',
      'example': '<p>',
      'pattern_type': 'xml_tag',
      '_group_': 0,
      '_priority_': (0, 0, 0, 1),
      '_regex_pattern_': re.compile(r'''
                         (<[^<>]{1,25}?>)                         # an xml tag
                         '''.format(**MACROS), re.X),
      'normalized': 'lambda m: None'},
    { 'comment': '*) Detect XML tags from the text (no content limit, but must include =");',
      'example': '<a href=”http://sait.ee/” rel=”nofollow”>',
      'pattern_type': 'xml_tag',
      '_group_': 0,
      '_priority_': (0, 0, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         (<[^<>]+?=["”][^<>]+?>)                  # an xml tag
                         '''.format(**MACROS), re.X),
      'normalized': 'lambda m: None'},
]

email_and_www_patterns = [
     # Patterns for detecting (possibly incorrectly tokenized) e-mails & www-addresses
     {'comment': '*) Pattern for detecting common e-mail formats;',
      'example': 'bla@bla.bl',
      'pattern_type': 'email',
      '_group_': 1,
      '_priority_': (0, 0, 1),
      '_regex_pattern_': re.compile(r'''
                            ([{ALPHANUM}_.+-]+                 # name
                             (\(at\)|\[at\]|@)                 # @
                             [{ALPHANUM}-]+\.[{ALPHANUM}-.]+)  # domain
                          '''.format(**MACROS), re.X),
      'normalized': 'lambda m: None'},
      
     {'comment': '*) Pattern for detecting common e-mail formats;',
      'example': 'sambamees . siim @ pri . ee',
      'pattern_type': 'email',
      '_group_': 1,
      '_priority_': (0, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         ([{ALPHANUM}_+-]+                        # first name
                         \s?\.\s?                                 # period
                         [{ALPHANUM}_+-]+                         # last name
                         \s?                                      # space possibly
                         (\[\s?-at-\s?\]|\(at\)|\[at\]|@)         # @
                         \s?                                      # space possibly
                         [{ALPHANUM}-]+                           # domain
                         \s?\.\s?                                 # period
                         [{ALPHANUM}_.+-]+)                       # domain
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub(r'\s','', m.group(1) ) },
      
      
     {'comment': '*) Pattern for detecting (possibly incorrectly tokenized) web addresses #1;',
      'example': 'http : //www.offa.org',
      'pattern_type': 'www_address',
      '_group_': 1,
      '_priority_': (0, 0, 3),
      '_regex_pattern_':  re.compile(r'''
                         (https?                                  # http
                         \s*:\s*(/+)\s*                           # colon + //
                         www[2-6]?                                # www (or www2, www3 etc.)
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_\-]+                         # domain name
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_.\-/]+                       # domain name
                         (\?\S+|\#\S+)?                           # query variables (optional)
                         )
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub(r'\s','', m.group(1) ) },
      
     {'comment': '*) Pattern for detecting (possibly incorrectly tokenized) web addresses #2;',
      'example': 'http://f6.pmo.ee',
      'pattern_type': 'www_address',
      '_group_': 1,
      '_priority_': (0, 0, 4),
      '_regex_pattern_':  re.compile(r'''
                         (https?                                  # http
                         \s*:\s*(/+)\s*                           # colon + //
                         [{ALPHANUM}_\-]+                         # domain name
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_.\-/]+                       # domain name
                         (\?\S+|\#\S+)?                           # query variables (optional)
                         )
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub(r'\s','', m.group(1) ) },

     {'comment': '*) Pattern for detecting (possibly incorrectly tokenized) web addresses #3;',
      'example': 'www. esindus.ee/korteriturg',
      'pattern_type': 'www_address',
      '_group_': 1,
      '_priority_': (0, 0, 5),
      '_regex_pattern_':  re.compile(r'''
                         (www[2-6]?                               # www (or www2, www3 etc.)
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_\-]+                         # domain name
                         \s*\.\s*                                 # period
                         [{ALPHANUM}_.\-/]+                       # domain name
                         (\?\S+|\#\S+)?                           # query variables (optional)
                         )
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub(r'\s','', m.group(1) ) },
      
     {'comment': '*) Pattern for detecting short web addresses (without prefixes "http" and "www");',
      'example': 'Postimees.ee',
      'pattern_type': 'www_address_short',
      '_group_': 2,
      '_priority_': (0, 0, 6),
      '_regex_pattern_':  re.compile(r'''
                         (^|[^{ALPHANUM}])                               # beginning or non-alphanum
                         (
                         [{ALPHANUM}_\-.]+                               # domain name
                         (\s\.\s|\.)                                     # period
                         (ee|org|edu|com|uk|ru|fi|lv|lt|eu|se|nl|de|dk)  # top-level domain
                         )
                         ([^{ALPHANUM}]|$)                               # non-alphanum or ending
                         '''.format(**MACROS), re.X),
      'normalized': lambda m: re.sub(r'\s','', m.group(2) ) },

            ]

emoticon_patterns = [
    # Pattern for detecting common emoticons: initial version created by Tarmo Vaino
    { 'comment': '*) Aims to detect most common emoticons #1;',
      'example': ':=)',
      'pattern_type': 'emoticon',
      '_group_': 0,
      '_priority_': (1, 0, 1),
      '_regex_pattern_': re.compile(r'''
                         ([;:][=-]*[\)|\(ODP]+)                   # potential emoticon
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
    # Patterns for emoticons in etTenTen: initial versions created by Kristiina Vaik
    { 'comment': '*) Aims to detect most common emoticons #2;',
      'example': ':-S',
      'pattern_type': 'emoticon',
      '_group_': 2,
      '_priority_': (1, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         (\s)
                         (:-?[Ss]|:S:S:S)                         # potential emoticon
                         (\s)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
    { 'comment': '*) Aims to detect most common emoticons #3;',
      'example': ':-o',
      'pattern_type': 'emoticon',
      '_group_': 2,
      '_priority_': (1, 0, 3),
      '_regex_pattern_': re.compile(r'''
                         (\s)
                         ([:;][-']+[(\[/*o9]+)                    # potential emoticon
                         (\s)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
    { 'comment': '*) Aims to detect most common emoticons #4;',
      'example': ':o )',
      'pattern_type': 'emoticon',
      '_group_': 2,
      '_priority_': (1, 0, 4),
      '_regex_pattern_': re.compile(r'''
                         (\s)((=|:-|[;:]o)\s\)(\s\))*)(\s)        # potential emoticon
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
    { 'comment': '*) Aims to detect most common emoticons #5;',
      'example': ':// ?',
      'pattern_type': 'emoticon',
      '_group_': 2,
      '_priority_': (1, 0, 5),
      '_regex_pattern_': re.compile(r'''
                         ((?<!https?)\s)
                         ([:;][\[/\]@o]+)                         # potential emoticon
                         (\s)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
    { 'comment': '*) Aims to detect most common emoticons #6;',
      'example': ': D',
      'pattern_type': 'emoticon',
      '_group_': 2,
      '_priority_': (1, 0, 6),
      '_regex_pattern_': re.compile(r'''
                         (\s)
                         ([:;]\sD)                               # potential emoticon
                         (\s)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
    { 'comment': '*) Aims to detect most common emoticons #7;',
      'example': ':K',
      'pattern_type': 'emoticon',
      '_group_': 1,
      '_priority_': (1, 0, 7),
      '_regex_pattern_': re.compile(r'''
                         (:[KL])                                 # potential emoticon
                         (\s)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(1))"},
]

hashtag_and_username_patterns = [
    # Pattern for detecting Twitter-style hashtags
    { 'comment': '*) detect Twitter-style hashtags. Note: the pattern is a simplification;',
      'example': '#eestilaul #superstaar #goalz',
      'pattern_type': 'hashtag',
      '_group_': 0,
      '_priority_': (1, 0, 8),
      '_regex_pattern_': re.compile(r'''
                         (\#[{ALPHANUM}_]+)          # potential hashtag
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
    # Pattern for detecting Twitter-style username mentions
    { 'comment': '*) detect Twitter-style username mentions. Note: the pattern is a simplification;',
      'example': 'RT @polaaarkaru',
      'pattern_type': 'username_mention',
      '_group_': 0,
      '_priority_': (1, 0, 9),
      '_regex_pattern_': re.compile(r'''
                         (@[{ALPHANUM}_]+)           # potential user name mention
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
]

_month_period_year_pattern = re.compile(r'^([012][0-9]|1[012])\.(1[7-9]\d\d|2[0-2]\d\d)$')
_day_period_month_pattern  = re.compile(r'^(3[01]|[12][0-9]|0?[0-9])\.([012][0-9]|1[012])$')

def _numeric_with_period_normalizer(m):
    ''' Normalizes numerics with periods, but makes additional checkups beforehand: 
        if the numeric string looks suspiciously like month + year (e.g. '03.2003') 
        or like day+month (e.g. '31.01'), then periods will not be deleted from 
        the string. Otherwise, all periods will be deleted from the string. '''
    if _month_period_year_pattern.match(m.group(0)) or \
       _day_period_month_pattern.match(m.group(0)):
        # The number looks suspiciously like a part of date: do not delete the period
        return m.group(0)
    return re.sub(r'[\.]', '', m.group(0))


number_patterns = [
    # Heuristic date & time patterns
    # Date and time tokens should be detected before generic numerics in order to reduce
    # false positives ...
    { 'comment': '*) Date patterns in the commonly used form "dd.mm.yyyy";',
      'example': '02.02.2010',
      'pattern_type': 'numeric_date',
      '_group_': 0,
      '_priority_': (2, 0, 1),
      '_regex_pattern_': re.compile(r'''
                         (3[01]|[12][0-9]|0?[0-9])                # day
                         \s?\.\s?                                 # period
                         ([012][0-9]|1[012])                      # month
                         \s?\.\s?                                 # period
                         (1[7-9]\d\d|2[0-2]\d\d)                  # year
                         a?                                       # a (optional)
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Date patterns in the ISO format "yyyy-mm-dd";',
      'example': '2011-04-22',
      'pattern_type': 'numeric_date',
      '_group_': 0,
      '_priority_': (2, 0, 2),
      '_regex_pattern_': re.compile(r'''
                         (1[7-9]\d\d|2[0-2]\d\d)                  # year
                         -                                        # hypen
                         ([012][0-9]|1[012])                      # month
                         -                                        # hypen
                         (3[01]|[12][0-9]|0?[0-9])                # day
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Date patterns in the commonly used form "dd/mm/yy";',
      'example': '19/09/11',
      'pattern_type': 'numeric_date',
      '_group_': 0,
      '_priority_': (2, 0, 3, 1),
      '_regex_pattern_': re.compile(r'''
                         (0[0-9]|[12][0-9]|3[01])                       # day
                         /                                              # slash
                         ([012][0-9]|1[012])                            # month
                         /                                              # slash
                         (1[7-9]\d\d|2[0-2]\d\d|[7-9][0-9]|[0-3][0-9])  # year
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
    { 'comment': '*) Date patterns that contain month as a Roman numeral: "dd. roman_mm yyyy";',
      'example': '26. XII 1933',
      'pattern_type': 'numeric_date',
      '_group_': 0,
      '_priority_': (2, 0, 3, 2),
      '_regex_pattern_': re.compile(r'''
                         (0[0-9]|[12][0-9]|3[01])                       # day
                         \.                                             # period
                         \s+                                            # space(s)
                         (I{1,3}|IV|V|VI{1,3}|I{1,2}X|X|XI{1,2})        # roman month
                         \s+                                            # space(s)
                         (1[7-9]\d\d|2[0-2]\d\d)                        # year
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'\s{2,}',' ', m.group(0))"},
    { 'comment': '*) Time patterns in the commonly used form "HH:mm:ss";',
      'example': '21:14',
      'pattern_type': 'numeric_time',
      '_group_': 0,
      '_priority_': (2, 0, 4),
      '_regex_pattern_': re.compile(r'''
                         (0[0-9]|[12][0-9]|2[0123])               # hour
                         \s?:\s?                                  # colon
                         ([0-5][0-9])                             # minute
                         (\s?:\s?                                 # colon
                         ([0-5][0-9]))?                           # second
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},
      
    # Patterns for generic numerics
    { 'comment': '*) A generic pattern for detecting long numbers (5 groups).',
      'example': '21 134 567 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 0),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\ \.]+\d+[\ \.]+\d+[\ \.]+\d+[\ \.]+\d+     # 5 groups of numbers
                         (\ ,\ \d+|,\d+)?                                # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (4 groups).',
      'example': '34 567 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 1),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\ \.]+\d+[\ \.]+\d+[\ \.]+\d+       # 4 groups of numbers
                         (\ ,\ \d+|,\d+)?                        # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))"},
    { 'comment': '*) A generic pattern for detecting long numbers (3 groups).',
      'example': '67 000 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 2),
      '_regex_pattern_': re.compile(r'''                             
                         \d+[\ \.]+\d+[\ \.]+\d+       # 3 groups of numbers
                         (\ ,\ \d+|,\d+)?              # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))"},

    { 'comment': '*) A generic pattern for detecting long numbers (2 groups, point-separated, followed by comma-separated numbers).',
      'example': '67.123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 3, 1),
      '_regex_pattern_': re.compile(r'''
                         \d+\.+\d+           # 2 groups of numbers
                         (\ ,\ \d+|,\d+)     # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s\.]' ,'' , m.group(0))" },
    { 'comment': '*) A generic pattern for detecting long numbers (2 groups, point-separated, without following comma-separated numbers).',
      'example': '67.123',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 3, 2),
      '_regex_pattern_': re.compile(r'''
                         \d+\.+\d+           # 2 groups of numbers
                         '''.format(**MACROS), re.X),
      # Note: we do not delete '.' here, because that would harm 
      #   date/time expressions (such as '03.2003' or '31.12') and price expressions (such as '4.50', '3.25')'
      'normalized': 'lambda m: None' },

    { 'comment': '*) A generic pattern for detecting long numbers (2 groups, space-separated).',
      'example': '67 123 , 456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 4),
      '_regex_pattern_': re.compile(r'''
                         \d+\ +\d\d\d+       # 2 groups of numbers
                         (\ ,\ \d+|,\d+)?    # + comma-separated numbers
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},

    { 'comment': '*) A generic pattern for detecting long numbers (1 group).',
      'example': '12,456',
      'pattern_type': 'numeric',
      '_group_': 0,
      '_priority_': (2, 1, 5),
      '_regex_pattern_': re.compile(r'''                             
                         \d+                    # 1 group of numbers
                         (\ ,\ \d+|,\d+|\ *\.)  # + comma-separated numbers or period-ending
                         '''.format(**MACROS), re.X),
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(0))"},

    # Remark on the decimal numerals (numerals with the decimal separator ','):
    #   *) form where the separator is between two spaces (' , ') is common to Koondkorpus 
    #      (which has been tokenized previously);
    #   *) form where the separator has no spaces (',') is common to regular / untokenized 
    #      texts;
    #   *) other forms (', ' and ' ,') more likely cause false detections rather than correct
    #      numeric expressions;

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
      'normalized': r"lambda m: re.sub(r'[\s]' ,'' , m.group(2))"},
              ]

unit_patterns = [
    { 'comment': '2.1) A generic pattern for units of measure preceded by quantities;',
      'example': '30 km / h',
      'pattern_type': 'unit',
      '_regex_pattern_': re.compile(r'''
                         ([0-9])                # number
                         \s*                    # potential space
                         (([{LETTERS}]{1,3})    # up to 3 letters
                         \s?/\s?                # slash
                         ([{LETTERS}]{1,3}))    # up to 3 letters
                         '''.format(**MACROS), re.X),
     '_group_': 2,
     '_priority_': (3, 1),
     'normalized': r"lambda m: re.sub(r'\s' ,'' , m.group(2))",
    },
    { 'comment': '2.2) A pattern for capturing specific units of measure;',
      'example': 'km / h',
      'pattern_type': 'unit',
      '_regex_pattern_': re.compile(r'''
                         (^|[^{LETTERS}])       # beginning or non-letter
                         ({UNITS})              # common unit combinations
                         ([^{LETTERS}]|$)       # end or non-letter
                         '''.format(**MACROS), re.X),
     '_group_': 2,
     '_priority_': (3, 2),
     'normalized': r"lambda m: re.sub(r'\s' ,'' , m.group(2))",
    },
                 ]

abbreviations_before_initials_patterns = [
    # --------------------------------------------------
    #  Abbreviations that usually do not end sentences,
    #  and that need to be captured BEFORE capturing
    #  names with initials (to prevent a mix-up)
    # --------------------------------------------------
    { 'comment': '*) P.S. (post scriptum) abbreviation -- needs to be captured before name with initials;',
      'example': 'P.S.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        ((P\s?\.\s?P\s?\.\s?S|P\s?\.\s?S)   # non-ending abbreviation
                         \s?\.)                             # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 0, 0, 1),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
     },
    { 'comment': '*) P.S (post scriptum) abbreviation -- needs to be captured before name with initials;',
      'example': 'P.S',
      'pattern_type': 'non_ending_abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        (P\s?\.\s?P\s?\.\s?S|P\s?\.\s?S)    # non-ending abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (4, 0, 0, 2),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
     },
]

initial_patterns = [
    { 'comment': '*) Negative pattern: filters out "degree + temperature unit" before it is annotated as an initial;',
      'pattern_type':   'negative:temperature_unit', # prefix "negative:" instructs to delete this pattern afterwards
      'example': 'ºC',
      '_regex_pattern_': re.compile(r'''
                        ([º˚\u00B0]+\s*[CF])            # degree + temperature unit -- this shouldn't be an initial
                        '''.format(**MACROS), re.X),
     '_group_': 1,
     '_priority_': (4, 0, 1),
     'normalized': lambda m: re.sub(r'\s','', m.group(1)),
     },
    { 'comment': '*) Names starting with 2 initials;',
      'pattern_type': 'name_with_initial',
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
     'normalized': lambda m: re.sub('\1.\2. \3', '', m.group(0)),
     },
    { 'comment': '*) Names starting with one initial;',
      'pattern_type': 'name_with_initial',
      'example': 'A. Hein',
      '_regex_pattern_': re.compile(r'''
                        ([{UPPERCASE}])                 # first initial
                        \s?\.\s?                        # period
                        ([{UPPERCASE}][{LOWERCASE}]+)   # last name
                        '''.format(**MACROS), re.X),
     '_group_': 0,
     '_priority_': (4, 2),
     'normalized': lambda m: re.sub('\1. \2', '', m.group(0)),
     }
                    ]

abbreviation_patterns = [
    # --------------------------------------------------
    # 1) Abbreviations that usually do not end sentences
    # --------------------------------------------------
    { 'comment': '*) Month name abbreviations (detect to avoid sentence breaks after month names);',
      'example': '6 dets.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        [0-9]\.?\s*                                                                         # date 
                        (([Jj]aan|[Vv]eebr?|Mär|[Aa]pr|Jun|Jul|[Aa]ug|[Ss]ept|[Oo]kt|[Nn]ov|[Dd]ets)\s?\.)  # month abbreviation + period
                        \s*([{LOWERCASE}]|\d\d\d\d)                                                         # lowercase word  or year number (sentence continues)
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 1, 0),
      'normalized': r"lambda m: re.sub(r'\s' ,'' , m.group(1))",
     },
    { 'comment': '*) Abbreviations that end with period, and usually do not end the sentence;',
      'example': 'sealh.',
      'pattern_type': 'non_ending_abbreviation',
      '_regex_pattern_': re.compile(r'''
                        (({ABBREVIATIONS1}|{ABBREVIATIONS2}) # non-ending abbreviation
                        \s?\.)                               # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 2, 0),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
     },
    { 'comment': '*) Abbreviations not ending with period, and usually do not end the sentence;',
      'example': 'Lp',
      'pattern_type': 'non_ending_abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS1}|{ABBREVIATIONS2})  # non-ending abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 3, 0),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
      #'overlapped': True,
     },
    # --------------------------------------------------
    # 2) Abbreviations that can end sentences
    # --------------------------------------------------
    { 'comment': '*) Abbreviations that end with period, and that can end the sentence;',
      'example': 'p.Kr.',
      'pattern_type': 'abbreviation',
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS3A}          # abbreviation
                        \s?\.)                      # period
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 4, 0),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
     },
    { 'comment': '*) Abbreviations not ending with period, and that can end the sentence;',
      'example': 'saj',
      'pattern_type': 'abbreviation', 
      '_regex_pattern_': re.compile(r'''
                        ({ABBREVIATIONS3B})         # abbreviation
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (5, 5, 0),
      'normalized': r"lambda m: re.sub(r'\.\s','.', re.sub(r'\s\.','.', m.group(1)))",
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
      'normalized': r"lambda m: re.sub(r'\s' ,'' , m.group(1))",
     },
                    ]

# =================================================
#     2nd level patterns
#     ("non-strict tokenization hints")
# =================================================
case_endings_patterns = [

    # (38)
    # four:   -isse, -lise, -line
    # three:  -iks, -ile, -ilt, -iga, -ist, -sse, -ide, -ina, -ini, -ita
    # two:    -il, -it, -le, -lt, -ga, -st, -is, -ni, -na, -id, -ed, -ta, -te, -ks, -se, -ne, -es
    # one:    -i, -l, -s, -d, -u, -e, -t,
    { 'comment': '*) Words and their separated case endings (one separating space at maximum);',
      'example': 'LinkedIn -ist',
      'pattern_type': 'case_ending',
      'left_strict': False,   # left side is loose, e.g can be in the middle of a token
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                        ([{ALPHANUM}]                                                    # word or number
                        [.%"]?                                                           # possible punctuation
                        (\s[\-\'′’´]|                                                    # left space + separator character
                         [\-\'′’´]\s|                                                    # right space + separator character
                         [\-\'′’´`])                                                     # separator character alone
                        (isse|li[sn]e|list|                                              # case ending
                         iks|ile|ilt|iga|ist|sse|ide|ina|ini|ita|                        # case ending
                         il|it|le|lt|ga|st|is|ni|na|id|ed|ta|te|ks|se|ne|es|             # case ending
                         i|l|s|d|u|e|t))                                                 # case ending
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 1),
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
     },
    { 'comment': '*) Words and their separated case endings (the special case of two separating spaces);',
      'example': "workshop ' e",
      'pattern_type': 'case_ending',
      'left_strict': False,   # left side is loose, e.g can be in the middle of a token
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                        ([{ALPHANUM}]                                                    # word or number
                        [.%"]?                                                           # possible punctuation
                        (\s[\'′’´`]\s)                                                   # non-dash between spaces as separator character
                        (isse|li[sn]e|list|                                              # case ending
                         iks|ile|ilt|iga|ist|sse|ide|ina|ini|ita|                        # case ending
                         il|it|le|lt|ga|st|is|ni|na|id|ed|ta|te|ks|se|ne|es|             # case ending
                         i|l|s|d|u|e|t))                                                 # case ending
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 2),
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
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
                        ([^{ALPHANUM}]|$)                                               # avoid continuation of a word
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 3),
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
     },
    { 'comment': '*) Numeric with case ending (case ending not separated);',
      'example': '18.20ni',
      'pattern_type': 'case_ending',
      'left_strict':  True,   # left side is strict: must match exactly with token's ending
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                       ([{NUMERIC}]+                                        # number
                        [.,]                                                # period/comma
                        [{NUMERIC}]+                                        # number
                        (ks|le|lt|ga|st|sse|na|ni|ta|l|t|ne|es|             # case ending
                         i|l|s|d|u|e|t))                                    # case ending
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 4),
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
     },
    { 'comment': '*) Numeric (year/decade) + ".-" + separated case ending;',
      'example': '1990.-ndatel',
      'pattern_type': 'case_ending',
      'left_strict': False,   # left side is loose, e.g can be in the middle of a token
      'right_strict': True,   # right side is strict: must match exactly with token's ending
      '_regex_pattern_': re.compile(r'''
                        ([{NUMERIC}]                                                    # word or number
                        \s?                                                             # potential space
                        ([.]\s?-|-|[.])                                                 # .- or - or .
                        \s?                                                             # potential space
                        nda                                                             # 'nda'
                        (tesse|teks|teni|test|tena|tele|telt|tega|isse|                 # case ending
                         iks|ile|ilt|ist|sse|ina|ini|ita|tel|tes|                       # case ending
                         il|le|lt|ga|st|is|ni|na|id|ta|te|ks|                           # case ending
                         l|s|d|t)?)                                                     # case ending
                        ([^{ALPHANUM}]|$)                                               # avoid continuation of a word
                        '''.format(**MACROS), re.X),
      '_group_': 1,
      '_priority_': (6, 0, 5),
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
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
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(2))",
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
      'normalized': r"lambda m: re.sub(r'\s','',  m.group(1))",
     },
                    ]