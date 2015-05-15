# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from ..core import as_unicode, as_binary
import unittest
import six


class TestAsUnicode(unittest.TestCase):
    """Tests for as_unicode function"""
    
    def test_unicode_input(self):
        w = as_unicode('ööTää')
        self.assertEqual(w, 'ööTää')
        if six.PY2:
            self.assertTrue(isinstance(w, unicode))
        if six.PY3:
            self.assertTrue(isinstance(w, str))
            
    def test_binary_input(self):
        w = as_unicode('ööTää'.encode('utf-8'))
        self.assertEqual(w, 'ööTää')
        if six.PY2:
            self.assertTrue(isinstance(w, unicode))
        if six.PY3:
            self.assertTrue(isinstance(w, str))
            
    def test_invalid_input_type(self):
        w = ['list']
        self.assertRaises(ValueError, as_unicode, w)


class TestAsBinary(unittest.TestCase):
    """Tests for as_binary function."""
    
    def test_unicode_input(self):
        w = as_binary('ööTää')
        self.assertEqual(w, 'ööTää'.encode('utf-8'))
        if six.PY2:
            self.assertTrue(isinstance(w, str))
        if six.PY3:
            self.assertTrue(isinstance(w, bytes))
        
    def test_binary_input(self):
        w = as_binary('ööTää'.encode('utf-8'))
        self.assertEqual(w, 'ööTää'.encode('utf-8'))
        if six.PY2:
            self.assertTrue(isinstance(w, str))
        if six.PY3:
            self.assertTrue(isinstance(w, bytes))
        
    def test_binary_wrong_encoding_raises_valueerror(self):
        w = 'ööTää'.encode('latin-1')
        self.assertRaises(ValueError, as_binary, w)
        
    def test_invalid_input_type(self):
        w = ['list']
        self.assertRaises(ValueError, as_unicode, w)
