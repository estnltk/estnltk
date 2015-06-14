# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
"""
  Notes
  ----
    Tests must be updated if wordnet file changes. Tests made for wordnet version kb69-a.
    
"""

import unittest
import sys, os

from ..wordnet import wn, eurown


class InternalSynsetOffsetQueryTest(unittest.TestCase):
 
  def test_empty_query(self):
    self.assertListEqual(wn._get_synset_offsets([]),[])
    
  def test_multiple_single_element_queries(self):
    idx_offset_pairs = [(1,111),(4967,12606307),(12672,26079737),(34800,58069170),(65518,91684951)]
    
    for i in range(len(idx_offset_pairs)):
      self.assertListEqual(wn._get_synset_offsets([idx_offset_pairs[i][0]]),[idx_offset_pairs[i][1]]) 
    
  def test_ordered_multiple_element_query(self):
    idx_offset_pairs = [(7,20473),(5421,13372490),(21450,39305206),(41785,66707187)]
    
    self.assertListEqual(wn._get_synset_offsets([idx_offset_pair[0] for idx_offset_pair in idx_offset_pairs]),[idx_offset_pair[1] for idx_offset_pair in idx_offset_pairs])
    
  def test_unordered_multiple_element_query(self):
    idx_offset_pairs = [(21450,39305206),(5421,13372490),(7,20473),(41785,66707187)]
    
    result = wn._get_synset_offsets([idx_offset_pair[0] for idx_offset_pair in idx_offset_pairs])
    
    self.assertTrue(all(offset in result for offset in [idx_offset_pair[1] for idx_offset_pair in idx_offset_pairs]))    

class SynsetKeyTest(unittest.TestCase):
  
  def test_key_derivation(self):
    lit,pos,sense = "test",'n',7
    variant = eurown.Variant(literal=lit,sense=sense)
    variants = eurown.Variants()
    variants.append(variant)
    raw_synset = eurown.Synset(pos=pos, variants=variants)

    self.assertEqual(wn._get_key_from_raw_synset(raw_synset),"%s.%s.%02d"%(lit,pos,sense))

class InternalSynsetQuery(unittest.TestCase):
  
  def test_empty_query(self):
    self.assertListEqual(wn._get_synsets([]),[])

  def test_single_element_query(self):
    synset_id,synset_offset,literal,pos,sense = 6,16983,'mõjutamine','n',2
    
    # todo: instead of comparing string representation, compare
    # literal, pos and sense variables directly
    self.assertEqual(wn._get_synsets([synset_offset])[0].id,synset_id)
"""

class SynsetQuery(unittest.TestCase):
  
  def test_synset_query(self):
    synset_id,synset_offset,literal,pos,sense = 6,16983,'mõjutamine','n',2
    
    synset_key = "%s.%s.%02d"%(literal,pos,sense)
    
    synset = wn.synset(synset_key)
    
    self.assertEqual(synset.id, synset_id)
    self.assertEqual(synset.name, synset_key)

"""
class SynsetsQuery(unittest.TestCase):
  
  def test_synsets_query(self):
    literal = 'aju'
    synset_ids = (10433,10434,12095,44798)

    self.assertTrue(all(synset.id in synset_ids for synset in wn.synsets(literal)))

class AllSynsetsQuery(unittest.TestCase):
  pass
  
  #def test_all_adverbs_query(self):
    #self.assertEqual(len(wn.all_synsets('b')),2244)

  #def test_all_adjectives_query(self):
    #self.assertEqual(len(wn.all_synsets('a')),3076)

  #def test_all_verbs_query(self):
    #self.assertEqual(len(wn.all_synsets('v')),5748)

  #def test_all_nouns_query(self):
    #self.assertEqual(len(wn.all_synsets('n')),54449)

class LemmaQuery(unittest.TestCase):
  
  def test_lemma_query(self):
    lemma_key = "kolask.n.01.elevant"
    self.assertTrue(wn.lemma(lemma_key).name,"elevant")

class AllLemmasQuery(unittest.TestCase):
  
  def test_all_lemmas_query(self):
    result = wn.lemmas("kiiresti")
    self.assertTrue(len(result),1)
    self.assertTrue(result[0].name,"kiiresti")

class MorphyTest(unittest.TestCase):
  
  def test_morphy(self):
    self.assertTrue(wn.morphy("karud"),"karu")

class Synset(unittest.TestCase):
  
  def test_get_related_synsets(self):
    ahel_synset = wn.synset("ahel.n.02")
    
    hyperonyms = ahel_synset.get_related_synsets('has_hyperonym')
    self.assertEqual(hyperonyms[0].name,'rida.n.01')
    
    hyponyms = ahel_synset.get_related_synsets('has_hyponym')
    self.assertEqual(hyponyms[0].name,'põhjusahel.n.01')
    self.assertEqual(hyponyms[1].name,'mäeahelik.n.01')

  def test_closure(self):
    real_ancestor_hyperonyms = [(293,'vahend.n.02'),(248,'asi.n.04'),(693,'objekt.n.01'),(8787,'olev.n.02')]
    real_ancestor_ids = [id_name[0] for id_name in real_ancestor_hyperonyms]
    
    hoob_synset = wn.synset("hoob.n.01")
    ancestor_hyperonyms = hoob_synset.closure('has_hyperonym')
    
    self.assertEqual(len(ancestor_hyperonyms),len(real_ancestor_hyperonyms))
    self.assertTrue(all(ancestor.id in real_ancestor_ids for ancestor in ancestor_hyperonyms))
  
  def test_closure_with_custom_depth(self):
    real_ancestor_hyperonyms = [(293,'vahend.n.02')]
    real_ancestor_ids = [id_name[0] for id_name in real_ancestor_hyperonyms]
    
    hoob_synset = wn.synset("hoob.n.01")
    ancestor_hyperonyms = hoob_synset.closure('has_hyperonym',depth=1)
    
    self.assertEqual(len(ancestor_hyperonyms),len(real_ancestor_hyperonyms))
    self.assertTrue(all(ancestor.id in real_ancestor_ids for ancestor in ancestor_hyperonyms))
  
  def test_shortest_path_distance_to_itself(self):
    source_synset = wn.synset('hulkuma.v.01')
    target_synset = wn.synset('hulkuma.v.01')

    self.assertEqual(source_synset._shortest_path_distance(target_synset),0)

  def test_shortest_path_distance_to_parent(self):
    source_synset = wn.synset('hiphop.n.01')
    target_synset = wn.synset('tantsustiil.n.01')

    self.assertEqual(source_synset._shortest_path_distance(target_synset),1)

  def test_shortest_path_distance_to_sibling(self):
    source_synset = wn.synset('hobu.n.01')
    target_synset = wn.synset('eesel.n.01')

    self.assertEqual(source_synset._shortest_path_distance(target_synset),2)

  def test_path_similarity_with_itself(self):
    source_synset = wn.synset('ilming.n.02')
    target_synset = wn.synset('fenomen.n.01')

    self.assertEqual(source_synset.path_similarity(target_synset),1)

  def test_path_similarity_with_unconnected(self):
    pass # would take too much time
  
  def test_path_similarity_with_sibling(self):
    source_synset = wn.synset('kaarhall.n.01')
    target_synset = wn.synset('näitusehall.n.01')
    
    self.assertEqual(source_synset.path_similarity(target_synset), 1.0/3)
  
  def test_root_min_depth(self):
    synset = wn.synset('olev.n.02')
    
    self.assertEqual(synset._min_depth(),0)

  def test_arbitrary_min_depth(self):
    synset = wn.synset('vahend.n.02')
    
    self.assertEqual(synset._min_depth(),3)

