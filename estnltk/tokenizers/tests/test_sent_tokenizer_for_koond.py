# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..sent_tokenizer_for_koond import SentenceTokenizerForKoond

#import nltk.data
#tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')

tokenizer = SentenceTokenizerForKoond()

class SentenceTokenizerForKoondTest(unittest.TestCase):

    def test_dates_and_years_1(self):
        text = '''Bänd , mis moodustati 1968 . aastal .
        Nad tähistavad oma sünnipäeva töiselt – 3 . septembril on Vanemuise kontserdimajas galakontsert .
        Ning juubeliaasta lõppkontsert toimub 22 . oktoobril Sakala keskuses .
        Aeg peaks jääma 16 . –18 . juuli vahele .
        1960 . aastal tõepoolest alustati .'''
        expected_texts = ['Bänd , mis moodustati 1968 . aastal .', \
                          'Nad tähistavad oma sünnipäeva töiselt – 3 . septembril on Vanemuise kontserdimajas galakontsert .',\
                          'Ning juubeliaasta lõppkontsert toimub 22 . oktoobril Sakala keskuses .', \
                          'Aeg peaks jääma 16 . –18 . juuli vahele .', \
                          '1960 . aastal tõepoolest alustati .']
        expected_spans = [(0, 37), (46, 143), (152, 222), (231, 272), (281, 316)]
        texts, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        self.assertListEqual(expected_texts, texts)
        self.assertListEqual(expected_spans, spans)


    def test_no_space_between_punct_and_words_1(self):
        text = 'Iga päev teeme valikuid.Valime kõike alates pesupulbrist ja lõpetades autopesulatega.Jah, iga päev teeme valikuid.'
        expected_texts = ['Iga päev teeme valikuid.', \
                          'Valime kõike alates pesupulbrist ja lõpetades autopesulatega.', \
                          'Jah, iga päev teeme valikuid.']
        expected_spans = [(0, 24), (24, 85), (85, 114)]
        texts, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        self.assertListEqual(expected_texts, texts)
        self.assertListEqual(expected_spans, spans)


    def test_break_between_parentheses(self):
        # a sentence break shouldn't be between the parentheses
        text = '''Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .
        ( " Mis siis õieti tahetakse ? " , 1912 ) .
        ( " Easy FM , soft hits ! " ) .'''
        expected_texts = ['Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .', \
                          '( " Mis siis õieti tahetakse ? " , 1912 ) .', \
                          '( " Easy FM , soft hits ! " ) .']
        expected_spans = [(0, 75), (84, 127), (136, 167)]
        texts, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        self.assertListEqual(expected_texts, texts)
        self.assertListEqual(expected_spans, spans)


    def test_break_after_parentheses(self):
        text = '''Eestlastest jõudsid punktikohale Tipp ( 2. ) ja Täpp ( 4. ) ja Käpp ( 7. ) .
        Eesti Päevalehes ( 21.01. ) ilmunud uudisnupuke kuulub kahjuks libauudiste rubriiki .
        Murelik lugeja kurdab ( EPL 31.03. ) , et valla on pääsenud kolmas maailmasõda .'''
        expected_texts = ['Eestlastest jõudsid punktikohale Tipp ( 2. ) ja Täpp ( 4. ) ja Käpp ( 7. ) .', \
                          'Eesti Päevalehes ( 21.01. ) ilmunud uudisnupuke kuulub kahjuks libauudiste rubriiki .', \
                          'Murelik lugeja kurdab ( EPL 31.03. ) , et valla on pääsenud kolmas maailmasõda .']
        expected_spans = [(0, 76), (85, 170), (179, 259)]
        texts, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        self.assertListEqual(expected_texts, texts)
        self.assertListEqual(expected_spans, spans)
        
    def test_break_before_comma_and_lowercase(self):
        text = ''' ETV-s esietendub homme " Õnne 13 ! " , mis kuu aja eest jõudis lavale Ugalas .
        Naise küsimusele : " Kes on tema uus sekretär ? " , vastas Jaak suure entusiasmiga .
        Lavale astuvad jõulise naissolistiga Conflict OK ! , kitarripoppi mängivad Claires Birthday ja Seachers .'''
        expected_texts = [' ETV-s esietendub homme " Õnne 13 ! " , mis kuu aja eest jõudis lavale Ugalas .', \
                          'Naise küsimusele : " Kes on tema uus sekretär ? " , vastas Jaak suure entusiasmiga .', \
                          'Lavale astuvad jõulise naissolistiga Conflict OK ! , kitarripoppi mängivad Claires Birthday ja Seachers .']
        expected_spans = [(0, 79), (88, 172), (181, 286)]
        texts, spans = tokenizer.tokenize(text), tokenizer.span_tokenize(text)
        self.assertListEqual(expected_texts, texts)
        self.assertListEqual(expected_spans, spans)
        
