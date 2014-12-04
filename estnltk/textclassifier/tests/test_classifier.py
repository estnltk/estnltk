# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.paths import TEST_PATH
from estnltk.textclassifier.classifier import Clf
from estnltk.textclassifier.settings import Settings

import unittest
import os
import pandas

class ClassifierTest(unittest.TestCase):

    def test_training_no_report(self):
        clf = self.clf()
        clf.train(self.dataset(), report=False)
        self.assertEqual(clf.report, None)
        self.assertEqual(clf.misclassified_data, None)
        
    def test_training_with_report(self):
        clf = self.clf()
        clf.train(self.dataset(), report=True)
        self.assertTrue(len(clf.report) > 100)
        self.assertTrue(len(clf.misclassified_data) > 50)
    
    def test_classify_fails_model_not_trainer(self):
        clf = self.clf()
        self.assertRaises(ValueError, clf.classify, self.dataset())
    
    def test_classify(self):
        clf = self.clf()
        clf.train(self.dataset())
        df = self.dataset()
        df = clf.classify(df)
        labels = df['järeldus']
        confidence = df['kindlus']
        self.assertEqual(df.shape[0], len(labels))
        self.assertEqual(df.shape[0], len(confidence))
    
    def clf(self):
        return Clf(self.settings())
    
    def settings(self):
        return Settings.read(os.path.join(TEST_PATH, 'weather.def'),
                             os.path.join(TEST_PATH, 'weather.txt'))

    def dataset(self):
        return pandas.read_excel(os.path.join(TEST_PATH, 'weather.xlsx'), sheet_name='Sheet1')
