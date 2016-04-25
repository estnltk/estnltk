# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..prettyprinter import PrettyPrinter

AESTHETICS = {
    'color': 'layer1',
    'background': 'layer2',
    'font': 'layer3',
    'weight': 'layer4',
    'italics': 'layer5',
    'underline': 'layer6',
    'size': 'layer7',
    'tracking': 'layer8'
}


class CssTest(unittest.TestCase):

    def test_one_layer_css(self):
        pp = PrettyPrinter(color='layer')
        self.assertTrue('mark.color' in pp.css)
        self.assertTrue('mark.background' not in pp.css)

    def test_color_value_supplied_by_user(self):
        pp = PrettyPrinter(color='layer', color_value='color_you_have_never_seen')
        self.assertTrue('color: color_you_have_never_seen' in pp.css)

    def test_full_css_without_rules(self):
        pp = PrettyPrinter(**AESTHETICS)
        css = pp.css
        # just check that CSS is generated for all aesthetics
        for aes in AESTHETICS:
            css_fragment = 'mark.' + aes + ' {'
            self.assertTrue(css_fragment in css)

    def test_color_css_with_rules(self):
        rules = [
            ('Nimisõnad', 'green'),
            ('värvitakse', 'blue')
        ]
        pp = PrettyPrinter(color='layer', color_value=rules)
        css = pp.css
        self.assertTrue('mark.color_0' in css)
        self.assertTrue('color: green;' in css)
        self.assertTrue('mark.color_1' in css)
        self.assertTrue('color: blue;' in css)
