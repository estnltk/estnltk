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

    def test_full_css(self):
        a ={'background_0': 'rgb(102, 204, 255)'}

        pp = PrettyPrinter(**AESTHETICS)
        css = pp.css(a)
        # just check that CSS is generated for all aesthetics
        for aes in AESTHETICS:
            css_fragment = 'mark.' + aes + ' {'
            self.assertTrue(css_fragment in css(a))

    def test_one_layer_css(self):
        a = {'background_0': 'rgb(102, 204, 255)'}
        pp = PrettyPrinter(color='layer')
        self.assertTrue('mark.color' in pp.css(a))
        self.assertTrue('mark.background' not in pp.css(a))

    def test_color_value_supplied_by_user(self):
        a = {'background_0': 'rgb(102, 204, 255)'}
        pp = PrettyPrinter(color='layer', color_value='color_you_have_never_seen')
        self.assertTrue('color: color_you_have_never_seen' in pp.css(a))

