# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..common import is_valid_symbol_name


class TestSymbolNameValidation(unittest.TestCase):

    def test_valid(self):
        valid_names = [
            'lowercaseascii',
            'UPPERCASEASCII',
            'MixedAscii',
            'symbol_with_underscore',
            'EestiSümbol',
            'Российская',
            '中华人民共和国',
            'NumbersAreokayToo123456789',
            'A'
        ]
        for name in valid_names:
            self.assertTrue(is_valid_symbol_name(name), name)

    def test_invalid(self):
        invalid_names = [
            'symbols should not contain spaces',
            '',
            'no\nshitespace\r',
            'wierd-characters-$%^&$^-are*%^*&not_#$%^#$%^allowed',
            'no.punctuation'
        ]
        for name in invalid_names:
            self.assertFalse(is_valid_symbol_name(name), name)

