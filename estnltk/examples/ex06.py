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
import json

corp_path = os.path.join(AA_PATH, 'tea_AA_03_1.tasak.xml')

corp = parse_tei_corpus(corp_path)

from estnltk.corpus import Corpus
from estnltk.morf import PyVabamorfAnalyzer
from estnltk.ner import NerTagger

analyzer = PyVabamorfAnalyzer()
tagger = NerTagger()

analyzer(corp, inplace=True)
tagger(corp, inplace=True)

pprint (zip(corp.lemmas, corp.labels))
