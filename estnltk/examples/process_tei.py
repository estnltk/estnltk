# -*- coding: utf-8 -*-
"""
Example that reads full AA TEI corpus and processes it.
"""
from __future__ import unicode_literals, print_function, absolute_import

from ..teicorpus import parse_tei_corpora, parse_tei_corpus
from ..core import AA_PATH

from pprint import pprint
import os

texts = parse_tei_corpora(os.path.join(AA_PATH))
for text in texts:
    print(text['title'], text['file'])
    text.compute_named_entities()
    text.compute_clauses()
    text.compute_verb_chains()
    text.compute_timexes()
