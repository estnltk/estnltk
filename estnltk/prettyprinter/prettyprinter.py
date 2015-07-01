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

from estnltk import Text


class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""
    def __init__(self, **kwargs):
        variables = {'color': 'black', 'background': 'white', 'font': 'serif', 'weight': 'normal',
                     'italics': 'normal', 'underline': 'normal', 'size': 'normal', 'tracking': 'normal'}
        for k,v in kwargs.items():
            print(k, v)
        self.color = variables['color']
        self.background = variables['background']
        self.font = variables['font']
        self.weight = variables['weight']
        self.italics = variables['italics']
        self.underline = variables['underline']
        self.size = variables['size']
        self.tracking = variables['tracking']
        self.text=kwargs['text']
        return

    def render(self, text):
        text = Text(text)
        return text

    @property
    def css(self):
        """The CSS of the prettyprinter."""
        return ''
kwargs={'text': "mis see on", 'vorming': ["a1", "a2"]}
p1=PrettyPrinter(**kwargs)
print(p1.text)
