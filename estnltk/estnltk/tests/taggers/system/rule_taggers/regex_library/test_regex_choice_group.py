import re
import os
import os.path 
import tempfile
import pytest

from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList

#===================================
#   StringList
#===================================

def test_regex_string_list_to_str():
    # Regular StringList
    PALLITUS = StringList(['p', 'pall', 'punkt', 'palli', 'punkti', 'st', '-st', 'palli'])
    PALLITUS.full_match('p')
    PALLITUS.full_match('st')
    PALLITUS.full_match('-st')
    PALLITUS.full_match('palli')
    PALLITUS.full_match('pall')
    PALLITUS.full_match('punkt')
    PALLITUS.full_match('punkti')
    PALLITUS.partial_match('pallile','palli')
    PALLITUS.partial_match('pallist','palli')
    PALLITUS.test()
    assert str(PALLITUS) == r'(?:punkti|palli|punkt|pall|\-st|st|p)'


def test_regex_string_list_to_str_with_replacements():
    # Regular StringList with (simple) replacement:  'p' -> '[Pp]'
    PALLITUS2 = StringList(['p', 'pall', 'punkt', 'palli', 'punkti'], \
                            replacements={'p':'[Pp]'})
    assert str(PALLITUS2) == \
        r'(?:(?:[Pp])unkti|(?:[Pp])alli|(?:[Pp])unkt|(?:[Pp])all|(?:[Pp]))'
    # replacements cannot be added afterwards
    with pytest.raises(AttributeError) as attrib_err:
        # 'changing of the attribute replacements after initialization not allowed in StringList'
        PALLITUS2.replacements = {'a':'[Aa]'}
    # Regular StringList with a bit more complex replacement: ' ' -> '\s+'
    PALLITUS3 = StringList([' p', ' pall', ' punkt', ' palli', ' punkti'], \
                            replacements={' ':r'\s+'})
    assert str(PALLITUS3) == \
        r'(?:(?:\s+)punkti|(?:\s+)palli|(?:\s+)punkt|(?:\s+)pall|(?:\s+)p)'


def test_regex_string_list_evaluation():
    # StringList as choice group
    PALLITUS = StringList(['p', 'pall', 'punkt', 'palli', 'punkti', 'st', '-st', 'palli'])
    # Passing tests
    PALLITUS.full_match('p')
    PALLITUS.full_match('st')
    PALLITUS.full_match('-st')
    PALLITUS.full_match('palli')
    PALLITUS.full_match('pall')
    PALLITUS.full_match('punkt')
    PALLITUS.full_match('punkti')
    PALLITUS.partial_match('pallile','palli')
    PALLITUS.partial_match('pallist','palli')
    PALLITUS.no_match('boonust')
    PALLITUS.no_match('skoor')
    # Failing tests
    PALLITUS.full_match('punni')
    PALLITUS.no_match('punni')
    PALLITUS.partial_match('pallile', 'pallile')
    # Validate
    eval_pos_results_dict = \
        PALLITUS.evaluate_positive_examples().to_dict(orient='split', index=False)
    #print( eval_pos_results_dict )
    assert eval_pos_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['p', '+'], ['st', '+'], ['-st', '+'], ['palli', '+'], 
                  ['pall', '+'], ['punkt', '+'], ['punkti', '+'], ['punni', 'F']]}
    eval_neg_results_dict = \
        PALLITUS.evaluate_negative_examples().to_dict(orient='split', index=False)
    #print( eval_neg_results_dict )
    assert eval_neg_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['boonust', 'F'], ['skoor', '+'], ['punni', 'F']]}
    eval_extract_results_dict = \
        PALLITUS.evaluate_extraction_examples().to_dict(orient='split', index=False)
    #print( eval_extract_results_dict )
    assert eval_extract_results_dict == \
        {'columns': ['Example', 'Status'], 
         'data': [['pallile', '+'], ['pallist', '+'], ['pallile', 'F']]}


def test_regex_string_list_csv_writing_and_reading():
    PALLITUS = StringList([' p', ' pall', ' punkt', ' palli_', ' punkti_'], \
                           replacements={' ':r'\s*', 'p': '[Pp]', '_': '.?'})
    PALLITUS.full_match(' palli')
    PALLITUS.full_match('pall')
    PALLITUS.full_match('  punkt')
    PALLITUS.full_match(' punkti')
    PALLITUS.partial_match(' pallile', ' pallil')
    PALLITUS.partial_match('pallist', 'pallis')
    PALLITUS.test()
    #print(str(PALLITUS))
    with tempfile.TemporaryDirectory(suffix='csv_') as tmp_dir:
        # Export to CSV
        fpath = os.path.join(tmp_dir, 'string_list_1.csv')
        PALLITUS.to_csv(fpath)
        # Read from CSV (must use the same replacements)
        PALLITUS2 = StringList.from_file(fpath,
                        replacements={' ':r'\s*', 'p': '[Pp]', '_': '.?'})
        # Check that string representations of both StringList-s match
        assert str(PALLITUS) == str(PALLITUS2)
        # Check tests
        PALLITUS2.full_match(' palli')
        PALLITUS2.full_match('pall')
        PALLITUS2.full_match('  punkt')
        PALLITUS2.full_match(' punkti')
        PALLITUS2.partial_match(' pallile', ' pallil')
        PALLITUS2.partial_match('pallist', 'pallis')
        PALLITUS2.test()
        #print(str(PALLITUS2))

    # assert clean up
    assert not os.path.exists(fpath)

        
        

