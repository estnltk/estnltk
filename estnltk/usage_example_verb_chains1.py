# -*- coding: utf-8 -*-
#
#     Verb chain detector - an usage example
#

from __future__ import unicode_literals, print_function
import json, os.path

from mw_verbs.verbchain_detector import VerbChainDetector

# Example sentence
inputSentenceJson = '''
[{"clauseID": 1, "text": "Mis", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "pl n", "root": "mis"}, {"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg n", "root": "mis"}]}, {"clauseID": 1, "text": "puutub", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "b", "form": "b", "root": "puutu"}]}, {"clauseID": 1, "text": "eelolevasse", "analysis": [{"partofspeech": "A", "clitic": "", "ending": "sse", "form": "sg ill", "root": "eel_olev"}]}, {"clauseID": 1, "text": "nädalasse", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "sse", "form": "sg ill", "root": "nädal"}]}, {"clauseID": 1, "text": ",", "analysis": [{"partofspeech": "Z", "clitic": "", "ending": "0", "form": "", "root": ","}]}, {"clauseID": 2, "text": "siis", "analysis": [{"partofspeech": "J", "clitic": "", "ending": "0", "form": "", "root": "siis"}]}, {"clauseID": 2, "text": "neljapäeval", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "l", "form": "sg ad", "root": "nelja_päev"}]}, {"clauseID": 2, "text": "ja", "analysis": [{"partofspeech": "J", "clitic": "", "ending": "0", "form": "", "root": "ja"}]}, {"clauseID": 2, "text": "reedel", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "l", "form": "sg ad", "root": "reede"}]}, {"clauseID": 2, "text": "ei", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "0", "form": "neg", "root": "ei"}]}, {"clauseID": 2, "text": "tohiks", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "ks", "form": "ks", "root": "tohti"}]}, {"clauseID": 2, "text": "Sa", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg n", "root": "sina"}]}, {"clauseID": 2, "text": "oma", "analysis": [{"partofspeech": "P", "clitic": "", "ending": "0", "form": "sg g", "root": "oma"}]}, {"clauseID": 2, "text": "tervist", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "t", "form": "sg p", "root": "tervis"}]}, {"clauseID": 2, "text": "proovile", "analysis": [{"partofspeech": "S", "clitic": "", "ending": "le", "form": "sg all", "root": "proov"}]}, {"clauseID": 2, "text": "panna", "analysis": [{"partofspeech": "V", "clitic": "", "ending": "a", "form": "da", "root": "pane"}]}, {"clauseID": 2, "text": ".", "analysis": [{"partofspeech": "Z", "clitic": "", "ending": "0", "form": "", "root": "."}]}]
'''
sentence = json.loads( inputSentenceJson )
sentenceText = [ token['text'] for token in sentence ]
print ( ' '.join(sentenceText) )

resourcesDir = os.path.join('mw_verbs', 'res')   # This should point to the directory  'mw_verbs\res'
detector  = VerbChainDetector( resourcesPath = resourcesDir )
allChains = detector.detectVerbChainsFromSent( sentence )
for verbChain in allChains:
    #  list of str : A general pattern describing words in the verb chain;
    #  For each word in chain, indicates whether it is 'ei','ega','pole','ära',
    #  'ole', '&' (conjunction: ja/ning/ega/või), 'verb' (verb different than 
    #  'ole') or 'nom/adv';
    print(' pattern:  ', verbChain['pattern'])
    
    #  list of int : IDs of the word tokens that belong to the chain
    #  (detectVerbChainsFromSent() assigns 'wordID' to each word token)
    print(' word_IDs: ', verbChain['phrase'])
    
    #  list of str : morphological analysis root values for each word in the chain
    print(' roots:  ', verbChain['roots'])
    
    #  list of str : partofspeech_form for each word in the chain
    print(' morph:  ', verbChain['morph'])
    
    #  str : grammatical polarity ('POS', 'NEG', '??') -- 'NEG' means that the chain
    #  begins with 'ei/ega/pole/ära';
    print(' polarity: ', verbChain['pol'])
    
    #  bool : Whether there are other verbs in the clause context?
    #  (if there are, it is uncertain whether the chain is complete or not)
    print(' is_context_ambiguous?: ', verbChain['otherVerbs'])
    
    print()


    
    

