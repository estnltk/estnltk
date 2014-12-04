# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.settings import Settings, SettingsFileReader
from estnltk.textclassifier.utils import read_dataset, write_dataset
from estnltk.textclassifier.utils import check_filename
from estnltk.textclassifier.classifier import merge_datasets

import argparse
import sys
import pandas as pd
import logging
import codecs

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('merge')

parser = argparse.ArgumentParser(prog='estnltk.textclassifier.merge')
parser.add_argument(
    'settings',
    help='Settings definitions containing features columns, label column and confidence column.')
parser.add_argument(
    'indata',
    help=('Main dataset. Must contain columns defined in settings file.'
        ' It is possible to load .csv and .xlsx files.'))
parser.add_argument(
    'extradata',
    help=('Extra dataset with filled confidence score column. Must contain other columns defined in settings file.'
        ' It is possible to load .csv and .xlsx files.'))
parser.add_argument(
    'outdata',
    help=('Extra dataset with filled confidence score column. Must contain other columns defined in settings file.'
        ' It is possible to save .csv and .xlsx files.'))
parser.add_argument(
    'treshold',
    type=float,
    default=0.9,
    help=('Confidence treshold. Only rows in extra dataset, where confidence >= treshold, will be used in merging.'))
        
parser.add_argument(
    '--insheet',
    default=0,
    help='Sheet name if loading data from Excel file (default is the first sheet).')
parser.add_argument(
    '--extrasheet',
    default=0,
    help='Sheet name if loading data from extra Excel file (default is the first sheet).')
parser.add_argument(
    '--outsheet',
    default='Sheet1',
    help='Sheet name if saving data to Excel file (default is Sheet1).')
parser.add_argument(
    '--insep',
    default = ',',
    help='Column separator for input CSV file (default is ,).')
parser.add_argument(
    '--extrasep',
    default = ',',
    help='Column separator for extra data CSV file (default is ,).')
parser.add_argument(
    '--outsep',
    default = ',',
    help='Column separator for output data CSV file (default is ,).')
    
class MergeApp(object):
    
    def __init__(self, args):
        self._args = args

    def run(self):
        args = self._args
        if not (args.outdata.endswith('.csv') or args.outdata.endswith('.xlsx')):
            print ('Output dataset filename must end with .csv or .xlsx')
            sys.exit(0)

        # loading settings
        settings = SettingsFileReader(args.settings).read()
        settings['synmap'] = {}
        settings = Settings(**settings)
        
        check_filename(args.indata)
        check_filename(args.extradata)
        check_filename(args.outdata)
            
        indata = read_dataset(args.indata, args.insep, args.insheet)
        extradata = read_dataset(args.extradata, args.extrasep, args.extrasheet)
        dataframe = merge_datasets(settings, indata, extradata, args.treshold)
        write_dataset(args.outdata, dataframe, args.outsep, args.outsheet)

        logger.info('Done!')
        
if __name__ == '__main__':
    app = MergeApp(parser.parse_args())
    app.run()
