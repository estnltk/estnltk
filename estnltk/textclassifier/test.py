# -*- coding: utf-8 -*-
'''Command line program for testing.
'''

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.utils import read_dataset, write_dataset
from estnltk.textclassifier.utils import check_filename, load_classifier

import argparse
import sys
import pandas as pd
import logging
import codecs

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('classify')

parser = argparse.ArgumentParser(prog='estnltk.textclassifier.test')
parser.add_argument(
    'data',
    help=('Path for the input dataset that will be classified. It is possible to load .csv and .xlsx files.'))
parser.add_argument(
    'model',
    help='The path of the classification model.')
parser.add_argument(
    '--sheet',
    default=0,
    help='Sheet name if reading data from Excel file (default is the first sheet).')
parser.add_argument(
    '--sep',
    default = ',',
    help='Column separator for reading CSV files (default is ,).')


class TestingApp(object):
    
    def __init__(self, args):
        self._args = args
        
    def run(self):       
        args = self._args
        
        
        check_filename(args.data)
        
        dataframe = read_dataset(args.data, args.sep, args.sheet)
        clf = load_classifier(args.model)
        logger.info('Performing testing on {0} examples.'.format(dataframe.shape[0]))
        results = clf.test(dataframe)
        print ('Precision: {0:.1f}%'.format(100*results['precision']))
        print ('   Recall: {0:.1f}%'.format(100*results['recall']))
        print (' F1-score: {0:.1f}%'.format(100*results['f1_score']))
        print ()
        print ('Label\tPrecision\tRecall\tF1-score\tCount')
        for rec in results['labels']:
            print('{0}\t{1:.1f}%\t{2:.1f}%\t{3:.1f}%\t{4}'.format(rec['label'], 100*rec['precision'], 100*rec['recall'], 100*rec['f1_score'], rec['count']))
        logger.info('Done!')

if __name__ == '__main__':
    app = TestingApp(parser.parse_args())
    app.run()
