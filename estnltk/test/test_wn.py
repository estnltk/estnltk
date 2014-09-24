# -*- coding: utf-8 -*-

import unittest
import sys

sys.path.insert(1,'../../wordnet/')

import wn

class SynsetOffsetQueryTest(unittest.TestCase):
  
  def test_empty_query(self):
    self.assertTrue(wn._get_synset_offsets([]) == [])