# -*- coding: utf-8 -*-
"""Core module of the Estnltk library, that sets up some common paths and has functions to convert between
binary and unicode data.

Python 2.x and Python 3.x versions are different in the way the handle unicode data.

* Python 2 uses ``str`` for binary data and ``unicode`` for textual data.
* Python 3 uses ``str`` for unicode data and ``bytes`` for binary data.

As it is impossible to write code that is compatible with both Python versions due to using different types,
we use :py:func:`~estnltk.core.as_unicode` and  :py:func:`~estnltk.core.as_binary` to abstact the conversion away.

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
    """Force conversion of given string to unicode type.
    Unicode is ``str`` type for Python 3.x and ``unicode`` for Python 2.x .

    If the string is already in unicode, then no conversion is done and the same string is returned.

    Parameters
    ----------
    s: str or bytes (Python3), str or unicode (Python2)
        The string to convert to unicode.
    encoding: str
        The encoding of the input string (default: utf-8)

    Raises
    ------
    ValueError
        In case an input of invalid type was passed to the function.

    Returns
    -------
    ``str`` for Python3 or ``unicode`` for Python 2.
    """
    if isinstance(s, six.text_type):
        return s
    elif isinstance(s, six.binary_type):
        return s.decode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(six.text_type, six.binary_type))


def as_binary(s, encoding='utf-8'):
    """Force conversion of given string to binary type.
    Binary is ``bytes`` type for Python 3.x and ``str`` for Python 2.x .

    If the string is already in binary, then no conversion is done and the same string is returned
    and ``encoding`` argument is ignored.

    Parameters
    ----------
    s: str or bytes (Python3), str or unicode (Python2)
        The string to convert to binary.
    encoding: str
        The encoding of the resulting binary string (default: utf-8)

    Raises
    ------
    ValueError
        In case an input of invalid type was passed to the function.

    Returns
    -------
    ``bytes`` for Python3 or ``str`` for Python 2.
    """
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