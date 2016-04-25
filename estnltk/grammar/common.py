# -*- coding: utf-8 -*-
"""
This module defines some common imports and functions for grammar package.
"""
from __future__ import unicode_literals, print_function, absolute_import

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import regex as re
import sre_constants


valid_name_pattern = re.compile('^\w+$', re.UNICODE)


def is_valid_symbol_name(name):
    """Check if a name is suitable for a symbol."""
    return valid_name_pattern.match(name) is not None


def is_valid_regex(regex):
    """Function for checking a valid regex."""
    if len(regex) == 0:
        return False
    try:
        re.compile(regex)
        return True
    except sre_constants.error:
        return False


class GrammarException(Exception):
    """Exception that should be used for any kind of parsing problem in grammar."""
    pass
