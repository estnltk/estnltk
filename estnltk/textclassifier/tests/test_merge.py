# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.utils import read_dataset
from estnltk.textclassifier.paths import TEST_PATH

import unittest
import os
import sys

from subprocess import call
from tempfile import mkdtemp


class MergeAcceptanceTest(unittest.TestCase):
    '''Test for merge.py application.'''
    
    def setUp(self):
        self.tempdir = mkdtemp(prefix='estnltk.textclassifiertest_')
    
    def input_file(self):
        return os.path.join(TEST_PATH, 'original.xlsx')

    def extra_file(self):
        return os.path.join(TEST_PATH, 'extra.xlsx')

    def definitions_file(self):
        return os.path.join(TEST_PATH, 'merge.def')

    def result_file(self):
        return os.path.join(TEST_PATH, 'result.xlsx')

    def output_file(self):
        return os.path.join(self.tempdir, 'output.csv')
    
    def when_merge(self):
        return call([sys.executable, '-m', 'estnltk.textclassifier.merge', self.definitions_file(), self.input_file(), self.extra_file(), self.output_file(), '0.5'])
    
    def then_output_file_is_created(self):
        self.assertTrue(os.path.exists(self.output_file()))
        
    def then_output_is_correct(self):
        result = read_dataset(self.result_file())
        output = read_dataset(self.output_file())
        self.assertEqual(result.shape, output.shape)
        self.assertListEqual(list(result.columns), list(output.columns))
        for row1, row2 in zip(result, output):
            self.assertListEqual(list(row1), list(row2))
    
    def test_merge(self):
        self.when_merge()
        self.then_output_file_is_created()
        self.then_output_is_correct()

