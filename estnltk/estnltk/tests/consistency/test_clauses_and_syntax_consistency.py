import pytest
import os.path
from collections import defaultdict

from estnltk_core.layer_operations import join_texts

from estnltk import Text
from estnltk import Layer
from estnltk.common import abs_path
from estnltk.converters import json_to_text

from estnltk.consistency.clauses_and_syntax_consistency import detect_clause_errors
from estnltk.consistency.clauses_and_syntax_consistency import fix_clause_errors_with_syntax

attributive_clause_errors_input_file = \
    abs_path('tests/consistency/test_data_attributive_clause_errors.jsonl')

disconnected_root_clause_errors_input_file = \
    abs_path('tests/consistency/test_data_disconnected_root_clause_errors.jsonl')

# =======================================================
#  Detect errors
# =======================================================

@pytest.mark.skipif(not os.path.exists(attributive_clause_errors_input_file),
                    reason="missing input file {!r}".format(attributive_clause_errors_input_file))
def test_detect_attributive_clause_errors_with_syntax__static():
    # Test that potential attributive clause errors can be detected with syntax in the test corpus
    # Note: this test works on static/pre-annotated input data
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    problems_found = defaultdict(int)
    with open(attributive_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        docs = 0
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                docs += 1
                assert syntax_layer in text_obj.layers
                assert clauses_layer in text_obj.layers
                assert sentences_layer in text_obj.layers
                errors_layer = detect_clause_errors( text_obj, clauses_layer=clauses_layer, 
                                                               syntax_layer=syntax_layer,
                                                               sentences_layer=sentences_layer,
                                                               debug_output=False,
                                                               status=problems_found )
                # There are errors in the first 100 sentences, but no errors in the last 5 sentences
                assert len(errors_layer) > 0 or docs > 100
    assert dict(problems_found) == {'attributive_mis_embedded_clause_wrong_end': 37, 
                                    'attributive_kes_clause_wrong_end': 5, 
                                    'attributive_kes_embedded_clause_wrong_end': 35, 
                                    'attributive_kus_embedded_clause_wrong_end': 8, 
                                    'attributive_kuidas_embedded_clause_wrong_end': 8, 
                                    'attributive_millal_embedded_clause_wrong_end': 1, 
                                    'attributive_mis_clause_wrong_end': 4, 
                                    'attributive_kas_embedded_clause_wrong_end': 1, 
                                    'attributive_kuhu_embedded_clause_wrong_end': 1}

@pytest.mark.skipif(not os.path.exists(disconnected_root_clause_errors_input_file),
                    reason="missing input file {!r}".format(disconnected_root_clause_errors_input_file))
def test_detect_disconnected_root_clause_errors_with_syntax__static():
    # Test that potential disconnected root clause errors can be detected with syntax in the test corpus
    # Note: this test works on static/pre-annotated input data
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    problems_found = defaultdict(int)
    with open(disconnected_root_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        docs = 0
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                docs += 1
                assert syntax_layer in text_obj.layers
                assert clauses_layer in text_obj.layers
                assert sentences_layer in text_obj.layers
                errors_layer = detect_clause_errors( text_obj, clauses_layer=clauses_layer, 
                                                               syntax_layer=syntax_layer,
                                                               sentences_layer=sentences_layer,
                                                               debug_output=False,
                                                               status=problems_found )
                # There are errors in the first 100 sentences
                assert len(errors_layer) > 0 or docs > 100
    assert dict(problems_found) == {'disconnected_root_clause': 100}

# =======================================================
#  Fix errors
# =======================================================

# Tests whether two clause layers are equal in terms of having the same annotations
def clause_layers_match( layer_a, layer_b ):
    a_words = [[(w.start, w.end) for w in cl] for cl in layer_a]
    b_words = [[(w.start, w.end) for w in cl] for cl in layer_b]
    matched_b_words = []
    for cid_a, cl_a in enumerate( a_words ):
        match_found = False
        for cid_b, cl_b in enumerate( b_words ):
            if cl_a == cl_b:
                if layer_a[cid_a].annotations != \
                    layer_b[cid_b].annotations:
                    return False
                match_found = True
                matched_b_words.append(cid_b)
                break
        if not match_found:
            return False
    if len(matched_b_words) != len(b_words):
        return False
    return True

@pytest.mark.skipif(not os.path.exists(attributive_clause_errors_input_file),
                    reason="missing input file {!r}".format(attributive_clause_errors_input_file))
def test_fix_attributive_clause_errors_with_syntax__static():
    # Test that potential attributive clause errors can be fixed with syntax in the test corpus
    # Note: this test works on static/pre-annotated input data
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    clause_fixes_layer = 'fixed_clauses'
    with open(attributive_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        docs = 0
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                docs += 1
                assert syntax_layer in text_obj.layers
                assert clauses_layer in text_obj.layers
                assert sentences_layer in text_obj.layers
                clauses_before_fix = len(text_obj[clauses_layer])
                words_before_fix = sorted([(w.start, w.end) for cl in text_obj[clauses_layer] for w in cl])
                fixed_layer = fix_clause_errors_with_syntax( text_obj, clauses_layer=clauses_layer, 
                                                             syntax_layer=syntax_layer,
                                                             sentences_layer=sentences_layer,
                                                             output_layer=clause_fixes_layer)
                assert fixed_layer.name == clause_fixes_layer
                assert fixed_layer.attributes == text_obj[clauses_layer].attributes
                assert fixed_layer.enveloping == text_obj[clauses_layer].enveloping
                words_after_fix = sorted([(w.start, w.end) for cl in fixed_layer for w in cl])
                clauses_after_fix = len(fixed_layer)
                # Assert that no word went missing during the fix
                assert words_before_fix == words_after_fix
                if docs <= 100:
                    # Assert that fixes change clause structure in the first 100 sentences
                    assert not clause_layers_match( text_obj[clauses_layer], fixed_layer )
                else:
                    # Assert that nothing is changed in the last 5 sentences (correct sentences)
                    assert clause_layers_match( text_obj[clauses_layer], fixed_layer )

@pytest.mark.skipif(not os.path.exists(disconnected_root_clause_errors_input_file),
                    reason="missing input file {!r}".format(disconnected_root_clause_errors_input_file))
def test_fix_disconnected_root_clause_errors_with_syntax__static():
    # Test that potential disconnected root clause errors can be fixed with syntax in the test corpus
    # Note: this test works on static/pre-annotated input data
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    clause_fixes_layer = 'fixed_clauses'
    with open(disconnected_root_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        docs = 0
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                docs += 1
                assert syntax_layer in text_obj.layers
                assert clauses_layer in text_obj.layers
                assert sentences_layer in text_obj.layers
                clauses_before_fix = len(text_obj[clauses_layer])
                words_before_fix = sorted([(w.start, w.end) for cl in text_obj[clauses_layer] for w in cl])
                fixed_layer = fix_clause_errors_with_syntax( text_obj, clauses_layer=clauses_layer, 
                                                             syntax_layer=syntax_layer,
                                                             sentences_layer=sentences_layer,
                                                             output_layer=clause_fixes_layer)
                assert fixed_layer.name == clause_fixes_layer
                assert fixed_layer.attributes == text_obj[clauses_layer].attributes
                assert fixed_layer.enveloping == text_obj[clauses_layer].enveloping
                words_after_fix = sorted([(w.start, w.end) for cl in fixed_layer for w in cl])
                clauses_after_fix = len(fixed_layer)
                # Assert that no word went missing during the fix
                assert words_before_fix == words_after_fix
                # Assert that clauses have been changed
                assert not clause_layers_match( text_obj[clauses_layer], fixed_layer )
                # Assert that there is one clause less
                assert clauses_after_fix + 1 == clauses_before_fix


@pytest.mark.skipif(not os.path.exists(attributive_clause_errors_input_file),
                    reason="missing input file {!r}".format(attributive_clause_errors_input_file))
def test_fix_attributive_clause_errors_with_syntax_multisentence__static():
    # Test that potential attributive clause errors can be fixed with syntax in a multisentence text object
    # Note: this test works on static/pre-annotated input data
    clauses_layer   = 'v169_clauses'
    sentences_layer = 'v166_sentences'
    syntax_layer    = 'v168_stanza_syntax'
    clause_fixes_layer = 'fixed_clauses'
    # Collect last 10 sentences from the input file
    last_sentences = []
    with open(attributive_clause_errors_input_file, 'r', encoding='utf-8') as in_f:
        docs = 0
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                text_obj = json_to_text(line)
                docs += 1
                if docs > 95:
                   last_sentences.append( text_obj ) 
    # Create a single Text object from last sentences
    mono_text = join_texts( last_sentences )
    assert syntax_layer in mono_text.layers
    assert clauses_layer in mono_text.layers
    assert sentences_layer in mono_text.layers
    assert len(mono_text[sentences_layer]) == 10
    # Fix clauses layer in mono_text
    fixed_layer = fix_clause_errors_with_syntax( mono_text, clauses_layer=clauses_layer, 
                                                            syntax_layer=syntax_layer,
                                                            sentences_layer=sentences_layer,
                                                            output_layer=clause_fixes_layer )
    for sent_id, sent in enumerate(mono_text[sentences_layer]):
        clauses_bf_fix = \
            [cl for cl in mono_text[clauses_layer] if sent.start <= cl.start and cl.end <= sent.end]
        clauses_af_fix = \
            [cl for cl in fixed_layer if sent.start <= cl.start and cl.end <= sent.end]
        assert len(clauses_bf_fix) > 0
        assert len(clauses_af_fix) > 0
        bf_words = [[(w.start, w.end) for w in cl] for cl in clauses_bf_fix]
        af_words = [[(w.start, w.end) for w in cl] for cl in clauses_af_fix]
        if sent_id < 5:
            # There should be changes in the first 5 sentences
            assert bf_words != af_words
        else:
            # Nothing should be different in the last 5 sentences
            assert bf_words == af_words
