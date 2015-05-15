# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer, PyVabamorfAnalyzer, NerTagger, Corpus
from pprint import pprint

import unittest

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
tagger = NerTagger()

text = '''Eesti Vabariik on riik Põhja-Euroopas.
Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.

Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.

2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
2006. aastal valiti presidendiks Toomas Hendrik Ilves.

Inimestelt saadud vihjed pole veel politseil aidanud leida 43-aastast Kajar Paasi, kes tema naise sõnul Ardus maanteel rööviti.
Tuhanded Šotimaa kodud on lääneranniku piirkondi tabanud „ilmapommi“-tormi tõttu elektrita
'''


class NerTest(unittest.TestCase):
    
    def test_basic(self):
        ner_tagged = tagger(analyzer(tokenizer(text)))
        self.assertEqual(len(ner_tagged.named_entities), 13)

    def test_second_time(self):
        # just repeat the same thing to test if anything breaks second time
        self.test_basic()
        
    def test_basic_json(self):
        ner_tagged = Corpus.construct(tagger(analyzer(tokenizer(text)).to_json()))
        self.assertEqual(len(ner_tagged.named_entities), 13)

if __name__ == '__main__':
    unittest.main()
