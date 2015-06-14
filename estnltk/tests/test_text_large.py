# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os
import timeit
from pprint import pprint

from ..text import Text
from ..teicorpus import parse_tei_corpus
from ..core import AA_PATH

dummy = Text('Tere maailm!').tag_analysis()

docs = parse_tei_corpus(os.path.join(AA_PATH, 'tea_AA_00_1.tasak.xml'))
plain = docs[5].text
n = len(plain)//2
half1, half2 = plain[:n], plain[n:]


def large_document():
    Text(plain).tag_analysis()

def small_documents():
    Text(half1).tag_analysis()
    Text(half2).tag_analysis()


class LargeTextTest(unittest.TestCase):
    """Test for ensuring that basic processing time of texts has linear complexity.
    This is good for detecting inefficient loops that depend on text size/complexity.
    """

    def test_time(self):

        number = 10
        large_time = timeit.timeit(large_document, number=number)
        small_time = timeit.timeit(small_documents, number=number)
        print('Large document: ', large_time)
        print('Small documents:', small_time)
        diff = abs((float(large_time) / float(small_time)) - 1.0)
        self.assertTrue(diff < 0.1) # fail with 10% difference
