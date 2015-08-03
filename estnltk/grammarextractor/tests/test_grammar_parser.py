# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os
import codecs

from ...core import PACKAGE_PATH
from ..parser.parser import GrammarParser
from ..parser.importers import FileSystemImporter

TEST_GRAMMARS_PATH = os.path.join(PACKAGE_PATH, 'grammarextractor', 'grammars', 'test')


def load_grammar(fnm):
    fnm = os.path.join(TEST_GRAMMARS_PATH, fnm)
    with codecs.open(fnm, 'rb', 'utf-8') as f:
        return f.read()


class GrammarParserTest(unittest.TestCase):

    def test_datenums(self):
        parser = GrammarParser(load_grammar('datenums'))
        grammar = parser.get_grammar()

        # fetch some symbols
        grammar.get_symbol('Day')
        grammar.get_symbol('Month')
        grammar.get_symbol('Year')

        expected_exports = {'Month': [], 'Year': [], 'Day': []}
        self.assertDictEqual(expected_exports, grammar.exports)

    def test_date(self):
        importer = FileSystemImporter([TEST_GRAMMARS_PATH])
        parser = GrammarParser(load_grammar('date'), importer)
        grammar = parser.get_grammar()

        expected_exports = {'Date': [('Day', 'integer'), ('Month', 'real'), ('Year', 'string')]}
        self.assertDictEqual(expected_exports, grammar.exports)

