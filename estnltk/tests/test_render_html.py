# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.corpus import List
from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk import NerTagger
from pprint import pprint
from estnltk.names import *
from estnltk.render_html import render_html

import unittest


text1 = '''Inimestelt saadud vihjed pole veel politseil aidanud leida 43-aastast Kajar Paasi, kes tema naise sõnul Ardus maanteel rööviti.'''
text2 = '''Tuhanded Šotimaa kodud on lääneranniku piirkondi tabanud „ilmapommi“-tormi tõttu elektrita'''

tok = Tokenizer()
ana = PyVabamorfAnalyzer()
tag = NerTagger()


class RenderHtmlTest(unittest.TestCase):

    def test_ner_values(self):
        analyzed = List([tag(ana(tok(text1))), tag(ana(tok(text2)))])
        html = render_html(analyzed, NAMED_ENTITIES, LABEL, [('PER', 'color:red'), ('ORG', 'color:green'), ('LOC', 'color:blue')])
        self.assertTrue('Tuhanded <span style="color:blue">' in html)
        self.assertTrue('style="color:red">Kajar Paasi</span>' in html)
        self.assertFalse('<!DOCTYPE html>' in html)
        
    def test_postags(self):
        analyzed = List([tag(ana(tok(text1))), tag(ana(tok(text2)))])
        html = render_html(analyzed, WORDS, lambda x: x.postag, [('V', 'color:blue'), ('S', 'color:green'), ('.*', 'background-color:gray')], encapsulate_body=True)
        self.assertTrue('style="color:blue">rööviti.</span></div>' in html)
        self.assertTrue('style="background-color:gray">aidanud</span>' in html)
        self.assertTrue('style="color:green">tõttu</span>' in html)
        self.assertTrue('<!DOCTYPE html>' in html)
    
if __name__ == '__main__':
    unittest.main()
