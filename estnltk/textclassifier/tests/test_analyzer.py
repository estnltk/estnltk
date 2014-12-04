# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.textclassifier.analyzer import SimpleTextAnalyzer
from estnltk.textclassifier.synunifier import SynUnifier

import unittest


class AnalyzerTest(unittest.TestCase):

    def test_analysis(self):
        an = SimpleTextAnalyzer(self.unifier())
        lemmas = an(self.sentence())
        self.assertSetEqual(set(lemmas), self.lemmas())

    def unifier(self):
        unifier = SynUnifier()
        unifier.add_synset(['valgus', 'heledus'])
        return unifier

    def sentence(self):
        return 'Valgus on sama, mis heledus.'

    def lemmas(self):
        return set(['valk', 'valguma', 'valgus', 'sama', 'valgus'])

