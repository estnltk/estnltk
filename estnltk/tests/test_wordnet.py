# -*- coding: utf-8 -*-

import unittest
import sys, os

'''
_MY_DIR = os.path.dirname(__file__)

sys.path.insert(1,os.path.join(_MY_DIR,'..'))
from wordnet import Wordnet

class AnnotationTest(unittest.TestCase):
  
  def test_annotation(self):
    wordnet = Wordnet()
    corpus = self.simple_document()

    annotated = wordnet(corpus,pos=True)

    self.assertDictEqual(corpus,self.annotated_document())
    
  def annotated_document(self):
    return {'doc':[{'analysis': [{'clitic': u'',
			    'ending': u's',
			    'form': u'sg in',
			    'lemma': u'ilu',
			    'lemma_tokens': [u'ilu'],
			    'partofspeech': u'S',
			    'root': u'ilu',
			    'wordnet':{'synsets':[{'id':24470,'pos':u'n'}]}},
			  {'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'ilus',
			    'lemma_tokens': [u'ilus'],
			    'partofspeech': u'A',
			    'root': u'ilus',
			    'wordnet':{'synsets':[{'id':23554,'pos':u'a'},
						  {'id':23555 ,'pos':u'a'},
						  {'id':24288 ,'pos':u'a'}]}}],
	    'text': u'Ilus'},
	    {'analysis': [{'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'koer',
			    'lemma_tokens': [u'koer'],
			    'partofspeech': u'A',
			    'root': u'k<oer',
			    'wordnet':{'synsets':[]}},
			  {'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'koer',
			    'lemma_tokens': [u'koer'],
			    'partofspeech': u'S',
			    'root': u'k<oer',
			    'wordnet':{'synsets':[{'id':267,'pos':u'n'},
						  {'id':63803, 'pos':u'n'}]}}],
	      'text': u'koer'},
	    {'analysis': [{'clitic': u'',
			    'ending': u's',
			    'form': u's',
			    'lemma': u'jaluta',
			    'lemma_tokens': [u'jaluta'],
			    'partofspeech': u'V',
			    'root': u'jaluta',
			    'wordnet':{'synsets':[]}}],
	      'text': u'jalutas'}]}

  def simple_document(self):
    return {'doc':[{'analysis': [{'clitic': u'',
			    'ending': u's',
			    'form': u'sg in',
			    'lemma': u'ilu',
			    'lemma_tokens': [u'ilu'],
			    'partofspeech': u'S',
			    'root': u'ilu'},
			  {'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'ilus',
			    'lemma_tokens': [u'ilus'],
			    'partofspeech': u'A',
			    'root': u'ilus'}],
	    'text': u'Ilus'},
	    {'analysis': [{'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'koer',
			    'lemma_tokens': [u'koer'],
			    'partofspeech': u'A',
			    'root': u'k<oer'},
			  {'clitic': u'',
			    'ending': u'0',
			    'form': u'sg n',
			    'lemma': u'koer',
			    'lemma_tokens': [u'koer'],
			    'partofspeech': u'S',
			    'root': u'k<oer'}],
	      'text': u'koer'},
	    {'analysis': [{'clitic': u'',
			    'ending': u's',
			    'form': u's',
			    'lemma': u'jaluta',
			    'lemma_tokens': [u'jaluta'],
			    'partofspeech': u'V',
			    'root': u'jaluta'}],
	      'text': u'jalutas'}]}
	    '''
if __name__ == '__main__':
    unittest.main()
