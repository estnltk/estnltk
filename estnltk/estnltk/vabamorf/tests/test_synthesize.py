from __future__ import unicode_literals, print_function

from estnltk.vabamorf.morf_extra import synthesize
import unittest


# noinspection SpellCheckingInspection
class TestSynthesize(unittest.TestCase):
    
    def test_pood(self):
        words = synthesize('pood', 'sg p', partofspeech='S', phonetic=False)
        self.assertListEqual(words, ['poodi'])

    def test_pooma(self):
        words = synthesize('pooma', 'ti', partofspeech='V', phonetic=False)
        self.assertListEqual(words, ['poodi'])
        
    def test_kaitse(self):
        words = synthesize('kaitse', 'sg g', phonetic=False)
        self.assertListEqual(words, ['kaitse', 'kaitsme'])
        
    def test_palk(self):
        words = synthesize('palk', 'sg kom', phonetic=False, guess=False)
        self.assertListEqual(words, ['palgaga', 'palgiga'])
        
    def test_palk2(self):
        words = synthesize('palk', 'sg kom', hint='palga', phonetic=False)
        self.assertListEqual(words, ['palgaga'])
