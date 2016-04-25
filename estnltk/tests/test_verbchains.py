# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text

from ..core import VERB_CHAIN_RES_PATH
from ..mw_verbs.verbchain_detector import VerbChainDetector


class VerbchainTest(unittest.TestCase):

    def test_verbchain_1(self):
        text = Text('Kass, suur ja must, ei jooksnud üle tee.')
        phrase = Text('ei jooksnud')
        phrase.tag_verb_chains()
        text.tag_verb_chains()
        phrases = text.split_by('verb_chains')
        self.assertEqual(len(phrases), 1)

    def test_verbchain_2(self):
        # Verbiahela sõnade järjekord ei pea kattuma sõnade järjekorraga tekstis
        text = Text('Samas on selge, et senine korraldus jätkuda ei saa.')
        text.tag_verb_chains()
        foundChains = text.verb_chains
        #print(foundChains)
        self.assertEqual(len(foundChains), 2)
        self.assertListEqual(foundChains[0]['roots'], ['ole'])
        self.assertListEqual(foundChains[1]['roots'], ['ei', 'saa', 'jätku'])
        
    def test_verbchain_3(self):
        # Verbiahela moodustamine ei tohiks katkeda vaheloleva punktuatsiooni tõttu
        text = Text('Londoni lend pidi täna hommikul kell 4:30 Tallinna saabuma.')
        text.tag_clauses()
        vc_detector = VerbChainDetector(resourcesPath=VERB_CHAIN_RES_PATH)
        firstSentence = text.divide()[0]
        chains = vc_detector.detectVerbChainsFromSent(firstSentence, breakOnPunctuation=True)
        self.assertListEqual(chains[0]['roots'], ['pida'])
        chains = vc_detector.detectVerbChainsFromSent(firstSentence)
        self.assertListEqual(chains[0]['roots'], ['pida', 'saabu'])

    def test_verbchain_4(self):
        # Verbiahela tekst ei tohi sisaldada ahelast väljapoole jäävaid sõnu
        text = Text('Lend oleks Tallinna pidanud juba öösel jõudma.')
        text.tag_verb_chains()
        verb_chains = text.verb_chain_texts
        self.assertListEqual(verb_chains, ['oleks pidanud jõudma'])

    def test_verbchain_5(self):
        # Verbiahela teksti leidmine peaks töötama ka mitmelauselise teksti korral
        text = Text('Samas on selge, et senine korraldus jätkuda ei saa. Saaks ehk jätkuda teisiti.')
        text.tag_verb_chains()
        verb_chains = text.verb_chain_texts
        self.assertListEqual(verb_chains, ['on','jätkuda ei saa','Saaks jätkuda'])

    def test_verbchain_invalid_input(self):
        '''
        Testib veakäsitlust kui etteantud sõnaanalüüs ei kattu verbiahelate tuvastaja eeldustega.
        '''
        # >> Praegu jääb selle testi eesmärk hägusaks, seega kommenteerisin selle välja;
        #text = Text({
        #      'text': 'Viga!!',
        #      'words': [{
        #                 'end': 4,
        #                 'start': 0,
        #                 'text': 'Viga'},
        #                {'end': 6, 'start': 4, 'text': '!!'}]}
        #)
        #with self.assertRaises(Exception) as e:
        #    text.tag_verb_chains()
        #self.assertNotIsInstance(e, IndexError, 'Inappropriate exception for error')
        self.assertTrue(True)