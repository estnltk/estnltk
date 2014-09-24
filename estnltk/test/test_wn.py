# -*- coding: utf-8 -*-

"""
  Notes
  ----
    Tests must be updated if wordnet file changes. Tests made for wordnet version kb69-a.
    
"""

import unittest
import sys

sys.path.insert(1,'../../wordnet/')

import wn
import eurown

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
    
    self.assertEqual(str(wn._get_synsets([synset_offset])[0]),"Synset('%s.%s.%02d')"%(literal,pos,sense))
    
class SynsetQuery(unittest.TestCase):
  
  def test_synset_query(self):
    synset_id,synset_offset,literal,pos,sense = 6,16983,'mõjutamine','n',2
    
    synset_key = "%s.%s.%02d"%(literal,pos,sense)
    
    synset = wn.synset(synset_key)
    
    self.assertEqual(synset.id,synset_id)
    self.assertEqual(synset.name,synset_key)

class SynsetsQuery(unittest.TestCase):
  
  def test_synsets_query(self):
    literal = 'aju'
    synset_ids = (10433,10434,12095,44798)

    self.assertTrue(all(synset.id in synset_ids for synset in wn.synsets(literal)))

if __name__ == '__main__':
    unittest.main()