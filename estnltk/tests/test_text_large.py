# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os
import timeit
from pprint import pprint

from ..text import Text
from ..teicorpus import parse_tei_corpus
from ..core import AA_PATH

# dummy initialization of everything we may test
dummy = Text('Tere maailm!').compute_analysis().compute_clauses().compute_named_entities().compute_verb_chains()

docs = parse_tei_corpus(os.path.join(AA_PATH, 'tea_AA_00_1.tasak.xml'))
plain = docs[5].text*10
n = len(plain)//2
half1, half2 = plain[:n], plain[n:]

def large_document():
    Text(plain).compute_analysis()

def small_documents():
    Text(half1).compute_analysis()
    Text(half2).compute_analysis()

class LargeTextTest(unittest.TestCase):
    """Test for ensuring that processing time of texts has linear complexity.
    This is good for detecting inefficient loops that depend on text size/complexity.
    """

    def test_time(self):
        number = 3
        large_time = timeit.timeit("large_document()", setup="from __main__ import large_document, small_documents", number=number)
        small_time = timeit.timeit("small_documents()", setup="from __main__ import large_document, small_documents", number=number)

print (timeit.timeit("large_document()", setup="from __main__ import large_document, small_documents", number=3))
print (timeit.timeit("small_documents()", setup="from __main__ import large_document, small_documents", number=3))