# -*- coding: utf-8 -*-

import unittest

from estnltk.corpus import apply_tokenizer, PlainTextDocumentImporter
from nltk.tokenize import RegexpTokenizer
from pprint import pprint

class ApplyTokenizerTest(unittest.TestCase):
    
    def test_apply_tokenizer(self):
        result = apply_tokenizer(self.text(), self.tokenizer(), 1000)
        self.assertListEqual(result, self.result())
    
    def text(self):
        return u'  see on \n\r\n  \r\n\r \n \t text  '
    
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

        
class PlainTextDocumentImporterTest(unittest.TestCase):
    
    def test_import_empty(self):
        importer = PlainTextDocumentImporter()
        imported = importer(self.empty_document())
        self.assertDictEqual(imported, self.empty_imported())
    
    def empty_document(self):
        return u''
    
    def empty_imported(self):
        return {'text': u'',
                'start': 0,
                'rel_start': 0,
                'end': 0,
                'rel_end': 0,
                'paragraphs': []}

    def test_simple(self):
        importer = PlainTextDocumentImporter()
        imported = importer(self.simple_document())
        self.assertDictEqual(imported, self.simple_imported())
                
    def simple_document(self):
        return u'Esimene lõik.\nTeine'
    
    def simple_imported(self):
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
    