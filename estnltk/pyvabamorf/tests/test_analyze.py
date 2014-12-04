# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest
import operator
from estnltk.pyvabamorf import analyze
from estnltk.pyvabamorf.morf import trim_phonetics, get_group_tokens, analysis_as_dict, convert, deconvert
from estnltk.pyvabamorf.vabamorf import Analysis
from pprint import pprint
from functools import reduce

class TrimPhoneticsTest(unittest.TestCase):
    
    def test_tilde(self):
        self.assertEqual(trim_phonetics('~'), '~')
        
    def test_questionmark(self):
        self.assertEqual(trim_phonetics('?'), '?')
    
    def test_rbracket(self):
        self.assertEqual(trim_phonetics(']'), ']')
        
    def test_lessthan(self):
        self.assertEqual(trim_phonetics('<'), '<')
        
    def test_phonetics(self):
        self.assertEqual(trim_phonetics('~~???ab]c<d'), 'abcd')


class TokensTest(unittest.TestCase):

    def get_tokens(self, root):
        return reduce(operator.add, get_group_tokens(root))

    def test_simple(self):
        tokens = self.get_tokens('all_+maa_raud_tee_jaam~~+')
        self.assertListEqual(tokens, ['all', 'maa', 'raud', 'tee', 'jaam'])

    def test_hyphen_grouping(self):
        tokens = self.get_tokens('saunameheks-tallimeheks-majahoidjaks')
        self.assertListEqual(tokens, ['saunameheks', 'tallimeheks', 'majahoidjaks'])

    def test_underscore(self):
        tokens = self.get_tokens('_')
        self.assertListEqual(tokens, ['_'])
        
    def test_plus(self):
        tokens = self.get_tokens('+')
        self.assertListEqual(tokens, ['+'])
        
    def test_equalmark(self):
        tokens = self.get_tokens('=')
        self.assertListEqual(tokens, ['='])
    
    def test_ltmark(self):
        tokens = self.get_tokens('<')
        self.assertListEqual(tokens, ['<'])
   
    def test_bracketclose(self):
        tokens = self.get_tokens(']')
        self.assertListEqual(tokens, [']'])
        
    def test_hyphen(self):
        tokens = self.get_tokens('-')
        self.assertListEqual(tokens, ['-'])
        

class AnalysisAsDictTest(unittest.TestCase):
    
    def test_verb_phonetic_compound(self):
        self.assertDictEqual(analysis_as_dict(self.verbanalysis(), True, True),
                             self.verb_phonetic_compound())
    
    def test_verb_compound(self):
        self.assertDictEqual(analysis_as_dict(self.verbanalysis(), False, True),
                             self.verb_compound())
    
    def test_verb_phonetic(self):
        self.assertDictEqual(analysis_as_dict(self.verbanalysis(), True, False),
                             self.verb_phonetic())
    
    def test_verb(self):
        self.assertDictEqual(analysis_as_dict(self.verbanalysis(), False, False),
                             self.verb())
                             
    def test_verb_default_args(self):
        self.assertDictEqual(analysis_as_dict(self.verbanalysis()),
                             self.verb_phonetic_compound())

    def verbanalysis(self):
        return Analysis(convert('l<aul'),
                        convert('b'),
                        convert(''),
                        convert('V'),
                        convert('b'))
    
    def verb_phonetic_compound(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'l<aul'}
    
    def verb_compound(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'laul'}
                
    def verb_phonetic(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'l<aul'}

    def verb(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'laul'}

    def substantiveanalysis(self):
        return Analysis(convert('lennuki_k<an]dja'),
                        convert('ile'),
                        convert(''),
                        convert('S'),
                        convert('pl all'))

    def test_substantive_phonetic_compound(self):
        self.assertDictEqual(analysis_as_dict(self.substantiveanalysis(), True, True),
                             self.substantive_phonetic_compound())
    
    def test_substantive_compound(self):
        self.assertDictEqual(analysis_as_dict(self.substantiveanalysis(), False, True),
                             self.substantive_compound())
    
    def test_substantive_phonetic(self):
        self.assertDictEqual(analysis_as_dict(self.substantiveanalysis(), True, False),
                             self.substantive_phonetic())
    
    def test_substantive(self):
        self.assertDictEqual(analysis_as_dict(self.substantiveanalysis(), False, False),
                             self.substantive())
                             
    def test_substantive_default_args(self):
        self.assertDictEqual(analysis_as_dict(self.substantiveanalysis()),
                             self.substantive_phonetic_compound())

    def substantive_phonetic_compound(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennuki_k<an]dja'}

    def substantive_compound(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennuki_kandja'}
                
    def substantive_phonetic(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennukik<an]dja'}
                
    def substantive(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennukikandja'}
                
                
class TextIsSameAsListTest(unittest.TestCase):
    
    def test_same(self):
        self.run_test(False, False, False)
        
    def test_same_guess(self):
        self.run_test(True, False, False)
    
    def test_same_phonetic(self):
        self.run_test(False, True, False)
    
    def test_same_compound(self):
        self.run_test(False, False, True)
    
    def test_same_heuristic_phonetic(self):
        self.run_test(True, True, False)

    def test_same_heuristic_compound(self):
        self.run_test(True, False, True)
        
    def test_same_phonetic_compound(self):
        self.run_test(False, True, True)
    
    def run_test(self, guess, phonetic, compound):
        text_output = analyze(self.text(),
                              guess=guess,
                              phonetic=phonetic,
                              compound=compound )
        list_output = analyze(self.text().split(),
                              guess=guess,
                              phonetic=phonetic,
                              compound=compound )
        self.assertListEqual(text_output, list_output)
    
    def text(self):
        # http://luuletused.ee/1005/elu/hetke-volu
        return '''Ma tahaks suudelda päikesekiiri 
                vat nii ihalevad mu huuled päikese suule.. 
                Ma tahaks tantsida kesksuvises vihmas 
                vat nii tunglevad minu tunded südames suures 

                Keegi kord ütles, et ära karda 
                armastus saab aja jooksul ainult kasvada 
                Võta kõik vastu, mis sulle pakutakse, 
                sest see, mis sulle antakse 
                on sinu jaoks loodud'''


                
if __name__ == '__main__':
    unittest.main()
