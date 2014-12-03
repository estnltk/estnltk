# -*- coding: utf-8 -*-
'''Clause detection example.'''
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
from pprint import pprint

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
segmenter = ClauseSegmenter()

text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''
# täpitähed:
#text = '''Mees, kes on Ärma talu juhataja, oli äärmiselt tuttav ja üllatavalt teretas meid.'''

segmented = segmenter(analyzer(tokenizer(text)))

# Clause indices
pprint(list(zip(segmented.words, segmented.clause_indices, segmented.clause_annotations)))

# The clauses themselves
pprint(segmented.clauses)

# Words grouped by clauses
for clause in segmented.clauses:
    pprint(clause.words)
    
