# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import six
import imp
import importlib
from estnltk.core import PACKAGE_PATH

NER_PACKAGE_PATH = os.path.join(PACKAGE_PATH, 'estner')
DEFAULT_SETTINGS_MODULE = os.path.join(NER_PACKAGE_PATH, 'conf', 'default.py')

def load_from_source(path):
    '''Load a module, given its path.'''
    mname = 'loaded_module'
    if six.PY2:
        import imp
        return imp.load_source(mname, path)
    else:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mname, path)
        return loader.load_module(mname)


class Settings(dict):
    '''Named entity recognition settings.'''
    
    keys = ['classes', 'templates', 'feature_extractors', 'gazetteer_file']
    
    def __init__(self, settings_module_path=DEFAULT_SETTINGS_MODULE):
        '''Load a module from given path and initialize settings.'''
        super(Settings, self).__init__()
        module = load_from_source(settings_module_path)
        
        for prop, value in module.__dict__.iteritems():
            if prop.lower() in Settings.keys:
                self[prop.lower()] = value
        
        for key in Settings.keys:
            if key not in self:
                raise Exception('Key "{0}" not present in settings'.format(key))

    @property
    def classes(self):
        return self['classes']
        
    @property
    def templates(self):
        return self['templates']
        
    @property
    def feature_extractors(self):
        return self['feature_extractors']
        
    @property
    def gazetteer_file(self):
        return self['gazetteer_file']
