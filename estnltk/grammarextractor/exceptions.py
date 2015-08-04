# -*- coding: utf-8 -*-
"""
Define grammarextractor exceptions.
"""
from __future__ import unicode_literals, print_function, absolute_import


class ParseException(Exception):
    """Exception that should be used for any kind of parsing problem in grammarextractor."""
    pass


class GrammarImportError(Exception):
    """Exception for grammar import failures."""
    pass

