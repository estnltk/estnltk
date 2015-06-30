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
        texts = [ Text(text, disambiguate=False, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # Count morph analyses before pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [106, 21, 85])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(texts, vabamorf_disambiguate=False, post_disambiguate=False)
        # Count morph analyses after pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [85, 5, 80])
        #print ([countTotal, countH, countNonH])


    def test_post_disambiguation_1(self):
        corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
                  'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
        #   Mitmesused:
        #      kohale  S_koht+le  S_koha+le
        #      mail   S_maa+l  S_mai+l
        #      summaga  S_summ+ga  S_summa+ga
        texts = [ Text(text, disambiguate=True, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # Count morph analyses before pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [53, 0, 53])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(texts, vabamorf=False, vabamorf_disambiguate=False, post_disambiguate=True )
        # Count morph analyses after pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [49, 0, 49])
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


    def test_vabamorf_disambiguate(self):
        corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
                  'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
        disambuator = Disambiguator()
        # todo: test ei tööta, sest ma pole kindel, kuidas tulemust tuleks kontrollida
        texts = disambuator.disambiguate(corpus, disambiguate=False, vabamorf_disambiguate=True, post_disambiguate=False)
        for orig_text, text in zip(corpus, texts):
            self.assertDictEqual(Text(orig_text).tag_analysis(), text)

