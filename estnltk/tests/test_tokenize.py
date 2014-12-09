# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.names import *
from estnltk.tokenize import Tokenizer, tokenize

from nltk.tokenize import RegexpTokenizer

from pprint import pprint
import unittest


class TokenizerTest(unittest.TestCase):
    '''Test the estnltk.tokenize.Tokenizer class.'''
    
    def test_tokenize_empty(self):
        tokenizer = Tokenizer()
        tokenized = tokenizer(self.empty_document())
        self.assertDictEqual(tokenized, self.empty_tokenized())
    
    def empty_document(self):
        return ''
    
    def empty_tokenized(self):
        return {TEXT: '',
                START: 0,
                REL_START: 0,
                END: 0,
                REL_END: 0,
                PARAGRAPHS: []}

    def test_simple(self):
        tokenizer = Tokenizer()
        tokenized = tokenizer.tokenize(self.simple_document()).to_json()
        self.assertDictEqual(tokenized, self.simple_tokenized())
    
    def simple_document(self):
        return 'Esimene lõik.\n\nTeine'
    
    def simple_tokenized(self):
        return {END: 20,
                PARAGRAPHS: [{END: 13,
                                REL_END: 13,
                                REL_START: 0,
                                SENTENCES: [{END: 13,
                                                REL_END: 13,
                                                REL_START: 0,
                                                START: 0,
                                                TEXT: 'Esimene l\xf5ik.',
                                                WORDS: [{END: 7,
                                                        REL_END: 7,
                                                        REL_START: 0,
                                                        START: 0,
                                                        TEXT: 'Esimene'},
                                                        {END: 13,
                                                        REL_END: 13,
                                                        REL_START: 8,
                                                        START: 8,
                                                        TEXT: 'l\xf5ik.'}]}],
                                START: 0,
                                TEXT: 'Esimene l\xf5ik.'},
                                {END: 20,
                                REL_END: 20,
                                REL_START: 15,
                                SENTENCES: [{END: 20,
                                                REL_END: 5,
                                                REL_START: 0,
                                                START: 15,
                                                TEXT: 'Teine',
                                                WORDS: [{END: 20,
                                                        REL_END: 5,
                                                        REL_START: 0,
                                                        START: 15,
                                                        TEXT: 'Teine'}]}],
                                START: 15,
                                TEXT: 'Teine'}],
                REL_END: 20,
                REL_START: 0,
                START: 0,
                TEXT: 'Esimene l\xf5ik.\n\nTeine'}
                

class TokenizeTest(unittest.TestCase):
    '''Test the estnltk.tokenize.tokenize function.'''
    
    def test_tokenizer(self):
        result = tokenize(self.text(), self.tokenizer(), 1000)
        self.assertListEqual(result, self.result())
    
    def test_tokenize_fails(self):
        '''Some tokenizers cannot be reasonably applied on texts.
        One example is RegexpTokenizer with \s*. The problem is
        that is can match zero characters and thus span_tokenize
        yields wrong results.'''
        self.assertRaises(AssertionError, tokenize, self.text(), self.bad_tokenizer(), 1000)
    
    def text(self):
        return '  see on \n\r\n  \r\n\r \n \t text  '
    
    def result(self):
        return [{TEXT: 'see',
                 START: 1002,
                 REL_START: 2,
                 END: 1005,
                 REL_END: 5
                 },
                 {TEXT: 'on',
                 START: 1006,
                 REL_START: 6,
                 END: 1008,
                 REL_END: 8
                 },
                 {TEXT: TEXT,
                 START: 1022,
                 REL_START: 22,
                 END: 1026,
                 REL_END: 26
                 }]
    
    def tokenizer(self):
        return RegexpTokenizer('\s+', gaps=True, discard_empty=True)

    def bad_tokenizer(self):
        return RegexpTokenizer('\s*', gaps=True, discard_empty=True)

                
if __name__ == '__main__':
    unittest.main()
