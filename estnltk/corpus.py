# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function


'''
from estnltk.core import PMNEWS_PATH, get_filenames
from estnltk.morf import PyVabamorfAnalyzer

import codecs
import os

from pprint import pprint


'''



    

            

#class PlaintextCorpusImporter(object):
    #'''Class for importing plain text corpora.'''
    
    #def __init__(self, root_path, prefix = '', suffix = '', importer=PlainTextDocumentImporter()):
        #'''Initialize plaintext corpus importer.
        
        #Parameters:
        
        #root_path - str
            #path of the directory containing the corpus documents.
        #prefix - str
            #prefix that the document filenames must have
        #suffix - str
            #suffix of the document filenames
        #'''
        #self._root_path = root_path
        #self._prefix = prefix
        #self._suffix = suffix
        #self._importer = importer

    #def read(self):
        #documents = []
        #for fnm in get_filenames(self._root_path, self._prefix, self._suffix):
            #abs_path = os.path.join(self._root_path, fnm)
            #document = self._importer(codecs.open(abs_path, 'rb', 'utf-8').read())
            #document['filename'] = fnm
            #document['abs_path'] = abs_path
            #documents.append(document)
        #return documents

'''
importer = PlainTextDocumentImporter()
corpus = importer(u'See on esimene lõik. Esimese lõigu sisu\n  See on teine lõik.')

print corpus

analyzer = PyVabamorfAnalyzer()
corpus = analyzer(corpus)

pprint(corpus)
'''
'''
analyzer = PyVabamorfAnalyzer()
            
importer = PlaintextCorpusImporter(PMNEWS_PATH, suffix='.txt')
corpus = importer.read()
corpus[0] = analyzer(corpus[0])
pprint(corpus)
'''


