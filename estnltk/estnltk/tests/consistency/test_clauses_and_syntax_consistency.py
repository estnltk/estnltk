import pytest
import os.path
from collections import defaultdict

from estnltk import Text
from estnltk import Layer
from estnltk.common import abs_path
from estnltk.converters import json_to_text

from estnltk.consistency.clauses_and_syntax_consistency import detect_clause_errors

detect_clause_errors_input_file = \
    abs_path('tests/consistency/test_data_detect_clause_errors.jsonl')

@pytest.mark.skipif(not os.path.exists(detect_clause_errors_input_file),
                    reason="missing input file {!r}".format(detect_clause_errors_input_file))
def test_detect_clause_errors_with_syntax():
    # Test that potential clause errors can be detected with syntax in the test corpus
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    problems_found = defaultdict(int)
    with open(detect_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                assert syntax_layer in text_obj.layers
                assert clauses_layer in text_obj.layers
                assert sentences_layer in text_obj.layers
                errors_layer = detect_clause_errors( text_obj, clauses_layer=clauses_layer, 
                                                               syntax_layer=syntax_layer,
                                                               sentences_layer=sentences_layer,
                                                               debug_output=False,
                                                               status=problems_found )
                assert len(errors_layer) > 0
    assert dict(problems_found) == {'attributive_kes_embedded_clause_wrong_end': 11, 
                                    'attributive_mis_clause_wrong_end': 5, 
                                    'attributive_kes_clause_wrong_end': 3, 
                                    'attributive_kus_embedded_clause_wrong_end': 3, 
                                    'attributive_mis_embedded_clause_wrong_end': 19, 
                                    'attributive_millal_embedded_clause_wrong_end': 1, 
                                    'attributive_kuidas_embedded_clause_wrong_end': 1}

