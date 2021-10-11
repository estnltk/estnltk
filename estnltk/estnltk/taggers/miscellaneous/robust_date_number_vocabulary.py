import regex as re

substitutions = {
    'LONGYEAR': r'(?P<LONGYEAR>((19[0-9]{2})|(20[0-9]{2})))',
    'YEAR':         r'(?P<YEAR>((19[0-9]{2})|(20[0-9]{2})|([0-9]{2})))',
    'MONTH': r'(?P<MONTH>(0?[1-9]|1[0-2]))',
    'DAY':     r'(?P<DAY>(0?[1-9]|[12][0-9]|3[01]))',
    'HOUR':     r'(?P<hour>[0-2][0-9])',
    'MINUTE': r'(?P<minute>[0-5][0-9])',
    'SECOND': r'(?P<second>[0-5][0-9])'}


vocabulary = [
{'grammar_symbol': 'NUMBER',
 'regex_type': 'anynumber',
 '_regex_pattern_': r'(^|[^0-9,.])([0-9]+(\s?[,.]\s?[0-9]+)?)',
 '_group_': 2,
 '_priority_': 1,
 '_validator_': lambda m: True,
 'value': lambda m: re.sub(r'\s?[.,]\s?','.', m.group(2))},

{'grammar_symbol': 'NUMBER',
 'regex_type': 'int',
 '_regex_pattern_': r'(^|[^0-9,.])([0-9]+)',
 '_group_': 2,
 '_priority_': 2,
 '_validator_': lambda m: True,
 'value': 'some_int'},

{'grammar_symbol': 'NUMBER',
 'regex_type': 'commanumber',
 '_regex_pattern_': r'\s[,.][0-9]+',
 '_group_': 0,
 '_priority_': 1,
 '_validator_': lambda m: True,
 'value': 'why'},

{'grammar_symbol': 'NUMBER',
 'regex_type': 'numbercomma',
 '_regex_pattern_': r'(^|[^0-9,.])([0-9]+\s?[,.]\s)',
 '_group_': 2,
 '_priority_': 1,
 '_validator_': lambda m: True,
 'value': 'why'},

{'grammar_symbol': 'DATENUM',
 'regex_type': 'datenum',
 '_regex_pattern_': r'((19[0-9]{2})|(20[0-9]{2}))[.]?([0-9]+(\s?[,.]\s?[0-9]+)?)',
 '_group_': 4,
 '_priority_': -2,
 '_validator_': lambda m: True ,
 'value': 'date_and_num'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date1',
 '_regex_pattern_': r'k(el)?l\s{HOUR}[.:]{MINUTE}(:{SECOND})?'.format(**substitutions),
 '_group_': 0,
 '_priority_': 2,
 '_validator_': lambda m: True,
 'value': 'time'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date2',
 '_regex_pattern_':
  r'{DAY}\.?\s*{MONTH}\.?\s*{YEAR}\s*{HOUR}[.:]{MINUTE}(:{SECOND})?'.format(**substitutions),
 '_group_': 0,
 '_priority_': 2,
 '_validator_': lambda m: True,
 'value': 'date_time'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date3',
 '_regex_pattern_':
 r'{DAY}\.?\s*{MONTH}\.?\s*{YEAR}[.a ]+\s*k(el)?l\.*\s*{HOUR}[.:]{MINUTE}(:{SECOND})?'.format(**substitutions),
 '_group_': 0,
 '_priority_': 2,
 '_validator_': lambda m: True,
 'value': 'date_time'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date4',
 '_regex_pattern_': r'(?P<DAY>(0[1-9]|[12][0-9]|3[01]))\.?\s*(?P<MONTH>(0[1-9]|1[0-2]))\.?\s*{YEAR}'.format(**substitutions),
 '_group_': 0,
 '_priority_': -1,
 '_validator_': lambda m: True,
 'value': 'date'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date5',
 '_regex_pattern_': r'{DAY}\.\s?{MONTH}'.format(**substitutions),
 '_group_': 0,
 '_priority_': 3,
 '_validator_': lambda m: True,
 'value': 'partial_date'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date6',
 '_regex_pattern_': r'{MONTH}\.\s?{LONGYEAR}'.format(**substitutions),
 '_group_': 0,
 '_priority_': 3,
 '_validator_': lambda m: True,
 'value': 'partial_date'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date7',
 '_regex_pattern_':
 r'{DAY}\.\s?{MONTH}\s*k(el)?l\s{HOUR}[.:]{MINUTE}(:{SECOND})?'.format(**substitutions),
 '_group_': 0,
 '_priority_': 3,
 '_validator_': lambda m: True,
 'value': 'partial_date'},

{'grammar_symbol': 'DATE',
 'regex_type': 'date8',
 '_regex_pattern_': r'{LONGYEAR}\s*a'.format(**substitutions),
 '_group_': 0,
 '_priority_': 0,
 '_validator_': lambda m: True,
 'value': 'partial_date'},

{
 'grammar_symbol': 'DATE',
 'regex_type': 'date9',
 '_regex_pattern_': r'{LONGYEAR}'.format(**substitutions),
 '_group_': 0,
 '_priority_': 0,
 '_validator_': lambda m: True,
 'value': 'partial_date'}
]
