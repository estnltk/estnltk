# -*- coding: utf-8 -*-
"""Core module of the estnltk library.
Defines some common functionality and various paths.
"""
from __future__ import unicode_literals, print_function, absolute_import

import os
import six


# setup some paths
PACKAGE_PATH = os.path.dirname(__file__)

# corpora
CORPORA_PATH = os.path.join(PACKAGE_PATH, 'corpora')
PMNEWS_PATH = os.path.join(CORPORA_PATH, 'pm_news')
AA_PATH = os.path.join(CORPORA_PATH, 'arvutustehnika_ja_andmetootlus')
DEFAULT_NER_DATASET = os.path.join(CORPORA_PATH, 'estner.json')

# default NER model path
DEFAULT_PY2_NER_MODEL_DIR = os.path.join(PACKAGE_PATH, 'estner', 'models', 'py2_default')
DEFAULT_PY3_NER_MODEL_DIR = os.path.join(PACKAGE_PATH, 'estner', 'models', 'py3_default')

# verb chain detection resources
VERB_CHAIN_RES_PATH = os.path.join(PACKAGE_PATH, 'mw_verbs', 'res')


def as_unicode(s, encoding='utf-8'):
    """Convert the string to unicode."""
    if isinstance(s, six.text_type):
        return s
    elif isinstance(s, six.binary_type):
        return s.decode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(six.text_type, six.binary_type))


def as_binary(s, encoding='utf-8'):
    """Convert the string to binary"""
    if isinstance(s, six.text_type):
        return s.encode(encoding)
    elif isinstance(s, six.binary_type):
        # make sure the binary is in required encoding
        return s.decode(encoding).encode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(six.text_type, six.binary_type))


def get_filenames(root, prefix=u'', suffix=u''):
    """Function for listing filenames with given prefix and suffix in the root directory.
    
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
    """
    return [fnm for fnm in os.listdir(root) if fnm.startswith(prefix) and fnm.endswith(suffix)]