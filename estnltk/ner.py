# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from pprint import pprint

from estnltk.estner.settings import Settings
from estnltk.estner.featureextraction import FeatureExtractor

settings = Settings()
tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()

print ('Loading vabadata')
import json
#vabadata = json.loads(open('estnltk/corpora/estner.json').read())
#vabadata['documents'] = vabadata['documents']
#print ('Loaded')

documents = vabadata['documents']

from estnltk.estner.crfsuiteutil import Trainer, Tagger

#trainer = Trainer(settings)
#print ('Training the model')
#model = trainer.train(documents, 'test.bin')


testdocs = analyzer(tokenizer('Maali sõitis Tartust Tallinnasse EL-i nõupidamisele.'))
tagger = Tagger(settings, filename='test.bin')
tagger.tag([testdocs])

pprint (testdocs)
