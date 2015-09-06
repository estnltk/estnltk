# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..disambiguator import Disambiguator
from ..names import *


class DisambiguatorTest(unittest.TestCase):

    # =========================================================
    #  Counting-based tests
    # =========================================================

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
        texts = disambuator.disambiguate(corpus, disambiguate=False, post_disambiguate=False)
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
        texts = [ Text(text, disambiguate=False, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # 1) Count morph analyses without any disambiguation
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [91, 20, 71])
        #print ([countTotal, countH, countNonH])
        texts = [ Text(text, disambiguate=True, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # 2) Count morph analyses before post-disambiguation step,
        #    without pre-disambiguation, but with vabamorf disambiguation
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [51, 0, 51])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate( corpus, disambiguate=True, post_disambiguate=True, pre_disambiguate=False )
        # 3) Count morph analyses after post-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [47, 0, 47])
        #print ([countTotal, countH, countNonH])


    def test_post_disambiguation_2(self):
        corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
                  'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
        #   Mitmesused:
        #      kohale  S_koht+le  S_koha+le
        #      mail   S_maa+l  S_mai+l
        #      summaga  S_summ+ga  S_summa+ga
        texts = [ Text(text, disambiguate=False, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # 1) Count morph analyses without any disambiguation
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [91, 20, 71])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(corpus, pre_disambiguate=True, disambiguate=False, post_disambiguate=False)
        # 2) Count morph analyses after pre-disambiguation step
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        #print ([countTotal, countH, countNonH])
        self.assertListEqual([countTotal, countH, countNonH], [74, 7, 67])
        texts = disambuator.disambiguate(corpus, pre_disambiguate=True, disambiguate=True, post_disambiguate=True)
        # 3) Count morph analyses after all disambiguation steps have been applied
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [47, 4, 43])
        #print ([countTotal, countH, countNonH])


    def test_post_disambiguation_3(self):
        corpus = [['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.'], \
                  ['Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']]
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(corpus, pre_disambiguate=False, disambiguate=True, post_disambiguate=True)
        [countTotal, countH, countNonH] = self.__debug_count_analyses_2(texts)
        self.assertListEqual([countTotal, countH, countNonH], [47, 0, 47])
        #print ([countTotal, countH, countNonH])


    def test_vabamorf_disambiguate_1(self):
        corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
                  'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
        texts = [ Text(text, disambiguate=False, guess=True, propername=True) for text in corpus ]
        texts = [ text.tag_analysis() for text in texts ]
        # 1) Count morph analyses without any disambiguation
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [91, 20, 71])
        #print ([countTotal, countH, countNonH])
        disambuator = Disambiguator()
        texts = disambuator.disambiguate(corpus, disambiguate=True, pre_disambiguate=False, post_disambiguate=False)
        # 2) Count morph analyses when only vabamorf disambiguation was applied
        [countTotal, countH, countNonH] = self.__debug_count_analyses(texts)
        self.assertListEqual([countTotal, countH, countNonH], [51, 0, 51])
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


    def __debug_count_analyses_2(self, collection):
        analyseCountTotal = 0
        analyseCountH     = 0
        analyseCountNotH  = 0
        for docs in collection:
            [countTotal, countH, countNonH] = self.__debug_count_analyses(docs)
            analyseCountTotal += countTotal
            analyseCountH     += countH
            analyseCountNotH  += countNonH
        return [analyseCountTotal, analyseCountH, analyseCountNotH]


    # =========================================================
    #  Comparison-based tests
    # =========================================================
    
    def test_vabamorf_disambiguate_2(self):
        corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
                  'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
                  'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
        # 1) Disambiguation without the Disambiguator class
        texts1 = [ Text(text, disambiguate=True, guess=True, propername=True) for text in corpus ]
        texts1 = [ text.tag_analysis() for text in texts1 ]
        # 2) Disambiguation with the Disambiguator class
        disambuator = Disambiguator()
        texts2 = disambuator.disambiguate(corpus, disambiguate=True, pre_disambiguate=False, post_disambiguate=False)
        # 3) Compare whether in both cases the analyses are the same
        for text1, text2 in zip(texts1, texts2):
            # NB! Analyses in lists word[ANALYSIS] appear at random order, so the 
            # lists need to be sorted before comparisons can be made properly ...
            self.__sort_analyses(text1)
            self.__sort_analyses(text2)
            self.assertDictEqual(text1, text2)


    def __sort_analyses(self, doc):
        for word in doc[WORDS]:
            if ANALYSIS not in word:
                raise Exception( '(!) Error: no analysis found from word: '+str(word) )
            else:
                word[ANALYSIS] = sorted(word[ANALYSIS], \
                    key=lambda x : x[ROOT]+"_"+x[POSTAG]+"_"+x[FORM]+"_"+x[CLITIC] )
        return doc
