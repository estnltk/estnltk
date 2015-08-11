# -*- coding: utf-8 -*-
'''This module defines HTML and CSS templates and markup-generating functions
that are required by PrettyPrinter to generate full HTML and CSS output.
'''
from __future__ import unicode_literals, print_function, absolute_import

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape

from .values import AES_CSS_MAP, AES_VALUE_MAP


HEADER = '''<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>\n
'''

MIDDLE = '''
    </style>
    <body>
        <p>
'''

FOOTER = '\t</body>\n</html>'

MARK_CSS = '''mark.{aes_name} {{
    {css_prop}: {css_value};
}}'''


def get_mark_css(aes_name, css_value):
    """Generate CSS class for <mark> tag.

    Parameters
    ----------
    aes_name: str
        The name of the class.
    css_value: str
        The value for the CSS property defined by aes_name.

    Returns
    -------
    str
        The CSS code
    """
    css_prop = AES_CSS_MAP[aes_name]
    return MARK_CSS.format(aes_name=aes_name, css_prop=css_prop, css_value=css_value)

OPENING_MARK = '<mark class="{classes}">'
CLOSING_MARK = '</mark>'


def get_opening_mark(classes):
    return OPENING_MARK.format(classes=htmlescape(classes))
