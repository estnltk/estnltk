# -*- coding: utf-8 -*-
'''Temporal expression tagger.'''
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk import ClauseSegmenter
from estnltk import VerbChainDetector
from pprint import pprint

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
segmenter = ClauseSegmenter()
detector = VerbChainDetector()

text = ''''Mis puutub eelolevasse nädalasse, siis neljapäeval ja reedel ei tohiks Sa oma tervist proovile panna.'''
processed = detector(segmenter(analyzer(tokenizer(text))))

# print timex objects
pprint(processed.verb_chains)
