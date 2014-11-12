# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import unittest

from estnltk.tokenize import tokenize, Tokenizer
from nltk.tokenize import RegexpTokenizer
from pprint import pprint

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
        return [{'text': u'see',
                 'start': 1002,
                 'rel_start': 2,
                 'end': 1005,
                 'rel_end': 5
                 },
                 {'text': u'on',
                 'start': 1006,
                 'rel_start': 6,
                 'end': 1008,
                 'rel_end': 8
                 },
                 {'text': u'text',
                 'start': 1022,
                 'rel_start': 22,
                 'end': 1026,
                 'rel_end': 26
                 }]
    
    def tokenizer(self):
        return RegexpTokenizer('\s+', gaps=True, discard_empty=True)

    def bad_tokenizer(self):
        return RegexpTokenizer('\s*', gaps=True, discard_empty=True)

        
class TokenizerTest(unittest.TestCase):
    '''Test the estnltk.tokenize.Tokenizer class.'''
    
    def test_tokenize_empty(self):
        tokenizer = Tokenizer()
        tokenized = tokenizer(self.empty_document())
        self.assertDictEqual(tokenized, self.empty_tokenized())
    
    def empty_document(self):
        return ''
    
    def empty_tokenized(self):
        return {'text': u'',
                'start': 0,
                'rel_start': 0,
                'end': 0,
                'rel_end': 0,
                'paragraphs': []}

    def test_simple(self):
        tokenizer = Tokenizer()
        tokenized = tokenizer.tokenize(self.simple_document())
        self.assertDictEqual(tokenized, self.simple_tokenized())
    
    def simple_document(self):
        return 'Esimene lõik.\nTeine'
    
    def simple_tokenized(self):
        return {'end': 19,
                'paragraphs': [{'end': 13,
                                'rel_end': 13,
                                'rel_start': 0,
                                'sentences': [{'end': 13,
                                                'rel_end': 13,
                                                'rel_start': 0,
                                                'start': 0,
                                                'text': u'Esimene l\xf5ik.',
                                                'words': [{'end': 7,
                                                        'rel_end': 7,
                                                        'rel_start': 0,
                                                        'start': 0,
                                                        'text': u'Esimene'},
                                                        {'end': 13,
                                                        'rel_end': 13,
                                                        'rel_start': 8,
                                                        'start': 8,
                                                        'text': u'l\xf5ik.'}]}],
                                'start': 0,
                                'text': u'Esimene l\xf5ik.'},
                                {'end': 19,
                                'rel_end': 19,
                                'rel_start': 14,
                                'sentences': [{'end': 19,
                                                'rel_end': 5,
                                                'rel_start': 0,
                                                'start': 14,
                                                'text': u'Teine',
                                                'words': [{'end': 19,
                                                        'rel_end': 5,
                                                        'rel_start': 0,
                                                        'start': 14,
                                                        'text': u'Teine'}]}],
                                'start': 14,
                                'text': u'Teine'}],
                'rel_end': 19,
                'rel_start': 0,
                'start': 0,
                'text': u'Esimene l\xf5ik.\nTeine'}
                
if __name__ == '__main__':
    unittest.main()
