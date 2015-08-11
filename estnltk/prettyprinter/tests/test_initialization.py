# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..prettyprinter import PrettyPrinter


class InitializationTest(unittest.TestCase):
    """Simple test that checks if using invalid arguments is handled by the prettyprinter."""

    def test_default_initialization(self):
        PrettyPrinter()

    def test_invalid_argument_throws_error(self):
        self.assertRaises(ValueError, PrettyPrinter, invalid_aesthetic='words')

    def test_layer_mapped_multiple_times_throws_error(self):
        self.assertRaises(ValueError, PrettyPrinter, color='layer', background='layer')

    def test_allowed_aesthetics(self):
        PrettyPrinter(
            color='layer1',
            background='layer2',
            font='layer3',
            weight='layer4',
            italics='layer5',
            underline='layer6',
            size='layer7',
            tracking='layer8'
        )

