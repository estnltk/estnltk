# -*- coding: utf-8 -*-


from estnltk.core import PMNEWS_PATH, get_filenames
from estnltk.morf import PyVabamorfAnalyzer

import codecs
import os

from itertools import izip
from pprint import pprint

import nltk.data

from nltk.corpus.reader import CorpusReader
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer

 
def apply_tokenizer(text, tokenizer, start=0):
    '''Function that applies given tokenizer on given text.
    
    Parameters:
    
    text: str
        The text to be tokenized.
    tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
        The tokenizer to use.
    start: int
        the absolute start position of the given text. Only required when this text is a substring
        of a larger text. Such as a sentence in a paragraph.
    '''
    end = start + len(text)
    toks = tokenizer.tokenize(text)
    spans = tokenizer.span_tokenize(text)
    results = []
    for tok, (tokstart, tokend) in izip(toks, spans):
        d = {'text': tok,
             'start': start + tokstart,
             'end': start + tokend,
             'rel_start': tokstart,
             'rel_end': tokend}
        results.append(d)
    return results

    
class PlainTextDocumentImporter(object):
    '''Class for importing plain text data.'''
    
    def __init__(self, **kwargs):
        '''Initialize plaintext document importer.
        
        Keyword parameters:
        
        paragraph_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Tokenizer used to create paragraphs.
        sentence_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Tokenizer used to create sentences.
        word_tokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer
            Tokenizer used to create words.

        Default paragraph tokenizer uses newlines to separate paragraphs.
        Default sentence tokenizer is NLTK default PunktSentenceTokenizer for Estonian.
        Default word tokenizer 
        '''
        self._paragraph_tokenizer = kwargs.get('paragraph_tokenizer',
            RegexpTokenizer('\s*\n\s*', gaps=True, discard_empty=True))
        self._sentence_tokenizer = kwargs.get('sentence_tokenizer',
            nltk.data.load('tokenizers/punkt/estonian.pickle'))
        self._word_tokenizer = kwargs.get('word_tokenizer',
            PunktWordTokenizer())

    def __call__(self, text):
        text = unicode(text)
        paras = apply_tokenizer(text, self._paragraph_tokenizer)
        for para in paras:
            sentences = apply_tokenizer(para['text'], self._sentence_tokenizer, para['start'])
            for sent in sentences:
                sent['words'] = words = apply_tokenizer(sent['text'], self._word_tokenizer, sent['start'])
            para['sentences'] = sentences
        return {'text': text,
                'paragraphs': paras,
                'start': 0,
                'rel_start': 0,
                'end': len(text),
                'rel_end': len(text)}
            

class PlaintextCorpusImporter(object):
    '''Class for importing plain text corpora.'''
    
    def __init__(self, root_path, prefix = '', suffix = '', importer=PlainTextDocumentImporter()):
        '''Initialize plaintext corpus importer.
        
        Parameters:
        
        root_path - str
            path of the directory containing the corpus documents.
        prefix - str
            prefix that the document filenames must have
        suffix - str
            suffix of the document filenames
        '''
        self._root_path = root_path
        self._prefix = prefix
        self._suffix = suffix
        self._importer = importer

    def read(self):
        documents = []
        for fnm in get_filenames(self._root_path, self._prefix, self._suffix):
            abs_path = os.path.join(self._root_path, fnm)
            document = self._importer(codecs.open(abs_path, 'rb', 'utf-8').read())
            document['filename'] = fnm
            document['abs_path'] = abs_path
            documents.append(document)
        return documents

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


