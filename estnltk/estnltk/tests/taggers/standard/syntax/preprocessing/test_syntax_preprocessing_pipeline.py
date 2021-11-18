"""Test syntax preprocessing pipeline, that is, MorphExtendedTagger + export_CG3

This file is inspired of
`koondkorpus-experiments/syntax_preprocessing_diff/syntax_preprocessing_devel_16_for_tokens_v01.py`

The data files for testing are created with the script in the bottom of this file.

"""
import json

from estnltk.common import abs_path
from estnltk import Text
from estnltk import Layer
from estnltk.taggers import MorphExtendedTagger
from estnltk.taggers import VabamorfTagger
from estnltk.converters import export_CG3

from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT

def create_single_token_text(token, analyses, morph_layer_name='morph_analysis'):
    """Construct a Text object containing one word, words layer, sentences layer and morph_analysis layer.

    """
    text = Text(token)
    words = Layer('words', text_object=text)
    words.add_annotation((0, len(token)))
    text.add_layer(words)

    sentences = Layer('sentences', text_object=text, enveloping='words')
    base_span = words[0].base_span
    sentences.add_annotation([base_span])
    text.add_layer(sentences)

    morph_attributes = list( VabamorfTagger.output_attributes )
    morph = Layer(morph_layer_name, attributes=morph_attributes, text_object=text, parent='words', ambiguous=True)
    for analysis in analyses:
        morph.add_annotation(base_span, **analysis)
    text.add_layer(morph)

    return text


def yield_tokens_analysis(file):
    """Reads the file of analysed tokens and yields the `(token, analysis)` tuples.

    """
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            token, analysis_tuples = json.loads(line.rstrip('\n'))
            analysis = [{'lemma': t[0],
                         'root': t[1],
                         'root_tokens': t[2],
                         'ending': t[3],
                         'clitic': t[4],
                         'partofspeech': t[5],
                         'form': t[6]} for t in analysis_tuples]
            if NORMALIZED_TEXT in VabamorfTagger.output_attributes:
                for a in analysis:
                    a[NORMALIZED_TEXT] = token
            yield token, analysis


def test_syntax_preprocessing_on_tokens():
    fs_to_synt_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/tmorftrtabel.txt')
    subcat_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/abileksikon06utf.lx')
    allow_to_remove_all = False

    tagger = MorphExtendedTagger(fs_to_synt_rules_file=fs_to_synt_rules_file,
                                 subcat_rules_file=subcat_rules_file,
                                 allow_to_remove_all=allow_to_remove_all)
    analysed_tokens_file = abs_path('tests/taggers/standard/syntax/preprocessing/analysed_tokens.txt')
    expected_cg3_file = abs_path('tests/taggers/standard/syntax/preprocessing/expected_cg3.txt')

    with open(expected_cg3_file, 'r', encoding='utf-8') as expected_cg3:
        for (token_a, analysis), expected in zip(yield_tokens_analysis(analysed_tokens_file), expected_cg3):
            token_b, cg3 = json.loads(expected)
            assert token_a == token_b, (token_a, token_b)
            text = create_single_token_text(token_a, analysis)
            tagger.tag(text)

            result = export_CG3(text)
            assert result == cg3, (result, cg3)


def test_syntax_preprocessing_with_customized_layer_names():
    fs_to_synt_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/tmorftrtabel.txt')
    subcat_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/abileksikon06utf.lx')
    allow_to_remove_all = False

    tagger = MorphExtendedTagger(output_layer='my_morph_extended',
                                 input_morph_analysis_layer='my_morph_analysis',
                                 fs_to_synt_rules_file=fs_to_synt_rules_file,
                                 subcat_rules_file=subcat_rules_file,
                                 allow_to_remove_all=allow_to_remove_all)
    analysed_tokens_file = abs_path('tests/taggers/standard/syntax/preprocessing/analysed_tokens.txt')
    expected_cg3_file = abs_path('tests/taggers/standard/syntax/preprocessing/expected_cg3.txt')

    with open(expected_cg3_file, 'r', encoding='utf-8') as expected_cg3:
        token_tests_passed = 0
        for (token_a, analysis), expected in zip(yield_tokens_analysis(analysed_tokens_file), expected_cg3):
            token_b, cg3 = json.loads(expected)
            assert token_a == token_b, (token_a, token_b)
            text = create_single_token_text(token_a, analysis, morph_layer_name='my_morph_analysis')
            tagger.tag(text)

            result = export_CG3(text, morph_layer='my_morph_extended')
            assert result == cg3, (result, cg3)
            token_tests_passed += 1
            if token_tests_passed > 99:
                # Test only on 100 first tokens 
                # ( the rest will be covered in test_syntax_preprocessing_on_tokens() )
                break


if __name__ == '__main__':
    '''This script can be used to create the data files for testing.
    run
    python estnltk/tests/test_syntax_preprocessing/test_syntax_preprocessing_pipeline.py

    '''
    import random
    # list here all tokens that should be included in the test files
    chosen_tokens = {'!', '"', '""', '?!', '...', '3-me', 'emba-kumba'}

    # there are 5000215 tokens, no more than 1000 are chosen
    chosen_lines = set(random.sample(range(5000215), 1000-len(chosen_tokens)))

    with open(abs_path('../../koondkorpus-experiments/temp/tokens_syntax_preprocessing_369f7c25.json')) as cg3_in, \
         open(abs_path('../../koondkorpus-experiments/temp/analyzed.json')) as analyses_in, \
         open(abs_path('tests/taggers/standard/syntax/preprocessing/analysed_tokens.txt'), 'w') as analyses_out, \
         open(abs_path('tests/taggers/standard/syntax/preprocessing/expected_cg3.txt'), 'w') as cg3_out:
        for i, (analysis, cg3) in enumerate(zip(analyses_in, cg3_in)):
            token, _ = json.loads(analysis)
            if i in chosen_lines or token in chosen_tokens:
                analyses_out.write(analysis)
                cg3_out.write(cg3)
            if i % 1000000 == 0:
                print(i, flush=True)
    print(i, 'done')
