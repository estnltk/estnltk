import json

from estnltk.text import words_sentences
from estnltk.syntax.syntax_preprocessing import SyntaxPreprocessing


fsToSyntFulesFile = '/home/paul/workspace/estnltk/estnltk/syntax/files/tmorftrtabel.txt'
subcatFile = '/home/paul/workspace/estnltk/estnltk/syntax/files/abileksikon06utf.lx'

pipeline = SyntaxPreprocessing( fs_to_synt=fsToSyntFulesFile, subcat=subcatFile )

test_data = 'test_data_10.json'

not_ok = []
with open(test_data, 'r') as f:
    for i, line in enumerate(f):
        print(i, end=' ', flush=True)
        file, t, expected = json.loads(line)
        print(file, end=' ' * (40 - len(file)), flush=True)
        t = words_sentences(t)
        _, result = pipeline.process_Text(t)
        if result == expected:
            print('OK')
        else:
            not_ok.append(i)
            print('Not OK. First mismatching line:')
            for r, e in zip(result, expected):
                if r != e:
                    print(r, e)
                    break
            continue
if not_ok:
    print('not ok lines:', not_ok)
else:
    print('Success!')