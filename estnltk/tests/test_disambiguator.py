# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..disambiguator import Disambiguator
from ..names import *


class DisambiguatorTest(unittest.TestCase):

    def test_pre_disambiguation_1(self):
        corpus = ['Jänes oli parajasti põllu peal. Hunti nähes ta ehmus ja pani jooksu.',\
                  'Talupidaja Jänes kommenteeris, et hunte on viimasel ajal liiga palju siginenud. Tema naaber, talunik Lammas, nõustus sellega.', \
                  'Jänesele ja Lambale oli selge, et midagi tuleb ette võtta. Eile algatasid nad huntidevastase kampaania.']
        texts = [ Text(text, vabamorf_disambiguate=False, post_disambiguate=False, disambiguate=False, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # Count morph analyses before pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [106, 21, 85])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(texts)
        # Count morph analyses after pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [85, 5, 80])
        #print ([countTotal, countH, countNonH])


    def __debug_count_analyses(self, docs):
        analyseCountTotal = 0
        analyseCountH     = 0
        analyseCountNotH  = 0
        for doc in docs:
            for word in doc[WORDS]:
                if ANALYSIS not in word:
                    raise Exception( '(!) Error: no analysis found from word: '+str(word) )
                else:
                    for analysis in word[ANALYSIS]:
                        analyseCountTotal += 1
                        if analysis[POSTAG] == 'H':
                            analyseCountH += 1
                        else:
                            analyseCountNotH += 1
        return [analyseCountTotal, analyseCountH, analyseCountNotH]
