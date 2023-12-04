import pytest

from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement


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
    GAP.full_match('  ')
    GAP.full_match(' \t')
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
    GAP.no_match(r'\n ')
    GAP.no_match(r' \n')
    GAP.no_match(r' \n ')
    eval_neg_results_dict = \
        GAP.evaluate_negative_examples().to_dict(orient='split', index=False)
    assert eval_neg_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [[r'\n', '+'], [r'\n ', '+'], [r' \n', '+'], [r' \n ', '+']]}
    # add mismatch
    GAP.no_match('  ')
    eval_neg_results_dict2 = \
        GAP.evaluate_negative_examples().to_dict(orient='split', index=False)
    assert eval_neg_results_dict2 == \
        {'columns': ['Example', 'Status'], 
         'data': [[r'\n', '+'], [r'\n ', '+'], [r' \n', '+'], [r' \n ', '+'], ['  ', 'F']]}


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


#
#  The following tests are based on:
#    https://github.com/estnltk/estnltk/blob/303f96312ab5b8e625bf019e965e5a70a5c8e47f/estnltk/estnltk/taggers/system/rule_taggers/regex_library/base_patterns.py
#

def test_regex_element_symbols():
    GAP = RegexElement(r'([ \t]+)')
    GAP.full_match(' ')
    GAP.full_match('\t')
    GAP.no_match('\n')
    GAP.full_match('  ')
    GAP.full_match(' \t')
    GAP.no_match('\n ')
    GAP.test()

    DASH = RegexElement(r'([ \t]*-[ \t]*)')
    DASH.full_match('-')
    DASH.full_match(' -')
    DASH.full_match('- ')
    DASH.full_match(' - ')
    DASH.full_match('  -')
    DASH.full_match('\t-')
    DASH.full_match('-\t')
    DASH.no_match('\n-')
    DASH.no_match('-\n')
    DASH.test()

    DIV = RegexElement(r'([ \t]*/[ \t]*)')
    DIV.full_match('/')
    DIV.full_match(' /')
    DIV.full_match('/ ')
    DIV.full_match(' / ')
    DIV.full_match('  /')
    DIV.full_match('\t/')
    DIV.full_match('/\t')
    DIV.no_match('\n/')
    DIV.no_match('/\n')
    DIV.test()

    EQ = RegexElement(r'([ \t]*=[ \t]*)')
    EQ.full_match('=')
    EQ.full_match('\t=')
    EQ.full_match(' = ')
    EQ.full_match('\t=')
    EQ.no_match('=\n')
    EQ.no_match('\n=')
    EQ.test()

    COLON = RegexElement(r'([ \t]*:[ \t]*)')
    COLON.full_match('\t:')
    COLON.full_match(' : ')
    COLON.full_match(':')
    COLON.full_match('\t:')
    COLON.no_match(':\n')
    COLON.no_match('\n:')
    COLON.test()

    COMA = RegexElement(r'([ \t]*,[ \t]*)')
    COMA.full_match(',')
    COMA.full_match('\t,')
    COMA.full_match(' , ')
    COMA.full_match('\t,')
    COMA.no_match(',\n')
    COMA.no_match('\n,')
    COMA.test()

    ARROW = RegexElement(r'([ \t]*(-*>)[ \t]*)')
    ARROW.full_match('>')
    ARROW.full_match('->')
    ARROW.full_match('-->')
    ARROW.full_match('--->')
    ARROW.full_match(' -> ')
    ARROW.full_match('\t-> ')
    ARROW.no_match(' ->\n')
    ARROW.test()

    ELLIPSE = RegexElement(r'([ \t]*(\.{2,4})[ \t]*)')

    SCORE_VALUE = RegexElement(r'[0-9]{1,2}')
    SCORE_VALUE.full_match('0')
    SCORE_VALUE.full_match('1')
    SCORE_VALUE.full_match('03')
    SCORE_VALUE.full_match('43')
    SCORE_VALUE.no_match('24 ')
    SCORE_VALUE.no_match('24p')
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
    SCORE_RANGE.no_match(' 3-4')
    SCORE_RANGE.no_match('3-4 ')
    SCORE_RANGE.partial_match('3 - 4p','3 - 4p')
    SCORE_RANGE.partial_match('3p-8p','3p-8p')
    SCORE_RANGE.partial_match('3 p - 4 p ','3 p - 4 p')
    SCORE_RANGE.partial_match('4 .... 10 ', '4 .... 10')
    SCORE_RANGE.no_match('3 palli - 4p')
    SCORE_RANGE.no_match('3-6p.')
    SCORE_RANGE.no_match('3-7p ')
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
    SCORE_RATIO_1.no_match(' 7/10 ')
    SCORE_RATIO_1.partial_match('7/ 10','7/ 10')
    SCORE_RATIO_1.partial_match('7 / 10','7 / 10')
    SCORE_RATIO_1.partial_match('7/10p','7/10p')
    SCORE_RATIO_1.partial_match('7/10 ','7/10')
    SCORE_RATIO_1.partial_match('7/10-st','7/10-st')
    SCORE_RATIO_1.partial_match('7/10 -st','7/10 -st')
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
    SCORE_RATIO.no_match('(20/30)')
    SCORE_RATIO.partial_match('saadud punkte 30-st 20 ','saadud punkte 30-st 20')
    SCORE_RATIO.test()

    TEXTUAL_SCORE_RATIO = RegexElement(rf'({SCORE_RATIO_1}|{SCORE_RATIO_2}|{SCORE_RATIO_3}' \
                          rf'|{SCORE_RATIO_4}|{SCORE_RATIO_5}|{SCORE_RATIO_6})')
    TEXTUAL_SCORE_RATIO.partial_match('20/30 punkti','20/30 punkti')
    TEXTUAL_SCORE_RATIO.partial_match('20 punkti 30-st.','20 punkti 30-st')
    TEXTUAL_SCORE_RATIO.partial_match('(20/30) ','(20/30)')
    TEXTUAL_SCORE_RATIO.partial_match('saadud punkte 30-st 20 ','saadud punkte 30-st 20')
    TEXTUAL_SCORE_RATIO.test()