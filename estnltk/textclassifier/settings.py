# -*- coding: utf-8 -*-
'''Module containing the funtionality to handle settings.'''

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.synunifier import SynUnifier, SynFileReader

import codecs
from copy import copy

NUM_CORES = 1

class Settings(dict):
    '''Classification task settings.
    
    1. The feature column names.
    2. The label column name.
    3. The confidence column name.
    4. The Problem-pecific synonyms.
    '''
    
    REQUIRED_KEYS = frozenset(['features', 'label'])
    
    def __init__(self, **kwargs):
        '''Initialize classification task settings.
        
        Keyword parameters:
        -------------------
        
        features: list[str]
            The list of columns that will be used for feature extraction.
        label: str
            The column name for category labels
        confidence: str
            The column name to store the classification label probabilities.
        synmap: dict
            The alternative synonym -> main synonym mappings for technical
            vocabulary unification.

        Raises
        ------
        
        ValueError
            In case illegal arguments are passed to the constructor or if some arguments are missing.
        '''
        
        for key, value in kwargs.items():
            if key == 'features':
                self['features'] = [name for name in value]
            elif key == 'label':
                self['label'] = value
            elif key == 'confidence':
                self['confidence'] = value
            elif key == 'synmap':
                self['unifier'] = SynUnifier(value)
            else:
                err = 'Invalid argument {0}. Allowed arguments are {1}'.format(repr(key), repr(Settings.KEYS))
                raise ValueError(err)
        if 'unifier' not in self:
            self['unifier'] = SynUnifier({})
        if 'confidence' not in self:
            self['confidence'] = 'confidence'
        missing = set(Settings.REQUIRED_KEYS) - set(kwargs.keys())
        if len(missing) > 0:
            raise ValueError('Not all required arguments were passed: {0}.'.format(repr(missing)))
        
        self._check_arguments()
        

    def export(self):
        '''Export the settings as a Python dictionary.'''
        return {'features': copy(self.features),
                'label': copy(self.label),
                'confidence': copy(self.confidence),
                'synmap': self.unifier.export()}

    @property
    def features(self):
        return self['features']

    @property
    def label(self):
        return self['label']
    
    @property
    def confidence(self):
        return self['confidence']
    
    @property
    def unifier(self):
        return self['unifier']

    def _check_arguments(self):
        if len(self.features) == 0:
            raise ValueError('Zero feature columns given.')
        for name in self.features:
            if len(name) == 0:
                raise ValueError('Zero-length feature column name.')
        if len(self.label) == 0:
            raise ValueError('Zero-length label column name.')
        if len(self.confidence) == 0:
            raise ValueError('Zero-length confidence column name.')
        if len(set(self.features)) != len(self.features):
            raise ValueError('Duplicate values in feature column names.')
        if len(set(self.features + [self.label, self.confidence])) != len(self.features) + 2:
            raise ValueError('Duplicate names.')

    @staticmethod
    def read(setfnm, synfnm=None):
        '''Initialize settings from technical synonym and settings files.
        
        Parameters
        ----------
        
        setfnm: str
            Path for file containing settings definitions.
        synfnm: str
            Path for file containing technical synonyms (default: None).
        
        Returns
        -------
        Settings
            Dictionary containing the settings and technical synonym vocabulary.
        '''
        settings = SettingsFileReader(setfnm).read()
        if synfnm is not None:
            unifier = SynFileReader(synfnm).read()
            settings['synmap'] = unifier.export()
        else:
            settings['synmap'] = {}
        return Settings(**settings)


class SettingsFileReader(object):
    '''Class to read settings files.'''
    
    SECTIONS = ['[features]', '[label]', '[confidence]']
    
    def __init__(self, fnm):
        self._fnm = fnm
    
    def _initialize(self):
        self._mode = None
        self._features = []
        self._label = None
        self._confidence = None
        self._lineno = 0
    
    def read(self):
        '''
        Returns
        -------
        Dictionary containing 'features', 'label' and 'confidence' values.
        
        NB! Use Settings.read instead to load the settings also with synonym vocabulary.
        '''
        self._initialize()
        with codecs.open(self._fnm, 'rb', 'utf-8') as f:
            line = f.readline()
            while line != '':
                line = line.strip()
                if len(line) == 0:
                    line = f.readline()
                    self._lineno += 1
                    continue
                if line.startswith('['):
                    self._parse_section(line)
                else:
                    self._parse_value(line)
                self._lineno += 1
                line = f.readline()
        return {'features': self._features,
                 'label': self._label,
                 'confidence': self._confidence}

    def _parse_section(self, line):
        if line not in SettingsFileReader.SECTIONS:
            raise ValueError('Invalid section: {0} on line {1}'.format(repr(line), self._lineno))
        self._mode = line[1:-1]

    def _parse_value(self, line):
        if self._mode == 'features':
            self._features.append(line)
        elif self._mode == 'label':
            if self._label is not None:
                raise ValueError('[label] already defined!. Duplicate definition on line {0}'.format(self._lineno))
            self._label = line
        elif self._mode == 'confidence':
            if self._confidence is not None:
                raise ValueError('[confidence] already defined!. Duplicate definition on line {0}'.format(self._lineno))
            self._confidence = line
        else:
            raise ValueError('No section defined on line {0}'.format(self._lineno))
        
