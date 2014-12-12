'''
Read in a A&A TEI corpus and perform some operations:
'''

from estnltk.core import AA_PATH
from estnltk.teicorpus import parse_tei_corpora, parse_tei_corpus
from estnltk.corpus import *
from pprint import pprint

import os
import json

# read a single XML file
corp_path = os.path.join(AA_PATH, 'tea_AA_03_1.tasak.xml')
corpus = parse_tei_corpus(corp_path)

# do something with the corpora
from estnltk.corpus import Corpus
from estnltk.morf import PyVabamorfAnalyzer
from estnltk.ner import NerTagger

# ner tag the corpus
analyzer = PyVabamorfAnalyzer()
tagger = NerTagger()
corpus = tagger(analyzer(corpus))

from nltk import FreqDist

entities = [ne.lemma for ne in corpus.named_entities]
print (entities)

