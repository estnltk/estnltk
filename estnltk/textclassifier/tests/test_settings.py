# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.settings import Settings, SettingsFileReader
from estnltk.textclassifier.synunifier import SynFileReader
from estnltk.textclassifier.paths import TEST_PATH

import unittest
import os


def valid_settings():
    return {'label': 'label',
            'confidence': 'confidence',
            'features': ['f1', 'f2', 'f3'],
            'synmap': {
                'kl': 'kl',
                'klient': 'kl',
                'digiboks': 'digiboks',
                'db': 'digiboks',
                'dbox': 'digiboks',
                'digibox': 'digiboks',
                'boks': 'digiboks'}
            }

def settings_zerofeatures():
    settings = valid_settings()
    settings['features'] = []
    return settings

def settings_zerolength_feature():
    settings = valid_settings()
    settings['features'] = ['f1', '', 'f3']
    return settings

def settings_zerolength_label():
    settings = valid_settings()
    settings['label'] = ''
    return settings

def settings_zerolength_confidence():
    settings = valid_settings()
    settings['confidence'] = ''
    return settings

def settings_features_missing():
    settings = valid_settings()
    del settings['features']
    return settings

def settings_label_missing():
    settings = valid_settings()
    del settings['label']
    return settings

def settings_confidence_missing():
    settings = valid_settings()
    del settings['confidence']
    return settings

def settings_duplicate_features():
    settings = valid_settings()
    settings['features'] = ['f1', 'f2', 'f1']
    return settings

def settings_duplicate_names():
    settings = valid_settings()
    settings['confidence'] = 'f2'
    return settings

class InitializationTest(unittest.TestCase):
    
    def test_valid_initialization(self):
        settings = Settings(**valid_settings())

    def test_serialization(self):
        settings = Settings(**valid_settings())
        self.assertDictEqual(settings.export(), valid_settings())
        
    def test_invalid_initialization_nofeaturecolumns(self):
        self.assertRaises(ValueError, Settings, **settings_zerofeatures())

    def test_invalid_initialization_zerolength_feature(self):
        self.assertRaises(ValueError, Settings, **settings_zerolength_feature())
        
    def test_invalid_initialization_zerolength_confidence(self):
        self.assertRaises(ValueError, Settings, **settings_zerolength_confidence())
    
    def test_invalid_settings_features_missing(self):
        self.assertRaises(ValueError, Settings, **settings_features_missing())
    
    def test_invalid_settings_label_missing(self):
        self.assertRaises(ValueError, Settings, **settings_label_missing())
        
    def test_invalid_initialization_zerolength_label(self):
        self.assertRaises(ValueError, Settings, **settings_zerolength_label())
    
    def test_invalid_initialization_duplicate_features(self):
        self.assertRaises(ValueError, Settings, **settings_duplicate_features())
    
    def test_invalid_initialization_duplicate_names(self):
        self.assertRaises(ValueError, Settings, **settings_duplicate_names())
        

class SettingsFileReaderTest(unittest.TestCase):
    
    def test_reading_succeeds(self):
        reader = SettingsFileReader(self.success_filepath())
        settings = reader.read()
        self.assertDictEqual(settings, self.success_settings())
    
    def test_reading_fails_nosection(self):
        reader = SettingsFileReader(self.fail_nosection_filepath())
        self.assertRaises(ValueError, reader.read)
    
    def test_reading_fails_invalid_section(self):
        reader = SettingsFileReader(self.fail_invalid_section_filepath())
        self.assertRaises(ValueError, reader.read)
    
    def test_reading_fails_duplicate_section(self):
        reader = SettingsFileReader(self.fail_duplicate_section_filepath())
        self.assertRaises(ValueError, reader.read)
    
    def success_filepath(self):
        return os.path.join(TEST_PATH, 'definition.def')
    
    def success_settings(self):
        return {'features': ['Tüüp', 'Alamtüüp', 'Lisateenus', 'Asukoht', 'Rikke põhjus',
                             'Hinnanguline põhjustaja', 'Kontakti kirjeldus', 'Täitja selgitus'],
                'label': 'Lahendus/Tegevus',
                'confidence': 'Lahendus/Tegevus kindlus'}
        
    def fail_nosection_filepath(self):
        return os.path.join(TEST_PATH, 'definition_nosection.def')
    
    def fail_invalid_section_filepath(self):
        return os.path.join(TEST_PATH, 'definition_invalid_section.def')

    def fail_duplicate_section_filepath(self):
        return os.path.join(TEST_PATH, 'definition_duplicate.def')


class SettingsWithSynonymsLoadingTest(unittest.TestCase):
    
    def test_loading_succeeds(self):
        settings = Settings.read(self.success_definitions(), self.success_synonyms())
        self.assertDictEqual(settings.export(), self.serialized())
    
    def success_definitions(self):
        return os.path.join(TEST_PATH, 'definition.def')
    
    def success_synonyms(self):
        return os.path.join(TEST_PATH, 'testsynonyms.txt')
    
    def serialized(self):
        return {'features': ['Tüüp', 'Alamtüüp', 'Lisateenus', 'Asukoht', 'Rikke põhjus',
                             'Hinnanguline põhjustaja', 'Kontakti kirjeldus', 'Täitja selgitus'],
                'label': 'Lahendus/Tegevus',
                'confidence': 'Lahendus/Tegevus kindlus',
                'synmap': {'kl': 'kl',
                           'klient': 'kl',
                           'äöü': 'kl', # test utf-8
                           'restart': 'restart',
                           'reset': 'restart',
                           'äöõ': 'restart',
                           'teler': 'teler',
                           'telekas': 'teler'}}
