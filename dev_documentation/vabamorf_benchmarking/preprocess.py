#  Preprocessing for speed benchmarking.
#  Loads XML files as Texts with the default tokenization and saves Texts as json files
#  Requires: directory 'xml_data' containing input XML files
#            directory 'json_data' for output JSON files

import os, os.path
import re
from datetime import datetime
from collections import defaultdict

from estnltk.corpus_processing.parse_koondkorpus import parse_tei_corpus

from estnltk import Text
from estnltk.converters import text_to_json

in_dir  = 'xml_data'
out_dir = 'json_data'

assert os.path.isdir(in_dir), '(!) Missing input directory {!r}'.format(in_dir)
assert os.path.isdir(out_dir), '(!) Missing output directory {!r}'.format(out_dir)

word_counts = defaultdict(int)
sentence_counts = defaultdict(int)
files = 0
texts = 0
start_time = datetime.now()
for fname in os.listdir(in_dir):
    if fname.endswith('xml'):
        print(fname, end='  ')
        fpath  = os.path.join(in_dir, fname)
        target = None
        ttype  = None
        if fname.startswith('aja_'):
            ttype = 'aja'
            target='artikkel'
        if fname.startswith('tea_'):
            ttype = 'tea'
            target='artikkel'
        if fname.startswith('ilu_'):
            ttype = 'ilu'
            target='tervikteos'
        assert ttype is not None
        assert target
        local_texts = 0
        for text_obj in parse_tei_corpus( fpath,target=[target],add_tokenization=True,preserve_tokenization=True ):
            word_counts[ttype] += len(text_obj['words'])
            sentence_counts[ttype] += len(text_obj['sentences'])
            texts += 1
            local_texts += 1
            if os.path.exists(out_dir):
                out_fname = fname.replace('.xml', ('_{:03d}'.format(local_texts))+'.json')
                outpath = os.path.join(out_dir, out_fname)
                #print('-->',out_fname, end='  ')
                text_to_json(text_obj, file=outpath)
        assert local_texts > 0, '(!) No texts found from '+fname
        files += 1
        print()

print()
print('Total processing time: {}'.format(datetime.now() - start_time))
print()
print('===========================')
print('  S t a t i s t i c s      ')
print('===========================')
print()
print('Files: ',files)
print('Texts: ',texts)
print()
for key in sorted(sentence_counts.keys()):
    print(key, '#sentences:',sentence_counts[key])
print('Total #sentences:', sum([sentence_counts[k] for k in sentence_counts.keys()]))
print()
for key in sorted(word_counts.keys()):
    print(key, '#words:',word_counts[key])
print('Total #words:', sum([word_counts[k] for k in word_counts.keys()]))