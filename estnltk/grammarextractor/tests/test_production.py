# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..production import tokenize
from ..exceptions import ParseException


class TokenizeTest(unittest.TestCase):
    """Test production tokenization."""

    def test_zero_input_gives_zero_output(self):
        actual = tokenize('')
        expected = []
        self.assertListEqual(expected, actual)

    def test_empty_input_gives_zero_output(self):
        actual = tokenize('     ')
        expected = []
        self.assertListEqual(expected, actual)

    def test_single_symbol(self):
        actual = tokenize('a_symbol')
        expected = ['a_symbol']
        self.assertListEqual(expected, actual)

    def test_multiple_symbols(self):
        actual = tokenize('  a_symbol b_symbol c_symbol  ')
        expected = ['a_symbol', 'b_symbol', 'c_symbol']
        self.assertListEqual(expected, actual)

    def test_regex(self):
        actual = tokenize("'this here is a regex'")
        expected = ["'this here is a regex'"]
        self.assertListEqual(expected, actual)

    def test_failing_regex(self):
        self.assertRaises(ParseException, tokenize, "'ilma lõpute regex")

    def test_two_regexes(self):
        actual = tokenize("'first regex' and 'second regex'")
        expected = ["'first regex'", 'and', "'second regex'"]
        self.assertListEqual(expected, actual)

    def test_parenthesis_with_symbol(self):
        actual1 = tokenize('  (a_symbol)')
        actual2 = tokenize('  ( a_symbol )')
        expected = ['(', 'a_symbol', ')']
        self.assertListEqual(expected, actual1)
        self.assertListEqual(expected, actual2)

    def test_optional_with_symbol(self):
        actual1 = tokenize('optional_symbol?')
        actual2 = tokenize('optional_symbol ?')
        expected = ['optional_symbol', '?']
        self.assertListEqual(expected, actual1)
        self.assertListEqual(expected, actual2)

    def test_or_with_symbols(self):
        actual1 = tokenize('first|second')
        actual2 = tokenize('first|second')
        expected = ['first', '|', 'second']
        self.assertListEqual(expected, actual1)
        self.assertListEqual(expected, actual2)
