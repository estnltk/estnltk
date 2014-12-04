# -*- coding: utf-8 -*-
'''Command line program for EKT model training.
'''

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.settings import Settings
from estnltk.textclassifier.classifier import Clf
from estnltk.textclassifier.utils import read_dataset, write_html
from estnltk.textclassifier.utils import check_filename, save_classifier

import argparse
import sys
import logging
import codecs
import six


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('train')

parser = argparse.ArgumentParser(prog='estnltk.textclassifier.train')
parser.add_argument(
    'settings',
    help='Settings definitions containing features columns, label column and confidence column.')
parser.add_argument(
    '--synonyms',
    help='File containing a set of technical synonyms, one set per line.')
parser.add_argument(
    'dataset',
    help=('Dataset to use for training. Must contain columns defined in settings file.'
        ' It is possible to load .csv and .xlsx files.'))
parser.add_argument(
    'model',
    help='The path to store the trained model.')
parser.add_argument(
    '-r', '--report',
    help='The name of the report. The report is written as two files [name].html and [name]_misclassified_data.html')
parser.add_argument(
    '--sheet',
    default=0,
    help='Sheet name if loading data from Excel file (default read the first sheet).')
parser.add_argument(
    '--sep',
    default = ',',
    help='Column separator for CSV files (default is ,).')


class TrainerApp(object):
    
    def __init__(self, args):
        self._args = args
        
    def run(self):
        args = self._args
        logger.info('Loading settings from {0} and techsynonyms from {1} .'.format(args.settings, args.synonyms))
        print (args)
        settings = Settings.read(args.settings, args.synonyms)
        
        check_filename(args.dataset)
        dataframe = read_dataset(args.dataset, args.sep, args.sheet)

        clf = Clf(settings)
        clf.train(dataframe, report=True if args.report is not None else False)
        
        save_classifier(args.model, clf)
        
        if args.report is not None:
            mainfnm = args.report + '.html'
            misclassfnm = args.report + '_misclassified_data.html'
            write_html(mainfnm, clf.report)
            write_html(misclassfnm, clf.misclassified_data)

        logger.info('Done!')
        

if __name__ == '__main__':
    app = TrainerApp(parser.parse_args())
    app.run()

