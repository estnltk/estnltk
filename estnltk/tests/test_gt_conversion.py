# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..names import *
from ..converters.gt_conversion import convert_to_gt


class GTconverterTest(unittest.TestCase):

    def test_gt_conversion_0(self):
        text = Text('Rändur võttis istet.')
        text.tag_analysis()
        convert_to_gt(text)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        # By default, original FS morph format is preserved:
        self.assertListEqual(results, ['  word_texts postags forms', \
                                       '0     Rändur       S  sg n', \
                                       '1     võttis       V     s', \
                                       '2      istet       S  sg p', \
                                       '3          .       Z      '])
        # GT analyses are stored in the text object in separate layer
        self.assertTrue( GT_WORDS in text )
        gt_analyses = [w[ANALYSIS] for w in text[GT_WORDS]]
        self.assertListEqual(gt_analyses, [ \
          [{'form': 'Sg Nom', 'root': 'rändur', 'clitic': '', 'root_tokens': ['rändur'], 'lemma': 'rändur', 'ending': '0', 'partofspeech': 'S'}], \
          [{'form': 'Pers Prt Ind Sg 3 Aff', 'root': 'võt', 'clitic': '', 'root_tokens': ['võt'], 'lemma': 'võtma', 'ending': 'is', 'partofspeech': 'V'}], \
          [{'form': 'Sg Par', 'root': 'iste', 'clitic': '', 'root_tokens': ['iste'], 'lemma': 'iste', 'ending': 't', 'partofspeech': 'S'}], \
          [{'form': '', 'root': '.', 'clitic': '', 'root_tokens': ['.'], 'lemma': '.', 'ending': '', 'partofspeech': 'Z'}]] )


    def test_gt_conversion_1(self):
        text = Text('Rändur võttis seljakotist vilepilli ja tõstis huultele.')
        text.tag_analysis()
        convert_to_gt(text, layer_name=WORDS)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        self.assertListEqual(results, ['    word_texts postags                  forms', \
                                       '0       Rändur       S                 Sg Nom', \
                                       '1       võttis       V  Pers Prt Ind Sg 3 Aff', \
                                       '2  seljakotist       S                 Sg Ela', \
                                       '3    vilepilli       S                 Sg Par', \
                                       '4           ja       J                       ', \
                                       '5       tõstis       V  Pers Prt Ind Sg 3 Aff', \
                                       '6     huultele       S                 Pl All', \
                                       '7            .       Z                       '] )

    def test_gt_conversion_2(self):
        text = Text('Ärge peatuge: siin ei tohi kiirust vähendada!')
        text.tag_analysis()
        convert_to_gt(text, layer_name=WORDS)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        self.assertListEqual(results, ['  word_texts postags                    forms',\
                                       '0       Ärge       V  Pers Prs Imprt Pl 2 Neg',\
                                       '1    peatuge       V      Pers Prs Imprt Pl 2',\
                                       '2          :       Z                         ',\
                                       '3       siin       D                         ',\
                                       '4         ei       V                      Neg',\
                                       '5       tohi       V         Pers Prs Ind Neg',\
                                       '6    kiirust       S                   Sg Par',\
                                       '7  vähendada       V                      Inf',\
                                       '8          !       Z                         ' ] )

    def test_gt_conversion_3(self):
        text = Text('Oleksid Sa siin olnud, siis oleksid nad ära läinud.')
        text.tag_analysis()
        convert_to_gt(text, layer_name=WORDS)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        self.assertListEqual(results, ['   word_texts postags                        forms',\
                                       '0     Oleksid       V       Pers Prs Cond Sg 2 Aff',\
                                       '1          Sa       P                       Sg Nom',\
                                       '2        siin       D                             ',\
                                       '3       olnud     A|V  |Pers Prt Prc|Pl Nom|Sg Nom',\
                                       '4           ,       Z                             ',\
                                       '5        siis       D                             ',\
                                       '6     oleksid       V       Pers Prs Cond Pl 3 Aff',\
                                       '7         nad       P                       Pl Nom',\
                                       '8         ära       D                             ',\
                                       '9      läinud     A|V  |Pers Prt Prc|Pl Nom|Sg Nom',\
                                       '10          .       Z                             ' ] )


    def test_gt_conversion_4(self):
        text = Text('Mine sa tea!')
        text.tag_analysis()
        convert_to_gt(text, layer_name=WORDS)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        self.assertListEqual(results, ['  word_texts postags                forms',\
                                       '0       Mine       V  Pers Prs Imprt Sg 2',\
                                       '1         sa       P               Sg Nom',\
                                       '2        tea       V  Pers Prs Imprt Sg 2',\
                                       '3          !       Z                     ' ] )

    def test_gt_conversion_5(self):
        text = Text('Sellist asja ei olnud.')
        text.tag_analysis()
        convert_to_gt(text, layer_name=WORDS)
        results = (text.get.word_texts.postags.forms.as_dataframe).to_string().split('\n')
        self.assertListEqual(results, ['  word_texts postags                            forms',\
                                       '0    Sellist       P                           Sg Par',\
                                       '1       asja       S                           Sg Par',\
                                       '2         ei       V                              Neg',\
                                       '3      olnud     A|V  |Pers Prt Ind Neg|Pl Nom|Sg Nom',\
                                       '4          .       Z                                 ' ] )
        


