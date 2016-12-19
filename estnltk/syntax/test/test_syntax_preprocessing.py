import json
from estnltk.text import words_sentences
from estnltk.syntax.syntax_preprocessing import SyntaxPreprocessing

def test_pipeline():

    fsToSyntFulesFile = '../../rewriting/syntax_preprocessing/rules_files/tmorftrtabel.txt'
    subcatFile = '../../rewriting/syntax_preprocessing/rules_files/abileksikon06utf.lx'
    subcat_extra_file = '../../rewriting/syntax_preprocessing/rules_files/abileksikon_extra.lx'

    pipeline = SyntaxPreprocessing(fs_to_synt=fsToSyntFulesFile, 
                                   subcat=subcatFile, 
                                   subcat_extra = subcat_extra_file)

    test_data = 'test_data_10.json'
    # this file contains 10 texts from koondkorpus and the output of previous 
    # version of syntax_preprocessing
    with open(test_data, 'r') as f:
        for line in f:
            file, t, expected = json.loads(line)
            t = words_sentences(t)
            _, result = pipeline.process_Text(t)
            assert result == expected

    test_data = 'test_data_coverage_85.json'
    # processing the text in this file covers all relevant lines of
    # previous version of syntax_preprocessing
    with open(test_data, 'r') as f:
        for line in f:
            file, t, expected = json.loads(line)
            t = words_sentences(t)
            _, result = pipeline.process_Text(t)
            assert result == expected