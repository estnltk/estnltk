# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..names import *
from pprint import pprint

class WordnetTaggerTest(unittest.TestCase):

    def test_synsets(self):
        kwargs = {
            'pos': True,
            'variants': True
            #'var_sense': True,
            #'relations': ['has_hyponym', 'has_hyperonym']
        }
        plain = 'Laisk mees magas'
        text = Text(plain, **kwargs)
        df = text.get.word_texts.postags.word_literals.as_dataframe
        #print(df)
        #pprint(text)
