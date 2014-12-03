# -*- coding: utf-8 -*-
#
#     Verb chain detector - an usage example
#

from __future__ import unicode_literals, print_function

from estnltk.names import *
from estnltk.core import VERB_CHAIN_RES_PATH
from estnltk.mw_verbs.verbchain_detector import VerbChainDetector

import json, os.path

# Example sentence
inputSentenceJson = '''
[{"clause_index": 1, "text": "Mis", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "pl n", "root": "mis"}, {"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg n", "root": "mis"}]}, {"clause_index": 1, "text": "puutub", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "b", "form": "b", "root": "puutu"}]}, {"clause_index": 1, "text": "eelolevasse", "analysis": [{"partofspeech": "A", "clitic": "", "ending": "sse", "form": "sg ill", "root": "eel_olev"}]}, {"clause_index": 1, "text": "nädalasse", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "sse", "form": "sg ill", "root": "nädal"}]}, {"clause_index": 1, "text": ",", "analysis": [{"partofspeech": "Z", "clitic": "", "ending": "0", "form": "", "root": ","}]}, {"clause_index": 2, "text": "siis", "analysis": [{"partofspeech": "J", "clitic": "", "ending": "0", "form": "", "root": "siis"}]}, {"clause_index": 2, "text": "neljapäeval", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "l", "form": "sg ad", "root": "nelja_päev"}]}, {"clause_index": 2, "text": "ja", "analysis": [{"partofspeech": "J", "clitic": "", "ending": "0", "form": "", "root": "ja"}]}, {"clause_index": 2, "text": "reedel", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "l", "form": "sg ad", "root": "reede"}]}, {"clause_index": 2, "text": "ei", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "0", "form": "neg", "root": "ei"}]}, {"clause_index": 2, "text": "tohiks", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "ks", "form": "ks", "root": "tohti"}]}, {"clause_index": 2, "text": "Sa", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg n", "root": "sina"}]}, {"clause_index": 2, "text": "oma", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg g", "root": "oma"}]}, {"clause_index": 2, "text": "tervist", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "t", "form": "sg p", "root": "tervis"}]}, {"clause_index": 2, "text": "proovile", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "le", "form": "sg all", "root": "proov"}]}, {"clause_index": 2, "text": "panna", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "a", "form": "da", "root": "pane"}]}, {"clause_index": 2, "text": ".", "analysis": [{"partofspeech": "Z", "clitic": "", "ending": "0", "form": "", "root": "."}]}]
'''
sentence = json.loads( inputSentenceJson )
sentenceText = [ token['text'] for token in sentence ]
print ( ' '.join(sentenceText) )

detector  = VerbChainDetector( resourcesPath = VERB_CHAIN_RES_PATH)
allChains = detector.detectVerbChainsFromSent( sentence )
for verbChain in allChains:
    #  list of str : A general pattern describing words in the verb chain;
    #  For each word in chain, indicates whether it is 'ei','ega','pole','ära',
    #  'ole', '&' (conjunction: ja/ning/ega/või), 'verb' (verb different than 
    #  'ole') or 'nom/adv';
    print(' pattern:  ', verbChain[PATTERN])
    
    #  list of int : IDs of the word tokens that belong to the chain
    #  (detectVerbChainsFromSent() assigns 'wordID' to each word token)
    print(' word_IDs: ', verbChain[PHRASE])
    
    #  list of str : morphological analysis root values for each word in the chain
    print(' roots:  ', verbChain[ROOTS])
    
    #  list of str : partofspeech_form for each word in the chain
    print(' morph:  ', verbChain[MORPH])
    
    #  str : grammatical polarity ('POS', 'NEG', '??') -- 'NEG' means that the chain
    #  begins with 'ei/ega/pole/ära';
    print(' polarity: ', verbChain[POLARITY])
    
    #  bool : Whether there are other verbs in the clause context?
    #  (if there are, it is uncertain whether the chain is complete or not)
    print(' is_context_ambiguous?: ', verbChain[OTHER_VERBS])
    
    print()


    
    

