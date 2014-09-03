# -*- coding: utf-8 -*-

'''Core module of the estnltk library.
Defines functionality common to all modules.
'''

import os

# setup some paths

PACKAGE_PATH = os.path.dirname(__file__)
CORPORA_PATH = os.path.join(PACKAGE_PATH, 'corpora')
PMNEWS_PATH = os.path.join(CORPORA_PATH, 'pm_news')


def get_filenames(root, prefix=u'', suffix=u''):
    '''Function for listing filenames with given prefix and suffix in the root directory.
    
    Parameters:
    
    prefix: str
        The prefix of the required files.
    suffix: str
        The suffix of the required files
        
    Returns: list of str
        List of filenames matching the prefix and suffix criteria.
    '''
    return [fnm for fnm in os.listdir(root) if fnm.startswith(prefix) and fnm.endswith(suffix)]

