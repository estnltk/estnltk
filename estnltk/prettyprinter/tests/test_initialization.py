# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..prettyprinter import PrettyPrinter
from ..values import DEFAULT_VALUE_MAP


class InvalidArgumentsTest(unittest.TestCase):
    """Simple test that checks if using invalid arguments is handled by the prettyprinter."""

    def test_default_initialization(self):
        PrettyPrinter()

    def test_invalid_argument_throws_error(self):
        self.assertRaises(ValueError, PrettyPrinter, invalid_aesthetic='words')

    def test_layer_mapped_multiple_times_throws_error(self):
        self.assertRaises(ValueError, PrettyPrinter, color='layer', background='layer')

    def test_invalid_rules_initialization(self):
        self.assertRaises(ValueError, PrettyPrinter, color='layer', color_value=[('A', 0), ('B', 1)])
        self.assertRaises(ValueError, PrettyPrinter, color='layer', color_value={})
        self.assertRaises(ValueError, PrettyPrinter, color='layer', color_value=[])


# data for second testcase
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

VALUES = {
    'color_value': 'red',
    'font_value': 'monospace'
}

EXPECTED_VALUES = DEFAULT_VALUE_MAP.copy()
EXPECTED_VALUES.update({
    'color': 'red',
    'font': 'monospace'
})


class CorrectInitializationTest(unittest.TestCase):
    """Simple testcase to check if user-provided arguments are parsed correctly."""

    def test_allowed_aesthetics(self):
        kwargs = AESTHETICS.copy()
        kwargs.update(VALUES)

        pp = PrettyPrinter(**kwargs)
        self.assertDictEqual(AESTHETICS, pp.aesthetics)
        self.assertDictEqual(EXPECTED_VALUES, pp.values)
