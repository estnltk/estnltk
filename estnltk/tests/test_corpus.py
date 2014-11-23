# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.corpus import Element, Word, most_frequent, Sentence
from estnltk.names import *

from nltk.tokenize import RegexpTokenizer

from pprint import pprint
from copy import deepcopy
import unittest


class ElementTest(unittest.TestCase):
    
    #### test correct initialization
    def test_basic_initialization(self):
        self.check_values(Element(self.elemdata()))
        self.check_values(Element(**self.elemdata()))
    
    def test_initialization_with_casting(self):
        data = self.elemdata()
        data[TEXT] = data[TEXT].encode('utf-8')
        data[START] = str(data[START])
        data[REL_START] = str(data[REL_START])
        data[END] = str(data[END])
        data[REL_END] = str(data[REL_END])
        elem = Element(data)
        self.check_values(elem)
    
    def check_values(self, elem):
        self.assertIsInstance(elem, Element)
        self.assertEqual(elem.start, 10)
        self.assertEqual(elem.end, 28)
        self.assertEqual(elem.text, 'This is an element')
        self.assertEqual(elem.rel_start, 12)
        self.assertEqual(elem.rel_end, 30)
        self.assertEqual(elem.span, (elem.start, elem.end))
        self.assertEqual(elem.rel_span, (elem.rel_start, elem.rel_end))
        
    def elemdata(self):
        return {TEXT: 'This is an element',
                START: 10, END: 28, REL_START: 12, REL_END: 30}

    #### test missing fields
    def test_init_fails_no_start(self):
        data = self.elemdata()
        del data[START]
        self.assertRaises(KeyError, Element, data)
    
    def test_init_fails_no_rel_start(self):
        data = self.elemdata()
        del data[REL_START]
        self.assertRaises(KeyError, Element, data)
        
    def test_init_fails_no_end(self):
        data = self.elemdata()
        del data[END]
        self.assertRaises(KeyError, Element, data)
    
    def test_init_fails_no_rel_end(self):
        data = self.elemdata()
        del data[REL_END]
        self.assertRaises(KeyError, Element, data)
        
    def test_init_fails_no_text(self):
        data = self.elemdata()
        del data[TEXT]
        self.assertRaises(KeyError, Element, data)
        
    #### test invalid ranges
    def test_invalid_main_span(self):
        data = self.elemdata()
        data[START] = 11
        self.assertRaises(AssertionError, Element, data)
        
    def test_invalid_relative_span(self):
        data = self.elemdata()
        data[REL_START] = 11
        self.assertRaises(AssertionError, Element, data)
        
    def test_negative_start(self):
        data = self.elemdata()
        data[START] = '-1'
        self.assertRaises(AssertionError, Element, data)

    def test_negative_relative_start(self):
        data = self.elemdata()
        data[REL_START] = '-1'
        self.assertRaises(AssertionError, Element, data)


class WordTest(unittest.TestCase):
    
    def test_initialization(self):
        word = self.word()
        
    def data(self):
        return   {ANALYSIS: [{CLITIC: '',
                              ENDING: '0',
                              FORM: 'adt',
                              LEMMA: 'Tallinn',
                              POSTAG: 'H',
                              ROOT: 'Tallinn',
                              ROOT_TOKENS: ['Tallinn']},
                             {CLITIC: '',
                              ENDING: '0',
                              FORM: 'sg g',
                              LEMMA: 'Tallinn',
                              POSTAG: 'H',
                              ROOT: 'Tallinn',
                              ROOT_TOKENS: ['Tallinn']},
                             {CLITIC: '',
                              ENDING: '0',
                              FORM: '',
                              LEMMA: 'tallinna',
                              POSTAG: 'G',
                              ROOT: 'tallinna',
                              ROOT_TOKENS: ['tallinna']},
                             {CLITIC: '',
                              ENDING: '0',
                              FORM: 'sg p',
                              LEMMA: 'Tallinn',
                              POSTAG: 'H',
                              ROOT: 'Tallinn',
                              ROOT_TOKENS: ['Tallinn']}],
                END: 29,
                LABEL: 'B-LOC',
                REL_END: 29,
                REL_START: 21,
                START: 21,
                TEXT: 'Tallinna'}

    def word(self):
        return Word(self.data())

    def test_queries(self):
        word = self.word()
        self.assertEqual(word.text, 'Tallinna')
        self.assertEqual(word.start, 21)
        self.assertEqual(word.end, 29)
        self.assertEqual(word.rel_start, 21)
        self.assertEqual(word.rel_end, 29)
        self.assertEqual(word.label, 'B-LOC')
        # check aggregations
        self.assertEqual(word.ending, '0')
        self.assertEqual(word.lemma, 'Tallinn')
        self.assertEqual(word.root, 'Tallinn')
        self.assertEqual(word.postag, 'H')
        self.assertEqual(word.form, '')
        self.assertEqual(word.clitic, '')
        self.assertEqual(word.root_tokens, ['Tallinn'])
    

class MostFrequentTest(unittest.TestCase):
    '''Test the most_frequent function in corpus.py'''

    def test_empty(self):
        self.assertEqual(most_frequent([]), None)
    
    def test_single_element(self):
        self.assertEqual(most_frequent([5]), 5)
    
    def test_multiple(self):
        self.assertEqual(most_frequent([0,9,1,8,8,2,7,3,6,4,5]), 8)
    
    def test_multiple_comparison(self):
        self.assertEqual(most_frequent([0,9,1,8,8,2,7,3,6,4,8,5,1,1,0,9,9]), 1)


class SentenceTest(unittest.TestCase):
    
    def test_initialization(self):
        sentence = Sentence(self.data())
        # invalid sentence
        data = self.data()
        del data[TEXT]
        self.assertRaises(KeyError, Sentence, data)
        
    def test_queries(self):
        sentence = Sentence(self.data())
        # word related queries
        self.assertListEqual(sentence.texts, ['Pane', 'moos', 'purki', 'tagasi'])
        self.assertListEqual(sentence.lemmas, ['pan', 'moos', 'purk', 'tagasi'])
        self.assertListEqual(sentence.postags, ['S', 'S', 'S', 'D'])
        self.assertListEqual(sentence.forms, ['o', 'sg n', 'adt', ''])
        self.assertListEqual(sentence.roots, ['pan', 'moos', 'purk', 'tagasi'])
        self.assertListEqual(sentence.root_tokens, [['pan'], ['moos'], ['purk'], ['tagasi']])
        self.assertListEqual(sentence.spans, [(0, 4), (5, 9), (10, 15), (16, 22)])
        self.assertListEqual(sentence.rel_spans, [(0, 4), (5, 9), (10, 15), (16, 22)])
    
    def data(self):
        return   {END: 22,
                  REL_END: 22,
                  REL_START: 0,
                  START: 0,
                  TEXT: 'Pane moos purki tagasi',
                  WORDS: [{ANALYSIS: [{CLITIC: '',
                                             ENDING: 'e',
                                             FORM: 'pl p',
                                             LEMMA: 'pan',
                                             POSTAG: 'S',
                                             ROOT: 'pan',
                                             ROOT_TOKENS: ['pan']},
                                            {CLITIC: '',
                                             ENDING: '0',
                                             FORM: 'o',
                                             LEMMA: 'panema',
                                             POSTAG: 'V',
                                             ROOT: 'pane',
                                             ROOT_TOKENS: ['pane']}],
                              END: 4,
                              REL_END: 4,
                              REL_START: 0,
                              START: 0,
                              TEXT: 'Pane'},
                             {ANALYSIS: [{CLITIC: '',
                                             ENDING: '0',
                                             FORM: 'sg n',
                                             LEMMA: 'moos',
                                             POSTAG: 'S',
                                             ROOT: 'moos',
                                             ROOT_TOKENS: ['moos']}],
                              END: 9,
                              REL_END: 9,
                              REL_START: 5,
                              START: 5,
                              TEXT: 'moos'},
                             {ANALYSIS: [{CLITIC: '',
                                             ENDING: '0',
                                             FORM: 'adt',
                                             LEMMA: 'purk',
                                             POSTAG: 'S',
                                             ROOT: 'purk',
                                             ROOT_TOKENS: ['purk']},
                                            {CLITIC: '',
                                             ENDING: '0',
                                             FORM: 'sg p',
                                             LEMMA: 'purk',
                                             POSTAG: 'S',
                                             ROOT: 'purk',
                                             ROOT_TOKENS: ['purk']}],
                              END: 15,
                              REL_END: 15,
                              REL_START: 10,
                              START: 10,
                              TEXT: 'purki'},
                             {ANALYSIS: [{CLITIC: '',
                                             ENDING: '0',
                                             FORM: '',
                                             LEMMA: 'tagasi',
                                             POSTAG: 'D',
                                             ROOT: 'tagasi',
                                             ROOT_TOKENS: ['tagasi']},
                                            {CLITIC: '',
                                             ENDING: '0',
                                             FORM: '',
                                             LEMMA: 'tagasi',
                                             POSTAG: 'K',
                                             ROOT: 'tagasi',
                                             ROOT_TOKENS: ['tagasi']}],
                              END: 22,
                              REL_END: 22,
                              REL_START: 16,
                              START: 16,
                              TEXT: 'tagasi'}]}


if __name__ == '__main__':
    unittest.main()
    
