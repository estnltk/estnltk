import re
import pytest

from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement
from estnltk.taggers.system.rule_taggers.regex_library.regex_pattern import RegexPattern

#===================================
#   RegexElement
#===================================

def test_regex_element_to_str():
    GAP = RegexElement(r'([ \t]+)')
    GAP.full_match(' ')
    GAP.no_match(r'\n')
    assert str(GAP) == r'(?:([ \t]+))'
    SCORE_VALUE = RegexElement(r'[0-9]{1,2}')
    NEG_SCORE = RegexElement(rf'-{SCORE_VALUE}', group_name='neg_score')
    NEG_SCORE.partial_match('-2', {'neg_score':'-2'})
    assert str(NEG_SCORE) == r'(?P<neg_score>-(?:[0-9]{1,2}))'


def test_regex_element_evaluate_positive_examples():
    GAP = RegexElement(r'([ \t]+)')
    # fully matching examples
    GAP.full_match(' ')
    GAP.full_match('\t')
    # displayable examples (same as full_match)
    GAP.example('  ')
    GAP.example(' \t')
    eval_pos_results_dict = \
        GAP.evaluate_positive_examples().to_dict(orient='split', index=False)
    assert eval_pos_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [[' ', '+'], ['\t', '+'], ['  ', '+'], [' \t', '+']]}
    # add mismatch
    GAP.full_match('\n')
    eval_pos_results_dict2 = \
        GAP.evaluate_positive_examples().to_dict(orient='split', index=False)
    assert eval_pos_results_dict2 == \
        {'columns': ['Example', 'Status'], 
         'data': [[' ', '+'], ['\t', '+'], ['  ', '+'], [' \t', '+'], ['\n', 'F']]}


def test_regex_element_evaluate_negative_examples():
    GAP = RegexElement(r'([ \t]+)')
    # fully (mis)matching examples
    GAP.no_match(r'\n')
    GAP.no_match(r'\n-')
    GAP.no_match(r'-\n')
    GAP.no_match(r'-\n-')
    eval_neg_results_dict = \
        GAP.evaluate_negative_examples().to_dict(orient='split', index=False)
    assert eval_neg_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [[r'\n', '+'], [r'\n-', '+'], [r'-\n', '+'], [r'-\n-', '+']]}
    # add mismatch
    # note: negative example fails even 
    # if the pattern is partially found 
    # inside the example
    GAP.no_match('\n ')
    eval_neg_results_dict2 = \
        GAP.evaluate_negative_examples().to_dict(orient='split', index=False)
    assert eval_neg_results_dict2 == \
        {'columns': ['Example', 'Status'], 
         'data': [[r'\n', '+'], [r'\n-', '+'], [r'-\n', '+'], [r'-\n-', '+'], ['\n ', 'F']]}


def test_regex_element_evaluate_extraction_examples():
    SCORE_VALUE = RegexElement(r'[0-9]{1,2}')
    NEG_SCORE = RegexElement(rf'-{SCORE_VALUE}', group_name='neg_score')
    # partial matches
    NEG_SCORE.partial_match('-1', '-1')
    NEG_SCORE.partial_match('-2', {'neg_score':'-2'})
    NEG_SCORE.partial_match('skoor langes -3 võrra', {'neg_score':'-3'})
    POS_SCORE = RegexElement(rf'\+{SCORE_VALUE}', group_name='pos_score')
    POS_SCORE.partial_match('+1', '+1')
    POS_SCORE.partial_match('+2', {'pos_score':'+2'})
    POS_SCORE.partial_match('skoor suurenes +22 võrra', {'pos_score':'+22'})
    assert NEG_SCORE.evaluate_extraction_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['-1', '+'], 
                  ['-2', '+'], 
                  ['skoor langes -3 võrra', '+']]}
    assert POS_SCORE.evaluate_extraction_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['+1', '+'], 
                  ['+2', '+'], 
                  ['skoor suurenes +22 võrra', '+']]}
    # add partial mismatches
    NEG_SCORE.partial_match('skoor suurenes +3 võrra', {'neg_score':'-3'})
    POS_SCORE.partial_match('skoor langes -2 võrra', {'pos_score':'+2'})
    assert NEG_SCORE.evaluate_extraction_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['-1', '+'], 
                  ['-2', '+'], 
                  ['skoor langes -3 võrra', '+'],
                  ['skoor suurenes +3 võrra', 'F']]}
    assert POS_SCORE.evaluate_extraction_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['+1', '+'], 
                  ['+2', '+'], 
                  ['skoor suurenes +22 võrra', '+'],
                  ['skoor langes -2 võrra', 'F']]}


def test_regex_element_truncate_string():
    ID_BIRTH_GENDER = RegexElement(r'([1-6])', group_name='birth_century_gender')
    ID_BIRTH_YEAR   = RegexElement(r'([0-9][0-9])', group_name='birth_year_last_numbers')
    ID_BIRTH_MONTH  = RegexElement(r'(0[1-9]|1[0-2])', group_name='birth_month')
    ID_BIRTH_DAY    = RegexElement(r'(0[1-9]|[12][0-9]|3[0-1])', group_name='birth_day')
    ID_BIRTH_ORDER  = RegexElement(r'([0-9][0-9][0-9])', group_name='birth_order')
    ID_CONTROL      = RegexElement(r'([0-9])', group_name='control_number')
    FULL_ID_NUMBER = RegexElement(fr'{ID_BIRTH_GENDER}{ID_BIRTH_YEAR}{ID_BIRTH_MONTH}{ID_BIRTH_DAY}{ID_BIRTH_ORDER}{ID_CONTROL}')
    # Add valid cases
    FULL_ID_NUMBER.full_match('34501234215')
    FULL_ID_NUMBER.full_match('49403136526')
    FULL_ID_NUMBER.full_match('61107121760')
    # Add an invalid case
    FULL_ID_NUMBER.full_match('78107320799')
    # Assert untruncated
    assert not RegexElement.TRUNCATE
    assert FULL_ID_NUMBER.evaluate_positive_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['34501234215', '+'], ['49403136526', '+'], ['61107121760', '+'], ['78107320799', 'F']]}
    with pytest.raises(AssertionError) as assertion_err:
        FULL_ID_NUMBER.test()
    stripped_str_repr = ((fr"{str(FULL_ID_NUMBER)}")[3:])[:-1]
    assert fr"pattern {stripped_str_repr!r} did not match positive example '78107320799'" in str(assertion_err.value)
    # Assert truncated
    RegexElement.TRUNCATE = True
    RegexElement.MAX_STRING_WIDTH = 10
    assert FULL_ID_NUMBER.evaluate_positive_examples().to_dict(orient='split', index=False) == \
        {'columns': ['Example', 'Status'], 
         'data': [['3450...4215', '+'], ['4940...6526', '+'], ['6110...1760', '+'], ['7810...0799', 'F']]}
    with pytest.raises(AssertionError) as assertion_err2:
        FULL_ID_NUMBER.test()
    assert r"pattern '(?P<...9]))' did not match positive example '7810...0799'" in str(assertion_err2.value)
    RegexElement.TRUNCATE = False



#
#  The following tests are based on:
#    https://github.com/estnltk/estnltk/blob/303f96312ab5b8e625bf019e965e5a70a5c8e47f/estnltk/estnltk/taggers/system/rule_taggers/regex_library/base_patterns.py
#

def test_regex_element_base_patterns():
    # Symbols
    
    GAP = RegexElement(r'([ \t]+)')
    GAP.full_match(' ')
    GAP.full_match('\t')
    GAP.no_match('\n')
    GAP.full_match('  ')
    GAP.full_match(' \t')
    GAP.no_match('\n-')
    GAP.test()

    DASH = RegexElement(r'([ \t]*-[ \t]*)')
    DASH.full_match('-')
    DASH.full_match(' -')
    DASH.full_match('- ')
    DASH.full_match(' - ')
    DASH.full_match('  -')
    DASH.full_match('\t-')
    DASH.full_match('-\t')
    DASH.partial_match('\n-', '-')
    DASH.partial_match('-\n', '-')
    DASH.no_match('  ')
    DASH.no_match('\t\t')
    DASH.test()

    DIV = RegexElement(r'([ \t]*/[ \t]*)')
    DIV.full_match('/')
    DIV.full_match(' /')
    DIV.full_match('/ ')
    DIV.full_match(' / ')
    DIV.full_match('  /')
    DIV.full_match('\t/')
    DIV.full_match('/\t')
    DIV.partial_match('\n/', '/')
    DIV.partial_match('/\n', '/')
    DIV.no_match('  ')
    DIV.no_match('\n\n')
    DIV.test()

    EQ = RegexElement(r'([ \t]*=[ \t]*)')
    EQ.full_match('=')
    EQ.full_match('\t=')
    EQ.full_match(' = ')
    EQ.full_match('\t=')
    EQ.partial_match('=\n', '=')
    EQ.partial_match('\n=', '=')
    EQ.no_match('  ')
    EQ.no_match('\t\t')
    EQ.test()

    COLON = RegexElement(r'([ \t]*:[ \t]*)')
    COLON.full_match('\t:')
    COLON.full_match(' : ')
    COLON.full_match(':')
    COLON.full_match('\t:')
    COLON.partial_match(':\n', ':')
    COLON.partial_match('\n:', ':')
    COLON.no_match('  ')
    COLON.no_match('\t\t')
    COLON.test()

    COMA = RegexElement(r'([ \t]*,[ \t]*)')
    COMA.full_match(',')
    COMA.full_match('\t,')
    COMA.full_match(' , ')
    COMA.full_match('\t,')
    COMA.partial_match(',\n', ',')
    COMA.partial_match('\n,', ',')
    COMA.no_match('  ')
    COMA.no_match('\t\t')
    COMA.test()

    ARROW = RegexElement(r'([ \t]*(-*>)[ \t]*)')
    ARROW.full_match('>')
    ARROW.full_match('->')
    ARROW.full_match('-->')
    ARROW.full_match('--->')
    ARROW.full_match(' -> ')
    ARROW.full_match('\t-> ')
    ARROW.partial_match(' ->\n', ' ->')
    ARROW.no_match('  ')
    ARROW.no_match('\t\t')
    ARROW.test()

    ELLIPSE = RegexElement(r'([ \t]*(\.{2,4})[ \t]*)')

    SCORE_VALUE = RegexElement(r'[0-9]{1,2}')
    SCORE_VALUE.full_match('0')
    SCORE_VALUE.full_match('1')
    SCORE_VALUE.full_match('03')
    SCORE_VALUE.full_match('43')
    SCORE_VALUE.partial_match('24 ', '24')
    SCORE_VALUE.partial_match('24p', '24')
    SCORE_VALUE.no_match('  ')
    SCORE_VALUE.no_match('Xp')
    SCORE_VALUE.test()

    SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='score')
    MIN_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='min_score')
    MAX_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='max_score')
    GAINED_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='gained_score')
    NOMINAL_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='nominal_score')
    INITIAL_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='initial_score')
    FINAL_SCORE = RegexElement(rf'{SCORE_VALUE}', group_name='final_score')
    SCORE.partial_match('12', {'score':'12'})
    MIN_SCORE.partial_match('0',{'min_score':'0'})
    MAX_SCORE.partial_match('22',{'max_score':'22'})
    GAINED_SCORE.partial_match('14',{'gained_score':'14'})
    NOMINAL_SCORE.partial_match('12',{'nominal_score':'12'})
    INITIAL_SCORE.partial_match('0',{'initial_score':'0'})
    FINAL_SCORE.partial_match('13',{'final_score':'13'})
    SCORE.test()
    MIN_SCORE.test()
    MAX_SCORE.test()
    GAINED_SCORE.test()
    NOMINAL_SCORE.test()
    INITIAL_SCORE.test()
    FINAL_SCORE.test()

    DECOMPOSED_SCORE = RegexElement(r'[0-9]{1,2}( *[+] *[0-9]{1,2})+', group_name='score')
    DECOMPOSED_SCORE.partial_match('12+3', {'score': '12+3'})
    DECOMPOSED_SCORE.partial_match('12 + 3 + 4', {'score': '12 + 3 + 4'})
    DECOMPOSED_SCORE.test()

    SCORE_UNIT = RegexElement(r'(punkti|punkt|pallile|palli|pall|p)')
    SCORE_UNIT.partial_match('p','p')
    SCORE_UNIT.partial_match('pallile','pallile')
    SCORE_UNIT.partial_match('palli','palli')
    SCORE_UNIT.partial_match('pall','pall')
    SCORE_UNIT.partial_match('punkt','punkt')
    SCORE_UNIT.partial_match('punkti','punkti')
    SCORE_UNIT.test()

    SCORE_ENTRY_1 = RegexElement(rf'{SCORE}\.p')
    SCORE_ENTRY_1.partial_match('4.p ', '4.p')
    SCORE_ENTRY_1.partial_match('4.punkti ', '4.p')
    SCORE_ENTRY_1.partial_match('4.p ', {'score': '4'})
    SCORE_ENTRY_1.test()

    SCORE_ENTRY_2 = RegexElement(rf'({SCORE}( *{SCORE_UNIT})?)')
    SCORE_ENTRY_2.partial_match('0','0')
    SCORE_ENTRY_2.partial_match('1','1')
    SCORE_ENTRY_2.partial_match('03','03')
    SCORE_ENTRY_2.partial_match('43 ','43')
    SCORE_ENTRY_2.partial_match('24p','24p')
    SCORE_ENTRY_2.partial_match('4 p','4 p')
    SCORE_ENTRY_2.partial_match('4  p','4  p')
    SCORE_ENTRY_2.partial_match('4 palli','4 palli')
    SCORE_ENTRY_2.partial_match('4 punkti', {'score': '4'})
    SCORE_ENTRY_2.test()

    SCORE_ENTRY_3 = RegexElement(rf'({SCORE}/n{EQ}{SCORE_VALUE}{DASH}{SCORE_VALUE})')
    SCORE_ENTRY_3.partial_match('26/n=26-30','26/n=26-30')
    SCORE_ENTRY_3.partial_match('26/n = 26 - 30','26/n = 26 - 30')
    SCORE_ENTRY_3.partial_match('26/n = 26 - 30', {'score': '26'})
    SCORE_ENTRY_3.test()

    SCORE_ENTRY_4 = RegexElement(rf'((skoor){GAP}{DECOMPOSED_SCORE}( *{SCORE_UNIT})?)')
    SCORE_ENTRY_4.partial_match('skoor 21+2','skoor 21+2')
    SCORE_ENTRY_4.partial_match('skoor 21 + 2','skoor 21 + 2')
    SCORE_ENTRY_4.partial_match('skoor 21+2', {'score': '21+2'})
    SCORE_ENTRY_4.test()

    SCORE_ENTRY = RegexElement(rf'({SCORE_ENTRY_1}|{SCORE_ENTRY_2}|{SCORE_ENTRY_3}|{SCORE_ENTRY_4})')
    SCORE_ENTRY.partial_match('43 ','43')
    SCORE_ENTRY.partial_match('4 palli','4 palli')
    SCORE_ENTRY.partial_match('3.p. ta','3.p')
    SCORE_ENTRY.partial_match('skoor 21+2', {'score': '21+2'})
    SCORE_ENTRY.partial_match('4 punkti ', {'score': '4'})
    SCORE_ENTRY.test()

    INITIAL_ENTRY = RegexElement(rf'({INITIAL_SCORE}( *{SCORE_UNIT})?)')
    INITIAL_ENTRY.partial_match('0','0')
    INITIAL_ENTRY.partial_match('1','1')
    INITIAL_ENTRY.partial_match('03','03')
    INITIAL_ENTRY.partial_match('43 ','43')
    INITIAL_ENTRY.partial_match('24p','24p')
    INITIAL_ENTRY.partial_match('4 p','4 p')
    INITIAL_ENTRY.partial_match('4  p','4  p')
    INITIAL_ENTRY.partial_match('4 palli', '4 palli')
    INITIAL_ENTRY.partial_match('4 punkti', {'initial_score':'4'})
    INITIAL_ENTRY.test()

    MID_ENTRY = RegexElement(rf'({SCORE_VALUE}( *{SCORE_UNIT})?)')
    MID_ENTRY.partial_match('0','0')
    MID_ENTRY.partial_match('1','1')
    MID_ENTRY.partial_match('03','03')
    MID_ENTRY.partial_match('43 ','43')
    MID_ENTRY.partial_match('24p','24p')
    MID_ENTRY.partial_match('4 p','4 p')
    MID_ENTRY.partial_match('4  p','4  p')
    MID_ENTRY.partial_match('4 palli', '4 palli')
    MID_ENTRY.test()

    FINAL_ENTRY = RegexElement(rf'({FINAL_SCORE}( *{SCORE_UNIT})?)')
    FINAL_ENTRY.partial_match('0','0')
    FINAL_ENTRY.partial_match('1','1')
    FINAL_ENTRY.partial_match('03','03')
    FINAL_ENTRY.partial_match('43 ','43')
    FINAL_ENTRY.partial_match('24p','24p')
    FINAL_ENTRY.partial_match('4 p','4 p')
    FINAL_ENTRY.partial_match('4  p','4  p')
    FINAL_ENTRY.partial_match('4 palli', '4 palli')
    FINAL_ENTRY.partial_match('4 punkti', {'final_score':'4'})
    FINAL_ENTRY.test()

    SCORE_PP_RANGE = RegexElement(fr'({MIN_SCORE} *p{DASH}{MAX_SCORE} *p)')
    SCORE_DD_RANGE = RegexElement(fr'({MIN_SCORE}{ELLIPSE}{MAX_SCORE})')
    SCORE_STD_RANGE = RegexElement(fr'({MIN_SCORE}{DASH}{MAX_SCORE}({GAP}?{SCORE_UNIT})?)')
    SCORE_RANGE = RegexElement(fr'({SCORE_STD_RANGE}|{SCORE_DD_RANGE}|{SCORE_PP_RANGE})')
    SCORE_RANGE.partial_match('3-4','3-4')
    SCORE_RANGE.partial_match('3 - 4','3 - 4')
    SCORE_RANGE.partial_match('3 -4 ','3 -4')
    SCORE_RANGE.partial_match('3- 4 ','3- 4')
    SCORE_RANGE.partial_match(' 3-4', '3-4')
    SCORE_RANGE.partial_match('3-4 ', '3-4')
    SCORE_RANGE.partial_match('3 - 4p','3 - 4p')
    SCORE_RANGE.partial_match('3p-8p','3p-8p')
    SCORE_RANGE.partial_match('3 p - 4 p ','3 p - 4 p')
    SCORE_RANGE.partial_match('4 .... 10 ', '4 .... 10')
    SCORE_RANGE.partial_match('3-6p.', '3-6p')
    SCORE_RANGE.partial_match('3-7p ', '3-7p')
    SCORE_RANGE.no_match('3 palli - 4p')
    SCORE_RANGE.no_match('3 palli - 4 palli')
    SCORE_RANGE.no_match('3 pallikest - 7palli')
    SCORE_RANGE.test()

    TEXTUAL_SCORE_RANGE = SCORE_RANGE
    TEXTUAL_SCORE_RANGE.partial_match('20-30 ', '20-30')
    TEXTUAL_SCORE_RANGE.partial_match('20-30 punkti','20-30 punkti')
    TEXTUAL_SCORE_RANGE.test()

    SCORE_RATIO_UNIT = RegexElement(r'(punkti|punkt|pallile|palli|pall|p|—st|-st|st)')
    SCORE_RATIO_UNIT.partial_match('p','p')
    SCORE_RATIO_UNIT.partial_match('st','st')
    SCORE_RATIO_UNIT.partial_match('-st','-st')
    SCORE_RATIO_UNIT.partial_match('—st','—st')
    SCORE_RATIO_UNIT.partial_match('pallile','pallile')
    SCORE_RATIO_UNIT.partial_match('palli','palli')
    SCORE_RATIO_UNIT.partial_match('pall','pall')
    SCORE_RATIO_UNIT.partial_match('punkt','punkt')
    SCORE_RATIO_UNIT.partial_match('punkti','punkti')
    SCORE_UNIT.test()

    SCORE_RATIO_1 = RegexElement(rf'({GAINED_SCORE}{DIV}{NOMINAL_SCORE}({GAP}?{SCORE_RATIO_UNIT})?)')
    SCORE_RATIO_1.partial_match('7/10','7/10')
    SCORE_RATIO_1.partial_match(' 7/10 ','7/10')
    SCORE_RATIO_1.partial_match('7/ 10','7/ 10')
    SCORE_RATIO_1.partial_match('7 / 10','7 / 10')
    SCORE_RATIO_1.partial_match('7/10p','7/10p')
    SCORE_RATIO_1.partial_match('7/10 ','7/10')
    SCORE_RATIO_1.partial_match('7/10-st','7/10-st')
    SCORE_RATIO_1.partial_match('7/10 -st','7/10 -st')
    SCORE_RATIO_1.no_match('kaks kolme-st')
    SCORE_RATIO_1.no_match('viis kaheksast')
    SCORE_RATIO_1.test()

    SCORE_RATIO_2 = RegexElement(rf'({GAINED_SCORE}{GAP}?(palli|punki|punkti){GAP}?{NOMINAL_SCORE}(-st|st))')
    SCORE_RATIO_2.partial_match('20 punkti 30-st.','20 punkti 30-st')
    SCORE_RATIO_2.partial_match('20 punkti 30-st.', {'gained_score': '20'})
    SCORE_RATIO_2.partial_match('20 punkti 30-st.', {'nominal_score': '30'})
    SCORE_RATIO_2.partial_match('20 punkti 30st.','20 punkti 30st')
    SCORE_RATIO_2.partial_match('19 palli 30-st.','19 palli 30-st')
    SCORE_RATIO_2.partial_match('25 punkti 30-st.','25 punkti 30-st')
    SCORE_RATIO_2.test()

    SCORE_RATIO_3 = RegexElement(rf'(\({GAINED_SCORE}{DIV}{NOMINAL_SCORE}\))')
    SCORE_RATIO_3.partial_match('(20/30) ','(20/30)')
    SCORE_RATIO_3.partial_match('(20/30) ', {'gained_score': '20'})
    SCORE_RATIO_3.partial_match('(20/30) ', {'nominal_score': '30'})
    SCORE_RATIO_3.partial_match('(20 / 30) ', '(20 / 30)')
    SCORE_RATIO_3.test()

    SCORE_RATIO_4 = RegexElement(rf'({NOMINAL_SCORE}{GAP}(võimalikust|võimalikkust){GAP}{GAINED_SCORE}({GAP}?(punkti|palli)))')
    SCORE_RATIO_4.partial_match('30 võimalikust 24 punkti.','30 võimalikust 24 punkti')
    SCORE_RATIO_4.partial_match('30 võimalikust 24 punkti.', {'gained_score': '24'})
    SCORE_RATIO_4.partial_match('30 võimalikust 24 punkti.', {'nominal_score': '30'})
    SCORE_RATIO_4.test()

    SCORE_RATIO_5 = RegexElement(rf'(saadud{GAP}(punkte|palle){GAP}{NOMINAL_SCORE}(-st|st){GAP}{GAINED_SCORE}({GAP}?(punkti|palli))?)')
    SCORE_RATIO_5.partial_match('saadud punkte 30-st 20 ','saadud punkte 30-st 20')
    SCORE_RATIO_5.partial_match('saadud punkte 30-st 20 ', {'gained_score': '20'})
    SCORE_RATIO_5.partial_match('saadud punkte 30-st 20 ', {'nominal_score': '30'})
    SCORE_RATIO_5.test()

    SCORE_RATIO_6 = RegexElement(rf'({GAINED_SCORE}{GAP}?(punkti|palli){GAP}\({GAP}?{NOMINAL_SCORE}(-st|st){GAP}?\))')
    SCORE_RATIO_6.partial_match('7 punkti	(30-st).','7 punkti	(30-st)')
    SCORE_RATIO_6.partial_match('7 punkti	(30-st).', {'gained_score': '7'})
    SCORE_RATIO_6.partial_match('7 punkti	(30-st).', {'nominal_score': '30'})
    SCORE_RATIO_6.test()

    SCORE_RATIO = RegexElement(rf'({SCORE_RATIO_1}|{SCORE_RATIO_2}|{SCORE_RATIO_4}|{SCORE_RATIO_5}|{SCORE_RATIO_5})')
    SCORE_RATIO.partial_match('20/30 punkti','20/30 punkti')
    SCORE_RATIO.partial_match('20 punkti 30-st.','20 punkti 30-st')
    SCORE_RATIO.partial_match('(20/30)', '20/30')
    SCORE_RATIO.partial_match('saadud punkte 30-st 20 ','saadud punkte 30-st 20')
    SCORE_RATIO.no_match('kakskümmend kolmekümbnest')
    SCORE_RATIO.test()

    TEXTUAL_SCORE_RATIO = RegexElement(rf'({SCORE_RATIO_1}|{SCORE_RATIO_2}|{SCORE_RATIO_3}' \
                          rf'|{SCORE_RATIO_4}|{SCORE_RATIO_5}|{SCORE_RATIO_6})')
    TEXTUAL_SCORE_RATIO.partial_match('20/30 punkti','20/30 punkti')
    TEXTUAL_SCORE_RATIO.partial_match('20 punkti 30-st.','20 punkti 30-st')
    TEXTUAL_SCORE_RATIO.partial_match('(20/30) ','(20/30)')
    TEXTUAL_SCORE_RATIO.partial_match('saadud punkte 30-st 20 ','saadud punkte 30-st 20')
    TEXTUAL_SCORE_RATIO.test()
   
    # Name extensions
    
    LEFT_EXT_24H = RegexElement(r'24( |\t)*h( |\t)*$')
    LEFT_EXT_24H.full_match('24h')
    LEFT_EXT_24H.full_match('24 h')
    LEFT_EXT_24H.full_match('24h ')
    LEFT_EXT_24H.full_match('24 h ')
    LEFT_EXT_24H.partial_match(' 24 h ', '24 h ')
    LEFT_EXT_24H.no_match('48h ')
    LEFT_EXT_24H.no_match('kakskümmend neli h')
    LEFT_EXT_24H.test()

    RIGHT_EXT_24H = RegexElement(r'^:?( |\t)*24( |\t)*h')
    RIGHT_EXT_24H.full_match('24h')
    RIGHT_EXT_24H.full_match('24 h')
    RIGHT_EXT_24H.full_match(' 24h')
    RIGHT_EXT_24H.full_match(' 24 h')
    RIGHT_EXT_24H.full_match(': 24 h')
    RIGHT_EXT_24H.full_match(':24h')
    RIGHT_EXT_24H.partial_match(' 24 h ', ' 24 h')
    RIGHT_EXT_24H.no_match(' 48h')
    RIGHT_EXT_24H.no_match(' kakskümmend-neli-h')
    RIGHT_EXT_24H.test()

    RIGHT_EXT_SCORE = RegexElement(r'^( |\t)*(skoor|skaala)')
    RIGHT_EXT_SCORE.partial_match('skoor','skoor')
    RIGHT_EXT_SCORE.partial_match('skoor:','skoor')
    RIGHT_EXT_SCORE.partial_match('skaala','skaala')
    RIGHT_EXT_SCORE.partial_match('skaala ','skaala')
    RIGHT_EXT_SCORE.test()

    RIGHT_EXT_BRACKET = RegexElement(rf'^({GAP})?\)')
    RIGHT_EXT_BRACKET.partial_match(')',')')
    RIGHT_EXT_BRACKET.partial_match(' ) ',' )')
    RIGHT_EXT_BRACKET.test()

    RIGHT_EXT_CASE = RegexElement(rf'^(-l|{DASH}l)')
    RIGHT_EXT_CASE.partial_match('-l','-l')
    RIGHT_EXT_CASE.partial_match(' -l',' -l')
    RIGHT_EXT_CASE.partial_match(' -l ',' -l')
    RIGHT_EXT_CASE.test()

    MMSE_NAME_1 = r'Mini - mental test'
    MMSE_NAME_2 = r'VMU'
    MMSE_NAME_3 = r'[Vv]aimse seisundi miniuuring'
    MMSE_NAME_4 = r'Mini-Mental State Examination'
    MMSE_NAME_5 = rf'[Vv]aimse seisundi mini{DASH}?uuringu'

    LEFT_MMSE_NAME_EXT = RegexElement(rf'({MMSE_NAME_3}|{MMSE_NAME_4}|{MMSE_NAME_5}){GAP}\($')
    LEFT_MMSE_NAME_EXT.partial_match('vaimse seisundi miniuuring (', 'vaimse seisundi miniuuring (')
    LEFT_MMSE_NAME_EXT.partial_match('Mini-Mental State Examination (', 'Mini-Mental State Examination (')
    LEFT_MMSE_NAME_EXT.partial_match('Vaimse seisundi miniuuringu (', 'Vaimse seisundi miniuuringu (')
    LEFT_MMSE_NAME_EXT.partial_match('Vaimse seisundi mini-uuringu (', 'Vaimse seisundi mini-uuringu (')
    LEFT_MMSE_NAME_EXT.test()

    RIGHT_MMSE_NAME_EXT = RegexElement(rf'^({GAP}({MMSE_NAME_1}|\({MMSE_NAME_2}\)|\({MMSE_NAME_3}\)))|^{DASH}{MMSE_NAME_4}')
    RIGHT_MMSE_NAME_EXT.partial_match(' Mini - mental test',' Mini - mental test')
    RIGHT_MMSE_NAME_EXT.partial_match(' (VMU)',' (VMU)')
    RIGHT_MMSE_NAME_EXT.partial_match(' (vaimse seisundi miniuuring)',' (vaimse seisundi miniuuring)')
    RIGHT_MMSE_NAME_EXT.partial_match(' - Mini-Mental State Examination',' - Mini-Mental State Examination')
    RIGHT_MMSE_NAME_EXT.no_match(' something else ... Mini - mental test')
    RIGHT_MMSE_NAME_EXT.no_match(' something else ... - Mini-Mental State Examination')
    RIGHT_MMSE_NAME_EXT.test()

    MMSE_COMPLETED = r'([Tt]einud|[Tt]eostatud|[Tt]ehtud|[Tt]egin)'
    LEFT_MMSE_COMPLETED_EXT = RegexElement(rf'{MMSE_COMPLETED}{GAP}$')
    LEFT_MMSE_COMPLETED_EXT.partial_match('teinud ', 'teinud ')
    LEFT_MMSE_COMPLETED_EXT.partial_match('Teostatud ', 'Teostatud ')
    LEFT_MMSE_COMPLETED_EXT.partial_match('tehtud ', 'tehtud ')
    LEFT_MMSE_COMPLETED_EXT.partial_match(' Tegin ', 'Tegin ')
    LEFT_MMSE_COMPLETED_EXT.test()

    RIGHT_MMSE_COMPLETED_EXT = RegexElement(rf'^({GAP})?,({GAP}? kus)?')
    RIGHT_MMSE_COMPLETED_EXT.partial_match(', ',',')
    RIGHT_MMSE_COMPLETED_EXT.partial_match(' ,',' ,')
    RIGHT_MMSE_COMPLETED_EXT.partial_match(', kus', ', kus')
    RIGHT_MMSE_COMPLETED_EXT.test()


    # Payloads

    PAYLOAD_END_1 = RegexElement(r'([\r\n,.;\(\)\t ]|->|$)')
    PAYLOAD_END_1.partial_match('','')
    PAYLOAD_END_1.partial_match('\n','\n')
    PAYLOAD_END_1.partial_match('.','.')
    PAYLOAD_END_1.partial_match(';',';')
    PAYLOAD_END_1.partial_match(')',')')
    PAYLOAD_END_1.partial_match(') ',')')
    PAYLOAD_END_1.partial_match('(1','(')
    PAYLOAD_END_1.partial_match('  ',' ')
    PAYLOAD_END_1.partial_match('\t ','\t')
    PAYLOAD_END_1.partial_match(' \t a',' ')
    PAYLOAD_END_1.partial_match('-> x','->')
    PAYLOAD_END_1.test()

    # For some reason, matching '\r' or '\rx' does not work correctly 
    # (at least on Windows platform)
    PAYLOAD_END_1.partial_match(r'\r', r'\r')
    PAYLOAD_END_1.partial_match(r'\rx', '\rx')
    last_extraction_examples_results_dict = \
        PAYLOAD_END_1.evaluate_extraction_examples().to_dict(orient='split', index=False)
    last_extraction_examples_results_dict['data'] = \
        last_extraction_examples_results_dict['data'][-2:]
    #print(last_extraction_examples_results_dict)
    assert last_extraction_examples_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['\\r', 'F'], ['\\rx', 'F']]}

    # Quick fix for segmenting errors
    PAYLOAD_END_2 = RegexElement(r'(CTA |CT-|CT |Patsien|Intensiiv|Vererõhk)')
    PAYLOAD_END_2.partial_match('CTA ','CTA ')
    PAYLOAD_END_2.partial_match('CT ','CT ')
    PAYLOAD_END_2.partial_match('CT-','CT-')
    PAYLOAD_END_2.partial_match('Patsient','Patsien')
    PAYLOAD_END_2.partial_match('Intensiiv','Intensiiv')
    PAYLOAD_END_2.partial_match('Vererõhk','Vererõhk')
    PAYLOAD_END_2.test()

    # Quick fix: Payloads are converted to lower letters
    PAYLOAD_END = RegexElement(rf'({PAYLOAD_END_1}|{str(PAYLOAD_END_2).lower()})')
    PAYLOAD_END.partial_match('','')
    PAYLOAD_END.partial_match('vererõhk','vererõhk')
    PAYLOAD_END.test()

    PAYLOAD_END_IS_NEEDED = RegexElement(r'\(.*\)$')
    PAYLOAD_END_IS_NEEDED.partial_match('(25)', '(25)')
    PAYLOAD_END_IS_NEEDED.no_match(' 25)')
    PAYLOAD_END_IS_NEEDED.test()

    PAYLOAD_END_ELIMINATOR_1 = RegexElement(r'[\r\n,.;\(\)]$|[\t ]+$|->$|$')
    PAYLOAD_END_ELIMINATOR_1.partial_match('','')
    PAYLOAD_END_ELIMINATOR_1.partial_match('\n','\n')
    PAYLOAD_END_ELIMINATOR_1.partial_match('\nabba\r','\r')
    PAYLOAD_END_ELIMINATOR_1.partial_match('a.','.')
    PAYLOAD_END_ELIMINATOR_1.partial_match('b;',';')
    PAYLOAD_END_ELIMINATOR_1.partial_match('.)',')')
    PAYLOAD_END_ELIMINATOR_1.partial_match(' (','(')
    PAYLOAD_END_ELIMINATOR_1.partial_match(') ',' ')
    PAYLOAD_END_ELIMINATOR_1.partial_match('a  ','  ')
    PAYLOAD_END_ELIMINATOR_1.partial_match(' \t ',' \t ')
    PAYLOAD_END_ELIMINATOR_1.partial_match(' \t a','')
    PAYLOAD_END_ELIMINATOR_1.partial_match('xx->','->')
    PAYLOAD_END_ELIMINATOR_1.test()

    PAYLOAD_END_ELIMINATOR = RegexElement(rf'{PAYLOAD_END_ELIMINATOR_1}|({PAYLOAD_END_2}$)').compile()


    DARROW_PAYLOAD = RegexElement(rf'^({DASH}|{GAP}){INITIAL_ENTRY}{ARROW}{MID_ENTRY}{ARROW}{FINAL_ENTRY}{PAYLOAD_END}')
    DARROW_PAYLOAD.no_match(' 3')
    DARROW_PAYLOAD.no_match(' 3->2')
    DARROW_PAYLOAD.full_match(' 23 ->20 -> 12')
    DARROW_PAYLOAD.full_match(' - 23p ->22 --> 5palli')
    DARROW_PAYLOAD.full_match('-20 --> 2p --> 3p;')
    DARROW_PAYLOAD.full_match(' 20>10>3p.')
    DARROW_PAYLOAD.full_match(' 20 -> 12 -> 10,')
    DARROW_PAYLOAD.full_match(' 20 -> 12 -> 10;')
    DARROW_PAYLOAD.no_match('x 20 -> 12 -> 10;')
    DARROW_PAYLOAD.test()

    ARROW_ENTRY_1 = RegexElement(rf'({INITIAL_ENTRY}{ARROW}{FINAL_ENTRY})')
    ARROW_ENTRY_1.no_match(' 3')
    ARROW_ENTRY_1.no_match(' -3')
    ARROW_ENTRY_1.no_match(' - 3')
    ARROW_ENTRY_1.partial_match(' 23 ->2', '23 ->2')
    ARROW_ENTRY_1.partial_match(' - 23p ->2', '23p ->2')
    ARROW_ENTRY_1.partial_match('-20 --> 2p', '20 --> 2p')
    ARROW_ENTRY_1.partial_match('-20 --> 2p.', '20 --> 2p')
    ARROW_ENTRY_1.partial_match(' 20 --> 2p,', '20 --> 2p')
    ARROW_ENTRY_1.partial_match(' 20 --> 2p;', '20 --> 2p')
    ARROW_ENTRY_1.partial_match('x 3 -> 2', '3 -> 2')
    ARROW_ENTRY_1.no_match('3 ==> 2')
    ARROW_ENTRY_1.no_match('3 ~~> 2')
    ARROW_ENTRY_1.test()

    ARROW_ENTRY_2 = RegexElement(rf'((paranenud|tõusnud){GAP}{INITIAL_SCORE}(-lt|lt){GAP}{FINAL_SCORE}(-le|le))')
    ARROW_ENTRY_2.partial_match('paranenud 22-lt 26-le.','paranenud 22-lt 26-le')
    ARROW_ENTRY_2.partial_match('paranenud 22-lt 26-le.', {'initial_score': '22'})
    ARROW_ENTRY_2.partial_match('paranenud 22-lt 26-le.', {'final_score': '26'})
    ARROW_ENTRY_2.test()

    ARROW_ENTRY_3 = RegexElement(rf'((saabudes){GAP}{INITIAL_ENTRY}{COMA}(lahkudes){GAP}{FINAL_ENTRY})')
    ARROW_ENTRY_3.partial_match('saabudes 23 p, lahkudes 20p','saabudes 23 p, lahkudes 20p')
    ARROW_ENTRY_3.partial_match('saabudes 23 p, lahkudes 20p', {'initial_score': '23'})
    ARROW_ENTRY_3.partial_match('saabudes 23 p, lahkudes 20p', {'final_score':'20'})
    ARROW_ENTRY_3.test()

    ARROW_ENTRY_4 = RegexElement(rf'{INITIAL_ENTRY}{GAP}(saabumisel{GAP}>>|saabumisel){GAP}{FINAL_ENTRY}{GAP}(lahkumisel)')
    ARROW_ENTRY_4.partial_match('3 palli saabumisel >> 1 palli lahkumisel','3 palli saabumisel >> 1 palli lahkumisel')
    ARROW_ENTRY_4.partial_match('3 palli saabumisel >> 1 palli lahkumisel', {'initial_score':'3'})
    ARROW_ENTRY_4.partial_match('3 palli saabumisel >> 1 palli lahkumisel', {'final_score':'1'})
    ARROW_ENTRY_4.test()

    ARROW_PAYLOAD = RegexElement(
        rf'^(({DASH}|{GAP}){ARROW_ENTRY_1}|{GAP}({ARROW_ENTRY_2}|{ARROW_ENTRY_3}|{ARROW_ENTRY_4})){PAYLOAD_END}')
    ARROW_PAYLOAD.no_match(' 3')
    ARROW_PAYLOAD.no_match(' -3')
    ARROW_PAYLOAD.no_match(' - 3')
    ARROW_PAYLOAD.full_match(' 23 ->2')
    ARROW_PAYLOAD.full_match(' - 23p ->2')
    ARROW_PAYLOAD.full_match('-20 --> 2p')
    ARROW_PAYLOAD.full_match(' 20 --> 2p.')
    ARROW_PAYLOAD.full_match(' 20 --> 2p,')
    ARROW_PAYLOAD.full_match(' 20 --> 2p;')
    ARROW_PAYLOAD.no_match('x 3 -> 2')
    ARROW_PAYLOAD.partial_match(' paranenud 22-lt 26-le.',' paranenud 22-lt 26-le.')
    ARROW_PAYLOAD.partial_match(' saabudes 23 p, lahkudes 20p',' saabudes 23 p, lahkudes 20p')
    ARROW_PAYLOAD.partial_match(' 3 palli saabumisel >> 1 palli lahkumisel',' 3 palli saabumisel >> 1 palli lahkumisel')
    ARROW_PAYLOAD.test()


    SHORT_PAYLOAD = RegexElement(rf'^({DASH}|{GAP}|{EQ}|{COLON})?{SCORE_ENTRY}{PAYLOAD_END}')
    SHORT_PAYLOAD.full_match('3')
    SHORT_PAYLOAD.full_match(' 3')
    SHORT_PAYLOAD.full_match('  3')
    SHORT_PAYLOAD.full_match('-3')
    SHORT_PAYLOAD.full_match('=3')
    SHORT_PAYLOAD.full_match(' - 5')
    SHORT_PAYLOAD.full_match(' = 3')
    SHORT_PAYLOAD.full_match('- 3')
    SHORT_PAYLOAD.full_match(' -3')
    SHORT_PAYLOAD.full_match(' 3p')
    SHORT_PAYLOAD.full_match(' 3p.')
    SHORT_PAYLOAD.full_match(' 3p,')
    SHORT_PAYLOAD.full_match(' 3p;')
    SHORT_PAYLOAD.full_match(': 3p')
    SHORT_PAYLOAD.full_match(' : 3p')
    SHORT_PAYLOAD.no_match('x 3')
    SHORT_PAYLOAD.partial_match('3 pankreatiit','3 ')
    SHORT_PAYLOAD.partial_match('3 p. ta','3 p.')
    SHORT_PAYLOAD.partial_match('3.p. ta','3.p.')
    SHORT_PAYLOAD.no_match('x 3 --> 1')
    SHORT_PAYLOAD.partial_match(' 3p --> 1', ' 3p ')
    SHORT_PAYLOAD.test()

    SHORT_RANGE_PAYLOAD = RegexElement(rf'^({GAP}|{EQ}|{COLON}){SCORE_RANGE}{PAYLOAD_END}')
    SHORT_RANGE_PAYLOAD.partial_match(' 3-4',' 3-4')
    SHORT_RANGE_PAYLOAD.partial_match('  3 - 4 ','  3 - 4 ')
    SHORT_RANGE_PAYLOAD.partial_match('= 3-4 panama','= 3-4 ')
    SHORT_RANGE_PAYLOAD.partial_match(' = 3 -4',' = 3 -4')
    SHORT_RANGE_PAYLOAD.partial_match(' 3 - 4p',' 3 - 4p')
    SHORT_RANGE_PAYLOAD.partial_match(' 3-6p. ',' 3-6p.')
    SHORT_RANGE_PAYLOAD.partial_match(' 3-7p,xx',' 3-7p,')
    SHORT_RANGE_PAYLOAD.partial_match(' 3-4p;\nx',' 3-4p;')
    SHORT_RANGE_PAYLOAD.partial_match(': 3-8p',': 3-8p')
    SHORT_RANGE_PAYLOAD.partial_match(' : 3-4p',' : 3-4p')
    SHORT_RANGE_PAYLOAD.partial_match(' 3p - 4p xx',' 3p - 4p ')
    SHORT_RANGE_PAYLOAD.no_match('-3-4')
    SHORT_RANGE_PAYLOAD.no_match('- 3-4')
    SHORT_RANGE_PAYLOAD.no_match(' - 5-4')
    SHORT_RANGE_PAYLOAD.no_match(' 3 palli - 4p')
    SHORT_RANGE_PAYLOAD.no_match(' 3p --> 1')
    SHORT_RANGE_PAYLOAD.no_match('x 3-4')
    SHORT_RANGE_PAYLOAD.test()

    SHORT_RATIO_PAYLOAD = RegexElement(rf'^({DASH}|{GAP}|{EQ}|{COLON})?{SCORE_RATIO}{PAYLOAD_END}')
    SHORT_RATIO_PAYLOAD.partial_match('3/10','3/10')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/10',' 3/10')
    SHORT_RATIO_PAYLOAD.partial_match('3/10p','3/10p')
    SHORT_RATIO_PAYLOAD.partial_match('3/10 punkti','3/10 punkti')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/ 10',' 3/ 10')
    SHORT_RATIO_PAYLOAD.partial_match('= 3/4\n','= 3/4\n')
    SHORT_RATIO_PAYLOAD.partial_match('= 3 / 4','= 3 / 4')
    SHORT_RATIO_PAYLOAD.partial_match('-3/4\tx','-3/4\t')
    SHORT_RATIO_PAYLOAD.partial_match('- 3/4 x','- 3/4 ')
    SHORT_RATIO_PAYLOAD.partial_match(': 3/8',': 3/8')
    SHORT_RATIO_PAYLOAD.partial_match(' : 3/4',' : 3/4')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/6.x',' 3/6.')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/7, ',' 3/7,')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/4; x',' 3/4;')
    SHORT_RATIO_PAYLOAD.partial_match(' 3/4) ',' 3/4)')
    SHORT_RATIO_PAYLOAD.no_match('x 3/4')
    SHORT_RATIO_PAYLOAD.test()
    
    # Potential payloads to be verified further

    TEXT_PREFIX = rf'^({GAP}|{DASH}|{COLON})(?P<text>.+?){GAP}'

    POTENTIAL_ARROW_PAYLOAD = RegexElement(
        rf'^{TEXT_PREFIX}({DASH}?{ARROW_ENTRY_1}|{ARROW_ENTRY_2}|{ARROW_ENTRY_3}|{ARROW_ENTRY_4}){PAYLOAD_END}')
    POTENTIAL_ARROW_PAYLOAD.partial_match(' dünaamika 20 --> 2p.',' dünaamika 20 --> 2p.')
    POTENTIAL_ARROW_PAYLOAD.partial_match(' dünaamika 20 --> 2p.', {'text': 'dünaamika'})
    POTENTIAL_ARROW_PAYLOAD.partial_match(' skoor paranenud 22-lt 26-le.',' skoor paranenud 22-lt 26-le.')
    POTENTIAL_ARROW_PAYLOAD.partial_match(' skoor saabudes 23 p, lahkudes 20p',' skoor saabudes 23 p, lahkudes 20p')
    POTENTIAL_ARROW_PAYLOAD.partial_match(' skoor 3 palli saabumisel >> 1 palli lahkumisel',' skoor 3 palli saabumisel >> 1 palli lahkumisel')


    POTENTIAL_SHORT_SCORE_PAYLOAD = RegexElement(rf'{TEXT_PREFIX}(?P<iscore>{SCORE_ENTRY}){PAYLOAD_END}')
    POTENTIAL_SHORT_SCORE_PAYLOAD.partial_match(' skoor 28', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_PAYLOAD.partial_match('- skoor 28', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_PAYLOAD.partial_match('- skoor 28 veel teksti ja 30', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_PAYLOAD.no_match(' tavatekst\n skoor 28')
    POTENTIAL_SHORT_SCORE_PAYLOAD.test()

    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD = RegexElement(rf'{TEXT_PREFIX}{TEXTUAL_SCORE_RANGE}{PAYLOAD_END}')
    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD.partial_match(' skoor 20 - 25 ', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD.partial_match('- skoor 20 - 25)', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD.partial_match('- skoor 20 - 25 veel teksti ja 30', {'text': 'skoor'})
    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD.no_match(' tavatekst\n skoor 28-29')
    POTENTIAL_SHORT_SCORE_RANGE_PAYLOAD.test()

    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD = RegexElement(rf'{TEXT_PREFIX}{TEXTUAL_SCORE_RATIO}{PAYLOAD_END}')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.partial_match(' sai 20/30 punkti;',' sai 20/30 punkti;')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.partial_match('- saab 20 punkti 30-st.','- saab 20 punkti 30-st.')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.no_match('(20/30)')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.no_match('  (20/30)')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.partial_match(' saab  (20/30) ',' saab  (20/30) ')
    POTENTIAL_SHORT_SCORE_RATIO_PAYLOAD.test()

    # Context validation

    RIGHT_COMMENT = RegexElement(rf'->{GAP}?(?P<text>.*)\.|^{DASH}(?P<text>.*)\.|^\((?P<text>.*)\)')
    RIGHT_COMMENT.partial_match('- word and word. Other text', {'text':'word and word'})
    RIGHT_COMMENT.partial_match(' - word and word. Other text', {'text': 'word and word'})
    RIGHT_COMMENT.partial_match('(word. word) Other text', {'text': 'word. word'})
    RIGHT_COMMENT.partial_match('(word. word). Other text', {'text': 'word. word'})
    RIGHT_COMMENT.test()
    
    SPURIOUS_NIH_SCORE_1 = RegexElement(rf'^NIH({DASH}|{GAP})?[0-9]{DASH}[0-9]{DASH}[0-9]')
    SPURIOUS_NIH_SCORE_1.partial_match('NIH0-1-1-3', 'NIH0-1-1')
    SPURIOUS_NIH_SCORE_1.partial_match('NIH-0-1-1-3', 'NIH-0-1-1')
    SPURIOUS_NIH_SCORE_1.partial_match('NIH 0-1-1-3', 'NIH 0-1-1')
    SPURIOUS_NIH_SCORE_1.partial_match('NIH 0 - 1 - 1 - 3', 'NIH 0 - 1 - 1')
    SPURIOUS_NIH_SCORE_1.no_match('NIH 2-3 palli', 'NIH 2-3')
    SPURIOUS_NIH_SCORE_1.test()
    
    SPURIOUS_NIH_SCORE_2 = RegexElement(rf'^N[iI]H({DASH}|{GAP})?[0-9]({GAP})?\(({GAP})?[0-9]({DASH})?[a-z],')
    SPURIOUS_NIH_SCORE_2.partial_match('NiH - 5(1 - c, 3 - 2, 4 - 2',   'NiH - 5(1 - c,')
    SPURIOUS_NIH_SCORE_2.partial_match('NiH - 5 (1 - c, 3 - 2, 4 - 2',  'NiH - 5 (1 - c,')
    SPURIOUS_NIH_SCORE_2.partial_match('NiH - 5 ( 1 - c, 3 - 2, 4 - 2', 'NiH - 5 ( 1 - c,')
    SPURIOUS_NIH_SCORE_2.partial_match('NiH-7(1b, 3-2, 4-4)', 'NiH-7(1b,')
    SPURIOUS_NIH_SCORE_2.partial_match('NiH - 7 (1b, 3-2, 4-4)', 'NiH - 7 (1b,')
    SPURIOUS_NIH_SCORE_2.test()


#===================================
#   RegexPattern
#===================================

def test_regex_pattern_smoke():
    # Smoke tests for RegexPattern
    DECIMAL_FRACTION = RegexElement(r'(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+')
    DECIMAL_FRACTION.full_match('123')
    DECIMAL_FRACTION.full_match('012')
    DECIMAL_FRACTION.full_match('1.2')
    DECIMAL_FRACTION.full_match('1,2')
    DECIMAL_FRACTION.full_match('0.12')
    DECIMAL_FRACTION.full_match('0,12')
    DECIMAL_FRACTION.full_match('1, 3')
    DECIMAL_FRACTION.full_match('1. 3')
    DECIMAL_FRACTION.full_match('1 , 3')
    DECIMAL_FRACTION.full_match('1 . 3')
    DECIMAL_FRACTION.no_match('XI.I')
    DECIMAL_FRACTION.no_match(',')
    DECIMAL_FRACTION.test()

    INTEGER_ABBREVIATION = RegexElement(r'(milj\.|milj)')
    SEMI_WORD_INTEGER = RegexPattern(r'{NUMBER}\s*{TEXT}').format(NUMBER=DECIMAL_FRACTION, TEXT=INTEGER_ABBREVIATION)
    SEMI_WORD_INTEGER.full_match('10 milj.')
    SEMI_WORD_INTEGER.full_match('1,5 milj.')
    SEMI_WORD_INTEGER.full_match('1 , 5milj.')
    SEMI_WORD_INTEGER.test()
    assert str(SEMI_WORD_INTEGER) == \
        r'(?:(?:(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+)\s*(?:(milj\.|milj)))'
        
    NUMBER_SLASH_NUMBER = RegexPattern(r'{NUMBER}\s*/\S*{NUMBER}').format(NUMBER=DECIMAL_FRACTION)
    NUMBER_SLASH_NUMBER.full_match('185/300')
    NUMBER_SLASH_NUMBER.full_match('18,5/30')
    NUMBER_SLASH_NUMBER.full_match('185/30.3')
    NUMBER_SLASH_NUMBER.test()
    assert str(NUMBER_SLASH_NUMBER) == \
        r'(?:(?:(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+)\s*/\S*(?:(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+))'

    INTEGER = RegexElement('[0-9]+')
    INTEGER.full_match('123')
    INTEGER.full_match('012')
    INTEGER.no_match('II')
    INTEGER.test()

    NUMERIC_SUM = RegexPattern(r'\(\s*{NUMBER}\s*\+\s*{NUMBER}\s*\)').format(NUMBER=INTEGER)
    NUMERIC_SUM.full_match('(20+5)')
    NUMERIC_SUM.no_match('20-5')
    NUMERIC_SUM.test()
    assert str(NUMERIC_SUM) == \
        r'(?:\(\s*(?:[0-9]+)\s*\+\s*(?:[0-9]+)\s*\))'

