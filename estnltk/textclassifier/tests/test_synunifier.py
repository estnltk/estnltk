# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.synunifier import SynUnifier, SynFileReader
from estnltk.textclassifier.paths import TEST_PATH

import unittest
import json
import os

def first_valid():
    return ['kl', 'klient']

def first_duplicate():
    return ['klaient', 'kl']

def second_valid():
    return ['digiboks', 'db', 'dbox', 'digibox', 'boks']

def invalid_too_few_unique():
    return ['aa', 'aa']

def invalid_different_cases():
    return ['AA', 'aa']

def invalid_empty_string():
    return ['aa', '']

def valid_serialized():
    return {
        'kl': 'kl',
        'klient': 'kl',
        'digiboks': 'digiboks',
        'db': 'digiboks',
        'dbox': 'digiboks',
        'digibox': 'digiboks',
        'boks': 'digiboks'}

def invalid_serialized():
    d = valid_serialized()
    del d['digiboks']
    return d

def compatible_serialized():
    return {
        'kl': 'kl',
        'klient': 'KL',
        'digiboks': 'digiboks',
        'db': 'digiboks',
        'DBOX': 'digiboks',
        'digibox': 'digiboks',
        'boks': 'digiBoks'}

class CorrectSynUnifierConstruction(unittest.TestCase):
    
    def test_construction_succeeds_with_valid_serialized_dictionary(self):
        su = SynUnifier(valid_serialized())
    
    def test_construction_suceeds_with_compatible_serialized_dictionary(self):
        su = SynUnifier(compatible_serialized())
    
    def test_construction_succeeds_with_valid_synsets(self):
        su = SynUnifier()
        su.add_synset(first_valid())
        su.add_synset(second_valid())


class IncorrectSynUnifierConstruction(unittest.TestCase):
    
    def test_construction_fails_with_invalid_synset(self):
        su = SynUnifier()
        self.assertRaises(ValueError, su.add_synset, invalid_too_few_unique())
    
    def test_construction_fails_with_uppercase_duplicates(self):
        su = SynUnifier()
        self.assertRaises(ValueError, su.add_synset, invalid_different_cases())

    def test_construction_fails_with_duplicate_synsets(self):
        su = SynUnifier()
        su.add_synset(first_valid())
        self.assertRaises(ValueError, su.add_synset, first_duplicate())

    def test_construction_fails_with_empty_strings(self):
        su = SynUnifier()
        self.assertRaises(ValueError, su.add_synset, invalid_empty_string())

    def test_construction_fails_with_invalid_serialized_dictionary(self):
        self.assertRaises(ValueError, SynUnifier, invalid_serialized())


class SerializationTest(unittest.TestCase):
    
    def test_serialization(self):
        su = SynUnifier(valid_serialized())
        self.assertDictEqual(su.export(), valid_serialized())

    def test_compatible_is_fixed_to_fully_correct(self):
        su = SynUnifier(compatible_serialized())
        self.assertDictEqual(su.export(), valid_serialized())
        
    def test_serialization_is_json_compatible(self):
        serialized = json.dumps(valid_serialized())
        

class UnificationTest(unittest.TestCase):
    
    def test_simple(self):
        su = SynUnifier(valid_serialized())
        self.assertEqual(su.unify('db'), 'digiboks')
        self.assertEqual(su.unify('digiboks'), 'digiboks')
    
    def test_word_not_in_synsets(self):
        su = SynUnifier(valid_serialized())
        self.assertEqual(su.unify('unknown'), 'unknown')
        
    def test_simple(self):
        su = SynUnifier(valid_serialized())
        self.assertEqual(su.unify('DB'), 'digiboks')
        self.assertEqual(su.unify('Digiboks'), 'digiboks')


class SynFileReaderTest(unittest.TestCase):

    def test_reading_succeeds(self):
        reader = SynFileReader(self.filepath())
        unifier = reader.read()
        serialized = unifier.export()
        self.assertDictEqual(serialized, self.serialized())

    def filepath(self):
        return os.path.join(TEST_PATH, 'testsynonyms.txt')
    
    def serialized(self):
        return {'kl': 'kl',
                'klient': 'kl',
                'äöü': 'kl', # test utf-8
                'restart': 'restart',
                'reset': 'restart',
                'äöõ': 'restart',
                'teler': 'teler',
                'telekas': 'teler'}

