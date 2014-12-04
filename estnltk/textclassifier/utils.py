# -*- coding: utf-8 -*-
'''
File reading/writing utilities for command line programs.
These are primarly meant to be used by command line programs.
'''

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.classifier import Clf

import logging
import pandas as pd
import codecs
import sys
import six
import csv

logger = logging.getLogger('util')

def check_filename(fnm):
    '''Check if given filename for datafiles is correct.
    
    Parameters
    ----------
    fnm: str
        Filename of the file.

    Returns
    -------
    bool
        True, if file is either CSV or XLSX, otherwise
        exists the program.
    '''
    if fnm.endswith('.xlsx') or fnm.endswith('.csv'):
        return True
    print ('File {0} does not end with .csv or .xlsx'.format(fnm))
    sys.exit(0)

def read_dataset(fnm, sep=',', sheet=0):
    '''Read the dataset from the disk.
    
    Parameters
    ----------
    fnm: str
        The filename of the dataset.
    sep: str
        The field separater in case of CSV files (default is ,)
    sheet: int or str
        The sheet index or name in case of XLSX files (default is 0)

    Returns
    -------
    pandas.DataFrame
        The dataframe loaded from given file.
    '''
    logging.info('Reading dataset {0}'.format(fnm))
    if fnm.endswith('.csv'):
        dataframe = pd.read_csv(fnm, sep=encode_arg(decode_cmdarg(sep)), encoding='utf-8')
    elif fnm.endswith('.xlsx'):
        dataframe = pd.read_excel(fnm, decode_cmdarg(sheet))
    else:
        print ('Dataset filename must end with .csv or .xlsx')
        sys.exit(0)
    return dataframe
    
def write_dataset(fnm, dataframe, sep=',', sheet='Sheet1'):
    '''Write the dataset to the disk.
    
    Parameters
    ----------
    fnm: str
        The filename to write the data.
    dataframe: pandas.DataFrame
        The pandas dataframe instance to write to disk.
    sep: str
        The field separater in case of CSV files (default is ,)
    sheet: str
        The sheet index or name in case of XLSX files (default is "Sheet1")
    '''
    logging.info('Writing dataset {0}'.format(fnm))
    if fnm.endswith('.csv'):
        dataframe.to_csv(fnm,
                         sep=encode_arg(decode_cmdarg(sep)),
                         encoding='utf-8',
                         quoting=csv.QUOTE_ALL,
                         index=False)
    elif fnm.endswith('.xlsx'):
        dataframe.to_excel(fnm,
                           sheet_name=decode_cmdarg(sheet),
                           encoding='utf-8',
                           index=False)
    else:
        print ('Dataset filename must end with .csv or .xlsx')
        sys.exit(0)

def write_html(fnm, html):
    '''Write HTML content to specified filename.
    
    Parameters
    ----------
    fnm: str
        The filename.
    html: str
        HTML content.
    '''
    logging.info('Writing HTML content to {0}'.format(fnm))
    with codecs.open(fnm, 'wb', 'utf-8') as f:
        f.write(html)

def load_classifier(fnm):
    '''Load the classifier from specified filename.
    
    Parameters
    ----------
    fnm: str
        The filename.

    Returns
    -------
    estnltk.textclassifier.classifier.Clf
        The previously trained classifier model.
    
    '''
    logging.info('Loading classifier from {0}'.format(fnm))
    with codecs.open(fnm, 'rb', 'ascii') as f:
        clf = Clf.from_json(f.read())
        return clf
    
def save_classifier(fnm, classifier):
    '''Save the classifier to specified filename.
    
    Parameters
    ----------
    fnm: str
        The filename.
    classifier: estnltk.textclassifier.classifier.Clf
        The classifier model instance.
    '''
    logging.info('Saving classifier to {0}'.format(fnm))
    with codecs.open(fnm, 'wb', 'ascii') as f:
        f.write(classifier.export_json())

def decode_cmdarg(arg):
    '''Convert a command line argument to str. Skip if int.'''
    if six.PY2 and arg != 0:
        return arg.decode(sys.stdin.encoding)
    return arg

def encode_arg(arg):
    if six.PY2 and arg != 0:
        return arg.encode('utf-8')
    return arg
