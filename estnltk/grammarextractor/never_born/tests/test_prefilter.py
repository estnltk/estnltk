# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os
import codecs

from ...core import PACKAGE_PATH
from ..parser import GrammarParser

TEST_GRAMMARS_PATH = os.path.join(PACKAGE_PATH, 'grammarextractor', 'grammars', 'test')


def load_grammar(fnm):
    fnm = os.path.join(TEST_GRAMMARS_PATH, fnm)
    with codecs.open(fnm, 'rb', 'utf-8') as f:
        return GrammarParser(f.read()).grammar


class PrefilterTest(unittest.TestCase):

    def test_dictionaries(self):
        grammar = load_grammar('prefilter_dictionaries')
        constraints = grammar.constraints

        # expected values
        case_sensitive_words = {'Õunad', 'Kapsad'}
        case_insensitive_words = {'pihlakad', 'mustsõstrad'}
        lemmas = {'peet', 'porgand'}
        self.assertSetEqual(case_sensitive_words, constraints.case_sensitive_words)
        self.assertSetEqual(case_insensitive_words, constraints.case_insensitive_words)
        self.assertSetEqual(lemmas, constraints.lemmas)
        self.assertEqual(False, constraints.all)

    def test_regex(self):
        grammar = load_grammar('prefilter_regex')
        constraints = grammar.constraints

        self.assertSetEqual(set(), constraints.case_sensitive_words)
        self.assertSetEqual(set(), constraints.case_insensitive_words)
        self.assertEqual(True, constraints.all)

    def test_production(self):
        grammar = load_grammar('prefilter_production')
        constraints = grammar.constraints

        # expected values
        case_sensitive_words = {'Tallinn', 'Tartu', 'Rapla'}
        lemmas = {'olema', 'tähendama'}
        all = False

        self.assertSetEqual(case_sensitive_words, constraints.case_sensitive_words)
        self.assertSetEqual(set(), constraints.case_insensitive_words)
        self.assertSetEqual(lemmas, constraints.lemmas)
        self.assertEqual(False, all)
