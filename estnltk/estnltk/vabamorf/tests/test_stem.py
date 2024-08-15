# -*- coding: utf-8 -*-

import unittest
import operator
from pprint import pprint

from estnltk.vabamorf.tests.morph_extra import analyze

class StemAnalysisTest(unittest.TestCase):
    
    def test_analyse_with_stem(self):
        # Smoke test for stem=True setting
        # Example text
        example_text = ['läks', 'omastega', 'rappa']
        # Result without stem (default)
        result_wo_stem = \
            [{'analysis': [{'clitic': '',
                            'ending': 's',
                            'form': 's',
                            'lemma': 'minema',
                            'partofspeech': 'V',
                            'root': 'mine',
                            'root_tokens': ['mine']}],
                            'text': 'läks'},
             {'analysis': [{'clitic': '',
                            'ending': 'tega',
                            'form': 'pl kom',
                            'lemma': 'omaksed',
                            'partofspeech': 'S',
                            'root': 'omaksed',
                            'root_tokens': ['omaksed']}],
                            'text': 'omastega'},
             {'analysis': [{'clitic': '',
                            'ending': '0',
                            'form': 'adt',
                            'lemma': 'raba',
                            'partofspeech': 'S',
                            'root': 'raba',
                            'root_tokens': ['raba']}],
                            'text': 'rappa'}]
        # Result with stem
        result_w_stem = \
             [{'analysis': [{'clitic': '',
                             'ending': 's',
                             'form': 's',
                             'partofspeech': 'V',
                             'root': 'läk',
                             'root_tokens': ['läk']}],
                             'text': 'läks'},
             {'analysis': [{'clitic': '',
                            'ending': 'tega',
                            'form': 'pl kom',
                            'partofspeech': 'S',
                            'root': 'omas',
                            'root_tokens': ['omas']}],
                            'text': 'omastega'},
             {'analysis': [{'clitic': '',
                            'ending': '0',
                            'form': 'adt',
                            'partofspeech': 'S',
                            'root': 'rappa',
                            'root_tokens': ['rappa']}],
                            'text': 'rappa'}]
        # Case 1: switch stemming off and on
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=False)
        #pprint(result)
        self.assertEqual( result, result_wo_stem )
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=True)
        #pprint(result)
        self.assertEqual( result, result_w_stem )
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=False)
        self.assertEqual( result, result_wo_stem )
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=True)
        self.assertEqual( result, result_w_stem )

        # Default: result without stem
        result = analyze(example_text, guess=True, propername=True, disambiguate=True)
        self.assertEqual( result, result_wo_stem )


    def test_analyse_compounds_with_stem(self):
        # Example text
        example_text = ['läksid', 'omastehoolekandega', 'rappa']
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=True)
        #pprint(result)
        self.assertEqual( result, \
             [{'analysis': [{'clitic': '',
                            'ending': 'sid',
                            'form': 'sid',
                            'partofspeech': 'V',
                            'root': 'läk',
                            'root_tokens': ['läk']}],
                            'text': 'läksid'},
              {'analysis': [{'clitic': '',
                            'ending': 'ga',
                            'form': 'sg kom',
                            'partofspeech': 'S',
                            'root': 'omas+te_hoole_kande',
                            'root_tokens': ['omaste', 'hoole', 'kande']}],
                            'text': 'omastehoolekandega'},
              {'analysis': [{'clitic': '',
                            'ending': '0',
                            'form': 'adt',
                            'partofspeech': 'S',
                            'root': 'rappa',
                            'root_tokens': ['rappa']}],
                            'text': 'rappa'}] )


    def test_analyse_clitic_with_stem(self):
        # Example text
        example_text = ['automaatjaamgi', 'polnud', 'valmis']
        result = analyze(example_text, guess=True, propername=True, disambiguate=True, stem=True)
        #pprint(result)
        self.assertEqual( result, \
            [{'analysis': [{'clitic': 'gi',
                            'ending': '0',
                            'form': 'sg n',
                            'partofspeech': 'S',
                            'root': 'automaat_jaam',
                            'root_tokens': ['automaat', 'jaam']}],
                            'text': 'automaatjaamgi'},
             {'analysis': [{'clitic': '',
                            'ending': 'nud',
                            'form': 'neg nud',
                            'partofspeech': 'V',
                            'root': 'pol',
                            'root_tokens': ['pol']}],
                            'text': 'polnud'},
             {'analysis': [{'clitic': '',
                            'ending': '0',
                            'form': '',
                            'partofspeech': 'A',
                            'root': 'valmis',
                            'root_tokens': ['valmis']}],
                            'text': 'valmis'}] )

