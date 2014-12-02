# -*- coding: utf-8 -*-
'''Named entity recognition example.'''
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer, PyVabamorfAnalyzer, NerTagger
from pprint import pprint

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
tagger = NerTagger()

text = '''Eesti Vabariik on riik Põhja-Euroopas. 
Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.

Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.

2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
2006. aastal valiti presidendiks Toomas Hendrik Ilves.
'''

# tag the documents
ner_tagged = tagger(analyzer(tokenizer(text)))

# print the words and their explicit labels in BIO notation
pprint(list(zip(ner_tagged.word_texts, ner_tagged.labels)))

# print words grouped as named entities
pprint (ner_tagged.named_entities)
