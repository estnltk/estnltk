# -*- coding: utf-8 -*-

import unittest
import sys

sys.path.insert(1,'../../wordnet/')

import wn

class SynsetOffsetQueryTest(unittest.TestCase):
  """
  Note
  ----
    Tests must be updated if wordnet file changes.
    
  """
  def test_empty_query(self):
    self.assertTrue(wn._get_synset_offsets([]) == [])
    
  def test_multiple_single_element_queries(self):
    idx_offset_pairs = [(1,111),(4967,12606307),(12672,26079737),(34800,58069170),(65518,91684951)]
    
    for i in range(len(idx_offset_pairs)):
      self.failUnlessEqual(wn._get_synset_offsets([idx_offset_pairs[i][0]]),[idx_offset_pairs[i][1]]) 
    
  def test_ordered_multiple_element_query(self):
    idx_offset_pairs = [(7,20473),(5421,13372490),(21450,39305206),(41785,66707187)]
    
    self.failUnlessEqual(wn._get_synset_offsets([idx_offset_pair[0] for idx_offset_pair in idx_offset_pairs]),[idx_offset_pair[1] for idx_offset_pair in idx_offset_pairs])
    
  def test_unordered_multiple_element_query(self):
    idx_offset_pairs = [(21450,39305206),(5421,13372490),(7,20473),(41785,66707187)]
    
    result = wn._get_synset_offsets([idx_offset_pair[0] for idx_offset_pair in idx_offset_pairs])
    
    self.assertTrue(all(offset in result for offset in [idx_offset_pair[1] for idx_offset_pair in idx_offset_pairs]))    
    
if __name__ == '__main__':
    unittest.main()