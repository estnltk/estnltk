# -*- coding: utf-8 -*-
'''Core module of the estnltk library.
Defines common functionality for all modules.
'''
from __future__ import unicode_literals, print_function

import six
import os
from jsonpath_rw import parse

# setup some paths
PACKAGE_PATH = os.path.dirname(__file__)

# corpora
CORPORA_PATH = os.path.join(PACKAGE_PATH, 'corpora')
PMNEWS_PATH = os.path.join(CORPORA_PATH, 'pm_news')
AA_PATH = os.path.join(CORPORA_PATH, 'arvutustehnika_ja_andmetootlus')
DEFAULT_NER_DATASET = os.path.join(CORPORA_PATH, 'estner.json.bz2')

# default NER model path
DEFAULT_NER_MODEL = os.path.join(PACKAGE_PATH, 'estner', 'models', 'default.bin')


def as_unicode(s, encoding='utf-8'):
    '''Convert the string to unicode.'''
    if isinstance(s, six.text_type):
        return s
    elif isinstance(s, six.binary_type):
        return s.decode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(six.text_type, six.binary_type))
   
    
def as_binary(s, encoding='utf-8'):
    '''Convert the string to binary'''
    if isinstance(s, six.text_type):
        return s.encode(encoding)
    elif isinstance(s, six.binary_type):
        # make sure the binary is in required encoding
        return s.decode(encoding).encode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(six.text_type, six.binary_type))


def get_filenames(root, prefix=u'', suffix=u''):
    '''Function for listing filenames with given prefix and suffix in the root directory.
    
    Parameters
    ----------
    
    prefix: str
        The prefix of the required files.
    suffix: str
        The suffix of the required files
        
    Returns
    -------
    list of str
        List of filenames matching the prefix and suffix criteria.
    '''
    return [fnm for fnm in os.listdir(root) if fnm.startswith(prefix) and fnm.endswith(suffix)]


class JsonPaths(object):
    '''Class for defining common jsonpath_rw expresssions.
    
    Attributes
    ----------
    words: jsonpath_rw.jsonpath.Descendants
        Expression for extracting words from corpus structures.
    analysis: jsonpath_rw.jsonpath.Descendants
        Expression for exracting analysis results from corpus structures.
    '''
    words = parse('[*]..words')
    analysis = parse('[*]..analysis')
