# -*- coding: utf-8 -*-
"""Module for highlighting elements in corpora using HTML and CSS."""

from __future__ import unicode_literals, print_function
from estnltk.corpus import Corpus
from estnltk.names import TEXT

try:
    from StringIO import cStringIO as StringIO
except ImportError: # Py3
    from io import StringIO
    
try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape
    
import colorsys
import re

HEADER = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{0}</title>
</head>

<body>"""

FOOTER = """</body></html>"""

def render_html(corpus, element, value=TEXT, css=[('.*', 'background-color:yellow')], encapsulate_body=False):
    """Highlight interesting corpus elements and return them as HTML
    
    Parameters
    ----------
    element: str
        The name of the element as defined in names.py.
    value: str or func
        If string, assume elements are dictionaries and this is a valid key to extract the value.
        If function, then gives the element as the argument and expects the function to return valid string.
        If none, just use element text in filtering.
    css: list of (str, str)
        Each tuple defines a regular expression and a string containing CSS style code
        that will be applied to elements whose value is matched by the regex.
        The regexes will be tested in the order given and the CSS of the first
        matching regex will be given.
    encapsulate_body: boolean
        If True, adds HTML5 header and body to HTML.
    """
    stream = StringIO()
    if encapsulate_body:
        stream.write(HEADER.format(element))
    
    css = [(re.compile(regex), style) for regex, style in css]
    
    for root in corpus.root_elements:
        stream.write('<div>\n')
        elems = root.elements(element)
        spans = [e.span for e in elems]
        values = []
        if callable(value):
            values = [value(e) for e in elems]
        else:
            values = [e[value] for e in elems]
        styles = collect_styles(values, css)
        assert len(spans) == len(styles)
        stream.write(insert_spans(root.text, spans, styles))
        stream.write('</div>\n')
    
    if encapsulate_body:
        stream.write(FOOTER)
    
    return stream.getvalue()

def collect_styles(values, css):
    styles = []
    for v in values:
        found_match = False
        for pattern, style in css:
            if pattern.match(v) is not None:
                styles.append(style)
                found_match = True
                break
        if not found_match:
            styles.append('')
    return styles

def make_colors(n):
    """Function that creates `n` colors usable in plotting."""
    hsv_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    return [colorsys.hsv_to_rgb(*x) for x in hsv_tuples]

def insert_spans(text, spans, css_classes):
    """Insert spans with specified css classes into text
    and html escape all other characters."""
    positions = []
    for (start, end), classes in zip(spans, css_classes):
        start_token = (start, 1, classes)
        end_token = (end, 0, None)
        positions.append(start_token)
        positions.append(end_token)
    positions.sort()
    text = [htmlescape(c) for c in text]
    for pos, t, classes in reversed(positions):
        if t == 1:
            text[pos:pos] = '<span style="{0}">'.format(classes)
        else:
            text[pos:pos] = '</span>'
    return ''.join(text)
