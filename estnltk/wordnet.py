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
    
    analysis_matches = JsonPaths.analysis.find(corpus)

    for analysis in analysis_matches:
      for candidate in analysis:
	
	wordnet_obj = {}
	
	#TODO MAP TIMO POS TO KOM POS
	
	candidate_synsets = [({'id':synset.id},synset) for synset in wn.synsets(candidate['lemma'],pos=candidate['partofspeech'])]
	
	for synset_dict,synset in candidate_synsets:
	  
	  if 'pos' in kwargs:
	    if kwargs['pos']:
	      synset_dict['pos'] = synset.pos
	
	  if 'variants' in kwargs:
	    if kwargs['variants']:
	      variants = [({},variant) for variant in synset.get_variants()]
	      
	      for variant_dict,variant in variants:
		if 'var_literal' in kwargs:
		  if kwargs['var_literal']:
		    variant_dict['literal'] = variant.literal
		    
		if 'var_sense' in kwargs:
		  if kwargs['var_sense']:
		    variant_dict['sense'] = variant.sense
	      
		if 'var_definition' in kwargs:
		  if kwargs['var_definition']:
		    variant_dict['definition'] = variant.definition
	      
		if 'var_examples' in kwargs:
		  if kwargs['var_examples']:
		    variant_dict['examples'] = variant.examples
	      
	      synset_dict['variants'] = [variant_dict for variant_dict,_ in variants]
	 
	wordnet_obj['synsets'] = [synset_dict for synset_dict,_ in candidate_synsets]
	 
	if 'relations' in kwargs:
	  if len(kwargs['relations']):
	    
	    relations_dict = {}
	    
	    for relation_str in kwargs['relations']:
	      related_synsets = [({'id':synset.id},synset) for synset in synset.get_by_relation(relation_str)]
	      
	      relations_dict[relation_str] = [synset_dict for synset_dict,_ in related_synsets]
	 
	      #TODO satisfy timo via additional relation_synset annotations
	 
	  wordnet_obj['relations'] = relations_dict
	 
	candidate['wordnet'] = wordnet_obj
	
    
  def annotate_synsets(self, corpus):
    analysis_matches = JsonPaths.analysis.find(corpus)
    
    for analysis in analysis_matches:
      for candidate in analysis:
	candidate['wordnet'] = {'synsets':[synset.id for synset in wn.synsets(candidate['lemma'],pos=candidate['partofspeech'])]}
