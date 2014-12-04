# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.paths import TEST_PATH
from estnltk.textclassifier.utils import load_classifier

import unittest
import os
import sys
from subprocess import call
from tempfile import mkdtemp


class UserRetrainsModelTest(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = mkdtemp(prefix='estnltk.textclassifiertest_')
        self._train_dataframe_size = None

    def deffile(self):
        return os.path.join(TEST_PATH, 'weather.def')

    def synfile(self):
        return os.path.join(TEST_PATH, 'weather.txt')
        
    def datafile(self):
        return os.path.join(TEST_PATH, 'weather.xlsx')
    
    def modelfile(self):
        return os.path.join(self.tempdir, 'model.bin')
    
    def reportfile(self):
        return os.path.join(self.tempdir, 'report')

    def main_reportfile(self):
        return os.path.join(self.tempdir, 'report.html')
        
    def misclassified_reportfile(self):
        return os.path.join(self.tempdir, 'report_misclassified_data.html')
    
    def infile(self):
        return self.datafile()
    
    def outfile(self):
        return os.path.join(self.tempdir, 'weather_out.xlsx')
    
    def traincommand(self):
        return [sys.executable, '-m', 'estnltk.textclassifier.train', self.deffile(), self.datafile(), self.modelfile(), '-r', self.reportfile()] 
    
    def retraincommand(self):
        return [sys.executable, '-m', 'estnltk.textclassifier.retrain', self.datafile(), self.modelfile(), self.modelfile(), '-t', '0.0', '-r', self.reportfile()] 
    
    def user_runs_training_command(self):
        call(self.traincommand())
        
    def then_report_is_generated(self):
        if not os.path.isfile(self.main_reportfile()):
            raise Exception('no main report generated')
        if not os.path.isfile(self.misclassified_reportfile()):
            raise Exception('no misclassified data report generated')
    
    def then_model_has_original_data(self):
        clf = load_classifier(self.modelfile())
        self.assertTrue(clf._train_dataframe.shape[0] > 0)
        self._train_dataframe_size = clf._train_dataframe.shape[0]
    
    def then_model_is_generated(self):
        if not os.path.isfile(self.modelfile()):
            raise exception('no model generated')
    
    def user_runs_retrain_command(self):
        call(self.retraincommand())
    
    def then_outfile_exists(self):
        if not os.path.isfile(self.outfile()):
            raise Exception('outfile does not exist')
            
    def then_model_has_twice_as_data(self):
        clf = load_classifier(self.modelfile())
        self.assertEqual(clf._train_dataframe.shape[0], 2*self._train_dataframe_size)
    
    def test_train_and_use_model(self):
        self.user_runs_training_command()
        self.then_report_is_generated()
        self.then_model_is_generated()
        self.then_model_has_original_data()
        self.user_runs_retrain_command()
        self.then_report_is_generated()
        self.then_model_is_generated()
        self.then_model_has_twice_as_data()

