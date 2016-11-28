# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..np_chunker import NounPhraseChunker
from ..names import *


class NP_ChunkerTest(unittest.TestCase):

    def test_np_chunker_1(self):
        chunker = NounPhraseChunker()
        text = Text('Üks kiisu, kaks suurt kutsut, villane lammas ja kena sinine lapitekk.')
        phrase_texts = chunker.analyze_text( text, return_type="strings" )
        self.assertListEqual(phrase_texts, \
            ['Üks kiisu', 'suurt kutsut', 'villane lammas', 'kena sinine lapitekk'])


    def test_np_chunker_2(self):
        chunker = NounPhraseChunker()
        text = Text('Autojuhi lapitekk pälvis linna koduleheküljel paljude kodanike tähelepanu.')
        phrase_texts = chunker.analyze_text( text, return_type="strings" )
        self.assertListEqual(phrase_texts, \
            ['Autojuhi lapitekk', 'linna koduleheküljel', 'paljude kodanike tähelepanu'])


    def test_np_chunker_3(self):
        chunker = NounPhraseChunker()
        text = Text('Saksamaal Bonnis leidis aset kummaline juhtum murdvargaga, kes kutsus endale ise politsei.')
        phrase_texts = chunker.analyze_text( text, return_type="strings" )
        #print( phrase_texts )
        self.assertListEqual(phrase_texts, \
            ['Saksamaal Bonnis', 'aset', 'kummaline juhtum', 'murdvargaga', 'kes', 'endale', 'ise', 'politsei'])


    def test_np_chunker_4(self):
        chunker = NounPhraseChunker()
        text = Text('Maril oli väike tall. Talle nimi oli Mall.')
        labels = chunker.analyze_text( text, return_type="labels" )
        self.assertListEqual(labels, \
             ['B', 'O', 'B', 'I', 'O', 'B', 'I', 'O', 'B', 'O'])


    def test_np_chunker_5(self):
        chunker = NounPhraseChunker()
        text = Text('Maril oli väike tall. Talle nimi oli Mall.')
        text = chunker.analyze_text( text, return_type="text" )
        self.assertTrue( NOUN_CHUNKS in text )
        phrase_texts = [ p[TEXT] for p in text[NOUN_CHUNKS] ]
        self.assertListEqual(phrase_texts, ['Maril', 'väike tall', 'Talle nimi', 'Mall'])
        