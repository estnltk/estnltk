# -*- coding: utf-8 -*-
"""This module defines HTML and CSS templates and markup-generating functions
that are required by PrettyPrinter to generate full HTML and CSS output.
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

from .values import AES_CSS_MAP, AES_VALUE_MAP


HEADER = """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>\n
"""

MIDDLE = """
    </style>
    <body>
        <p>
"""

FOOTER = "\t</body>\n</html>"

MARK_CSS = """mark.{aes_name} {{
    {css_prop}: {css_value};
}}\n"""


def mark_css(aes_name, user_value=None):
    """Generate CSS class for <mark> tag.

    Parameters
    ----------
    aes_name: str
        The name of the class.
    user_value: str
        Depending on the aesthetic, the value that will be put in the class.
        If the user provides no value itself, we use default value.

    Returns
    -------
    str
        The CSS code
    """
    css_prop = AES_CSS_MAP[aes_name]
    css_value = AES_VALUE_MAP[aes_name] if user_value is not None else user_value
    MARK_CSS.format(aes_name, css_prop, css_value)
