# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.paths import TEST_PATH

import unittest
import os
import sys
from subprocess import call
from tempfile import mkdtemp


class UserTrainsAndUsesModelTest(unittest.TestCase):
    '''Main test that does full cycle with excel files.'''

    def setUp(self):
        self.tempdir = mkdtemp(prefix='estnltk.textclassifiertest_')

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
        return [sys.executable, '-m', 'estnltk.textclassifier.train', self.deffile(), '--synonyms', self.synfile(), self.datafile(), self.modelfile(), '-r='+self.reportfile()] 
    
    def classifycommand(self):
        return [sys.executable, '-m', 'estnltk.textclassifier.classify', self.infile(), self.outfile(), self.modelfile()] 
    
    def user_runs_training_command(self):
        call(self.traincommand())
        
    def then_report_is_generated(self):
        if not os.path.isfile(self.main_reportfile()):
            raise Exception('no main report generated')
        if not os.path.isfile(self.misclassified_reportfile()):
            raise Exception('no misclassified data report generated')
    
    def then_model_is_generated(self):
        if not os.path.isfile(self.modelfile()):
            raise exception('no model generated')
    
    def user_runs_classification_command(self):
        call(self.classifycommand())
    
    def then_outfile_exists(self):
        if not os.path.isfile(self.outfile()):
            raise Exception('outfile does not exist')
    
    def test_train_and_use_model(self):
        self.user_runs_training_command()
        self.then_report_is_generated()
        self.then_model_is_generated()
        self.user_runs_classification_command()
        self.then_outfile_exists()

        
class UserInputsAndOutputsCsvFile(UserTrainsAndUsesModelTest):

    def datafile(self):
        return os.path.join(TEST_PATH, 'weather.csv')

    def outfile(self):
        return os.path.join(self.tempdir, 'weather_out.csv')

        
