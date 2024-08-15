# -*- coding: utf-8 -*-

import unittest
import operator
from ..morf import analyze

from pprint import pprint


class AnalysisTest(unittest.TestCase):
    
    def test_analyse_with_stem(self):
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
                             'lemma': 'läkma',
                             'partofspeech': 'V',
                             'root': 'läk',
                             'root_tokens': ['läk']}],
                             'text': 'läks'},
             {'analysis': [{'clitic': '',
                            'ending': 'tega',
                            'form': 'pl kom',
                            'lemma': 'omas',
                            'partofspeech': 'S',
                            'root': 'omas',
                            'root_tokens': ['omas']}],
                            'text': 'omastega'},
             {'analysis': [{'clitic': '',
                            'ending': '0',
                            'form': 'adt',
                            'lemma': 'rappa',
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


