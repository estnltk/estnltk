import json
from estnltk.text import words_sentences
from estnltk.syntax.syntax_preprocessing import SyntaxPreprocessing

def test_pipeline():

    fsToSyntFulesFile = '../files/tmorftrtabel.txt'
    subcatFile = '../files/abileksikon06utf.lx'

    pipeline = SyntaxPreprocessing(fs_to_synt=fsToSyntFulesFile, subcat=subcatFile)

    test_data = 'test_data_10.json'

    with open(test_data, 'r') as f:
        for line in f:
            file, t, expected = json.loads(line)
            t = words_sentences(t)
            _, result = pipeline.process_Text(t)
            assert result == expected