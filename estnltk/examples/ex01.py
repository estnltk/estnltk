'''
Read in a A&A TEI corpus and perform some operations:

1. show top word counts
2. show top lemma counts
3. show top lemma counts after removing stopwords
4. show top lemma counts for adjectives
'''

from estnltk.core import AA_PATH
from estnltk.teicorpus import parse_tei_corpora, parse_tei_corpus
from estnltk.corpus import *
from pprint import pprint

import os

corp_path = os.path.join(AA_PATH, 'tea_AA_03_1.tasak.xml')

corp = Corpus.construct(parse_tei_corpus(corp_path))
pprint (corp.documents())
