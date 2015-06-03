# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from ..teicorpus import parse_tei_corpora
from ..core import AA_PATH

import unittest


class TeiTest(unittest.TestCase):

    def test_parse_tei(self):
        docs = parse_tei_corpora(AA_PATH, 'tea_AA_00')
        self.assertEqual(53, len(docs))
