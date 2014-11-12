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
JAVARES_PATH = os.path.join(PACKAGE_PATH, 'java-res')

# corpora
CORPORA_PATH = os.path.join(PACKAGE_PATH, 'corpora')
PMNEWS_PATH = os.path.join(CORPORA_PATH, 'pm_news')

def as_unicode(s, encoding='utf-8'):
    '''Convert the string to unicode.
    
    Parameters
    ----------
    s: str or unicode or bytes
        Input string.
    encoding: str
        If the given string is binary, then assumes this encoding (default: utf-8).
        
    Returns
    -------
    unicode
        In case of Python2
    str
        In case of Python3
    '''
    if six.PY2:
        if isinstance(s, str):
            return s.decode(encoding)
        else:
            return unicode(s)
    else: # ==> Py3
        if isinstance(s, bytes):
            return s.decode(encoding)
        else:
            return str(s)
    
def as_binary(s, encoding='utf-8'):
    '''Convert the given string to binary.
    
    Parameters
    ----------
    s: unicode or str
        Input string.
    encoding: str
        The encoding for binary data (default: utf-8)
    
    Returns
    -------
    str
        In case of Python2
    bytes
        In case of Python3
    '''
    if six.PY2 and isinstance(word, unicode):
        return s.encode(encoding)
    elif six.PY3 and isinstance(word, str):
        return s.encode(encoding) # bytes must be in utf8
    return s.decode(encoding).encode(encoding)


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
