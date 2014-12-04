# -*- coding: utf-8 -*-
'''Command line program for classification.
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

parser = argparse.ArgumentParser(prog='estnltk.textclassifier.classify')
parser.add_argument(
    'indata',
    help=('Path for the input dataset that will be classified. It is possible to load .csv and .xlsx files.'))
parser.add_argument(
    'outdata',
    help = 'Path where the classified dataset will be stored. It is possible to save .csv and .xlsx files')
parser.add_argument(
    'model',
    help='The path of the classification model.')
parser.add_argument(
    '--insheet',
    default=0,
    help='Sheet name if reading data from Excel file (default is the first sheet).')
parser.add_argument(
    '--insep',
    default = ',',
    help='Column separator for reading CSV files (default is ,).')
parser.add_argument(
    '--outsheet',
    default='Sheet1',
    help='Sheet name if saving as an Excel file (default is Sheet1).')
parser.add_argument(
    '--outsep',
    default = ',',
    help='Column separator for saving CSV files (default is ,).')


class ClassificationApp(object):
    
    def __init__(self, args):
        self._args = args
        
    def run(self):       
        args = self._args
        
        if args.indata == args.outdata:
            print ('Indata and outdata point to same file. It is not allowed to minimize risk overwriting original training data')
            sys.exit(0)
        
        check_filename(args.indata)
        check_filename(args.outdata)
        
        dataframe = read_dataset(args.indata, args.insep, args.insheet)
        clf = load_classifier(args.model)
        logger.info('Performing classification on {0} examples.'.format(dataframe.shape[0]))
        dataframe = clf.classify(dataframe)
        write_dataset(args.outdata, dataframe, args.outsep, args.outsheet)

        logger.info('Done!')
        

if __name__ == '__main__':
    app = ClassificationApp(parser.parse_args())
    app.run()
