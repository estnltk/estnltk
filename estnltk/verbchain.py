# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk import Corpus
from estnltk.names import *
from estnltk.textprocessor import TextProcessor
from estnltk.core import VERB_CHAIN_RES_PATH, JsonPaths

from estnltk.mw_verbs.verbchain_detector import VerbChainDetector as Detector
from pprint import pprint


class VerbChainDetector(TextProcessor):
    
    def process_json(self, corpus, **kwargs):
        # inefficient for JSON:
        return self.process_corpus(Corpus.construct(corpus)).to_json()

    def process_corpus(self, corpus, **kwargs):
        detector = get_detector()
        for sentence in corpus.sentences:
            sentence[VERB_CHAINS] = detector.detectVerbChainsFromSent(sentence[WORDS])
        return corpus

def get_detector():
    return Detector(resourcesPath = VERB_CHAIN_RES_PATH)
