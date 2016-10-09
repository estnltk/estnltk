import json

from estnltk.text import words_sentences
from estnltk.syntax.syntax_preprocessing import SyntaxPreprocessing


fsToSyntFulesFile = '/home/paul/workspace/estnltk/estnltk/syntax/files/tmorftrtabel.txt'
subcatFile = '/home/paul/workspace/estnltk/estnltk/syntax/files/abileksikon06utf.lx'

pipeline = SyntaxPreprocessing( fs_to_synt=fsToSyntFulesFile, subcat=subcatFile )

test_data = 'test_data.json'

with open(test_data, 'r') as f:
    for line in f:
        t, expected = json.loads(line)
        t = words_sentences(t)
        result = pipeline.process_Text(t)
        print(result == expected)
        if result != expected:
            for r, e in zip(result, expected):
                if r != e:
                    print(r, e)
                    break
            continue  