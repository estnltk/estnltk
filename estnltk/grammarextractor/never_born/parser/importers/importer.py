# -*- coding: utf-8 -*-
"""
Module defining the interface for Grammar Importers.

As grammars can define import statements, it is important to specify, where to look for
these grammars. For instance, one might load the grammar from memory, file or even a database.

"""
from __future__ import unicode_literals, print_function, absolute_import

from ...exceptions import GrammarImportError


class Importer(object):

    def import_grammar(self, grammarname):
        raise GrammarImportError('No grammars found!')

