# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.

Deals with rendering Text instances as HTML.
"""
from __future__ import unicode_literals, print_function, absolute_import

try:
    from StringIO import cStringIO as StringIO
except ImportError: # Py3
    from io import StringIO

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape

from ..text import Text


class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""

    def __init__(self, **kwargs):
        pass

    def render(self, text):
        text = Text(text)
        return ''

    @property
    def css(self):
        """The CSS of the prettyprinter."""
        return ''

