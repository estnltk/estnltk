# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.names import *
from estnltk.textprocessor import TextProcessor
from estnltk.core import VERB_CHAIN_RES_PATH

from estnltk.mw_verbs.verbchain_detector import VerbChainDetector as Detector


class VerbChainDetector(TextProcessor):
    
    def process_json(self, corpus, **kwargs):
        for sentence_ptr in JsonPaths.words.find(corpus):
            sentence_ptr.value[VERB_CHAINS] = detector.detectVerbChainsFromSent(sentence_ptr.value[WORDS])
        return corpus

    def process_corpus(self, corpus, **kwargs):
        detector = get_detector()
        for sentence in corpus.sentences:
            sentence[VERB_CHAINS] = detector.detectVerbChainsFromSent(sentence[WORDS])
        return corpus

def get_detector():
    return Detector(resourcesPath = VERB_CHAIN_RES_PATH)
