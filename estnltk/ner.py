# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from pprint import pprint

from estnltk.estner.settings import Settings
from estnltk.estner.featureextraction import FeatureExtractor

settings = Settings()
pprint(settings)


fe = FeatureExtractor(settings)

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()

vabadata = analyzer(tokenizer('Mees nimega Andrus Ansip käis Brüsselis Euroopa Liidu nõupidamisel. Seal sai selgeks et NATO on siin.'))
