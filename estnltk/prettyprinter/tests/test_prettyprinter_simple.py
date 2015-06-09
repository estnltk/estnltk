# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..prettyprinter import PrettyPrinter


class InitializationTest(unittest.TestCase):

    def test_default_initialization(self):

class ColorTest(unittest.TestCase):

    @property
    def text(self):
        return 'Head omadussõnad annavad igasse suvisesse päeva helgust.'

    def test_default_coloring(self):
        pp = PrettyPrinter(color='postags')

        html = pp.render(self.text)

        self.assertEquals(html, 'Head omadussõnad</span>')
        self.assertEquals(html.css, '')

    def test_classes(self):
        pp = PrettyPrinter(color='postags',
                           color_classes={'V': 'verbs', 'A|S': 'nomens'})

        html = pp.render(self.text)

        self.assertEquals(html, 'Head <span>omadussõnad</span>')
        self.assertEquals(html.css, 'verbs { } nomens { }')

    def test_css(self):
        pp = PrettyPrinter(color='postags',
                           color_classes={'V': 'verbs', 'A|S': 'nomens'},
                           color_css={'V': 'blue', 'A|S': 'green'})

        html = pp.render(self.text)

        self.assertEquals(html, 'Head <span>omadussõnad</span>')
        self.assertEquals(html.css, 'verbs { } nomens { }')
