# -*- coding: utf-8 -*-
"""This module defines HTML and CSS templates and markup-generating functions
that are required by PrettyPrinter to generate full HTML and CSS output.
"""
from __future__ import unicode_literals, print_function, absolute_import

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape

from .values import AES_CSS_MAP

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
'''

FOOTER = '\t</body>\n</html>'

DEFAULT_MARK_CSS = '''\t\tmark {
\t\t\tbackground:none;
\t\t}'''

MARK_SIMPLE_CSS = '''\t\tmark.{aes_name} {{
\t\t\t{css_prop}: {css_value};
\t\t}}'''

MARK_RULE_CSS = '''\t\tmark.{aes_name}_{rule_index} {{
\t\t\t{css_prop}: {css_value};
\t\t}}'''


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
    list of str
        The CSS codeblocks
    """
    css_prop = AES_CSS_MAP[aes_name]
    if isinstance(css_value, list):
        return get_mark_css_for_rules(aes_name, css_prop, css_value)
    else:
        return get_mark_simple_css(aes_name, css_prop, css_value)


def get_mark_simple_css(aes_name, css_prop, css_value):
    return [MARK_SIMPLE_CSS.format(aes_name=aes_name, css_prop=css_prop, css_value=css_value)]


def get_mark_css_for_rules(aes_name, css_prop, css_value):
    for rule_idx, (rule_key, rule_value) in enumerate(css_value):
        yield MARK_RULE_CSS.format(aes_name=aes_name, rule_index=rule_idx, css_prop=css_prop, css_value=rule_value)


OPENING_MARK = '<mark class="{classes}">'
CLOSING_MARK = '</mark>'


def get_opening_mark(classes):
    return OPENING_MARK.format(classes=htmlescape(classes))