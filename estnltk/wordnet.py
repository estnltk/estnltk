# -*- coding: utf-8 -*-

import os, sys
from core import JsonPaths

_MY_DIR = os.path.dirname(__file__)

sys.path.insert(1,'../wordnet')

import wn

class Wordnet(object):
    
  def __init__(self):
    pass
    
  def __call__(self, corpus, **kwargs):
    pass
    
  def annotate_synsets(self, corpus):
    analysis_matches = JsonPaths.analysis.find(corpus)
    
    for analysis in analysis_matches:
      for candidate in analysis:
	candidate['wordnet'] = {'synsets':[synset.id for synset in wn.synsets(candidate['lemma'],pos=candidate['partofspeech'])]}
