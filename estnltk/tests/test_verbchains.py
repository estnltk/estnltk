# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text


class VerbchainTest(unittest.TestCase):

    def test_verbchain_1(self):
        text = Text('Kass, suur ja must, ei jooksnud üle tee.')
        phrase = Text('ei jooksnud')
        phrase.tag_verb_chains()
        text.tag_verb_chains()
        phrases = text.split_by('verb_chains')
        self.assertEqual(len(phrases), 1)

    def test_verbchain_2(self):
        text = Text('Samas on selge, et senine korraldus jätkuda ei saa.')
        text.tag_verb_chains()
        foundChains = text.verb_chains
        #print(foundChains)
        self.assertEqual(len(foundChains), 2)
        self.assertListEqual(foundChains[0]['roots'], ['ole'])
        self.assertListEqual(foundChains[1]['roots'], ['ei', 'saa', 'jätku'])
        
