# -*- coding: utf-8 -*-
'''Clause detection example.'''
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
from pprint import pprint

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
segmenter = ClauseSegmenter()

text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''

segmented = segmenter(analyzer(tokenizer(text)))
pprint(segmented.clauses)

