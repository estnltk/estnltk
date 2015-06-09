# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..prettyprinter import PrettyPrinter


class InitializationTest(unittest.TestCase):

    def test_default_initialization(self):
        PrettyPrinter()

    def test_invalid_argument_throws_error(self):
        self.assertRaises(ValueError, PrettyPrinter, invalid_aesthetic='words')

    def test_allowed_aesthetics(self):
        PrettyPrinter(
            color='words',
            background='words',
            font='words',
            weight='words',
            italics='words',
            underline='words',
            size='words',
            tracking='words'
        )

