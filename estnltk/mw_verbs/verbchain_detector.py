# -*- coding: utf-8 -*-
#
#    Tools for detecting verb chains from JSON format input sentences. Also aims
#    to detect initial (grammatical) polarity for the verb chains.
#    Requires that the input sentences are:
#      * split into tokens;
#      * morphologically analyzed;
#      * morphologically disambiguated (if not, the accuracy likely suffers);
#      * sentences are split into clauses; 
#        ('clauseID' must be marked to each token)
#

from __future__ import unicode_literals
import re

from .utils import WordTemplate
from .utils import addWordIDs
from .utils import getClausesByClauseIDs

from .basic_verbchain_detection import _extractBasicPredicateFromClause
from .basic_verbchain_detection import _expandSaamaWithTud
from .basic_verbchain_detection import _expandOlemaVerbChains
from .basic_verbchain_detection import _loadVerbSubcatRelations
from .basic_verbchain_detection import _expandVerbChainsBySubcat
from .basic_verbchain_detection import _determineVerbChainContextualAmbiguity
from .basic_verbchain_detection import _extractEgaNegFromSent
from .basic_verbchain_detection import _getJsonAsTextString

from .verbchain_nom_vinf_extender import VerbChainNomVInfExtender

# ================================================================
#    Various postprocessing functions
# ================================================================

def removeRedundantVerbChains( foundChains, removeOverlapping = True, removeSingleAraAndEi = False ):
    ''' Eemaldab yleliigsed verbiahelad: ahelad, mis katavad osaliselt v6i t2ielikult 
        teisi ahelaid (removeOverlapping == True), yhes6nalised 'ei' ja 'ära' ahelad (kui 
        removeSingleAraAndEi == True);
        
         Yldiselt on nii, et ylekattuvaid ei tohiks palju olla, kuna fraaside laiendamisel
        pyytakse alati kontrollida, et laiendus ei kattuks m6ne olemasoleva fraasiga;
        Peamiselt tekivad ylekattuvused siis, kui morf analyysi on sattunud valed 
        finiitverbi analyysid (v6i analyysid on j22nud mitmesteks) ja seega tuvastatakse 
        osalausest rohkem finiitverbe, kui oleks vaja.
         Heuristik: kahe ylekattuva puhul j2tame alles fraasi, mis algab eespool ning 
        m2rgime sellel 'otherVerbs' v22rtuseks True, mis m2rgib, et kontekstis on mingi
        segadus teiste verbidega.
    '''
    toDelete = []
    for i in range(len(foundChains)):
        matchObj1 = foundChains[i]
        if removeOverlapping:
            for j in range(i+1, len(foundChains)):
                matchObj2 = foundChains[j]
                if matchObj1 != matchObj2 and matchObj1['clauseID'] == matchObj2['clauseID']:
                    phrase1 = set(matchObj1['phrase'])
                    phrase2 = set(matchObj2['phrase'])
                    intersect = phrase1.intersection(phrase2)
                    if len(intersect) > 0:
                        #  Yldiselt on nii, et ylekattuvaid ei tohiks olla, kuna fraaside laiendamisel
                        # pyytakse alati kontrollida, et laiendus ei kattuks m6ne olemasoleva fraasiga;
                        #  Peamiselt tekivad ylekattuvused siis, kui morf analyysil on finiitverbi 
                        # analyysidesse j22nud sisse mitmesused (v6i on sattunud valed analyysid) ja 
                        # seega tuvastatakse osalausest rohkem finiitverbe, kui oleks vaja.
                        #  Heuristik: j2tame alles fraasi, mis algab eespool ning lisame selle otsa
                        # kysim2rgi (kuna pole kindel, et asjad on korras)
                        minWid1 = min(matchObj1['phrase'])
                        minWid2 = min(matchObj2['phrase'])
                        if minWid1 < minWid2:
                            matchObj1['otherVerbs'] = True
                            toDelete.append(j)
                        else:
                            matchObj2['otherVerbs'] = True
                            toDelete.append(i)
        if removeSingleAraAndEi:
            if ( len(matchObj1['pattern'])==1 and re.match('^(ei|ära)$', matchObj1['pattern'][0]) ):
                toDelete.append(i)
    if toDelete:
        if len(set(toDelete)) != len(toDelete):
            toDelete = list(set(toDelete))  # Eemaldame duplikaadid
        toDelete = [ foundChains[i] for i in toDelete ]
        for verbObj in toDelete:
            foundChains.remove(verbObj)


def addGrammaticalFeatsAndRoots( sentence, foundChains ):
    ''' Täiendab leitud verbiahelaid, lisades iga ahela kylge selle s6nade lemmad ('root' 
        v2ljad morf analyysist) ning morfoloogilised tunnused ('partofspeech'+'form': eraldajaks 
        '_' ning kui on mitu varianti, siis tuuakse k6ik variandid, eraldajaks '/');
        Iga verbiahela kylge pannakse atribuudid 'roots' ja 'morph', mis sisaldavad tunnuste
        loetelusid (iga ahela liikme jaoks yks tunnus);
         Nt.  
           ** 'püüab kodeerida' puhul tuleb 'morph' väärtuseks ['V_b', 'V_da'] ning
              'roots' väärtuseks ['püüd', 'kodeeri'];
           ** 'on tulnud' puhul tuleb 'morph' väärtuseks ['V_vad/b', 'V_nud'] ning
              'roots' väärtuseks ['ole', 'tule'];
    '''
    for i in range(len(foundChains)):
        matchObj1 = foundChains[i]
        roots = []
        grammFeats = []
        for j in range(len( matchObj1['phrase'] )):
            wid = matchObj1['phrase'][j]
            token = [token for token in sentence if token['wordID']==wid][0]
            analysisIDs = matchObj1['analysisIDs'][j]
            analyses = [ token['analysis'][k] for k in range(len( token['analysis'] )) if k in analysisIDs ]
            pos  = set( [a['partofspeech'] for a in analyses] )
            form = set( [a['form'] for a in analyses] )
            root = [a['root'] for a in analyses][0]
            grammatical = ("/".join(list(pos))) + '_' + ("/".join(list(form)))
            #  Yhtlustame m6ningaid mustreid (st kohendame nende morf analyysi selliseks, nagu
            # mustri poolt on eeldatud) ...
            if root == 'ei' and len(matchObj1['phrase'])>1:
                grammatical = 'V_neg'
            if matchObj1['pattern'][j] == '&':
                grammatical = 'J_'
            roots.append( root )
            grammFeats.append( grammatical )
        matchObj1['roots'] = roots
        matchObj1['morph'] = grammFeats

# ================================================================
#    VerbChainDetector -- The Main Class
# ================================================================

class VerbChainDetector:
    ''' Class for performing verb chain detection.
    '''
    
    verbInfSubcatLexicon   = None
    verbNomAdvVinfExtender = None
    #extender1 = VerbChainNomVInfExtender( resourcesPath = 'mw_verbs' )
    
    def __init__( self, **kwargs):
        ''' Initializes a verb chain detector. 
        
        Parameters
        ----------
        resourcesPath : str
            The path to the resource files (path to the 'mw_verbs' directory);
            (Default: current path)
        verbVinfSubcatFile : str
            Name of the file containing verb-infiniteVerb subcategorization relations.
            (Default: 'verb_vinf_subcat_relations.txt')
        useVerbNomVinfExtender : bool
            Whether verb chains are extended with 'nom/adv'+'Vinf' relations.
            (see verbchain_nom_vinf_extender.py for more details)
            (Default: True)
        '''
        from os import curdir
        import os.path
        verbVinfSubcatFile = 'verb_vinf_subcat_relations.txt'
        resourcesPath = curdir
        useVerbNomVinfExtender = True
        for argName, argVal in kwargs.items():
            if argName == 'verbVinfSubcatFile':
                verbVinfSubcatFile = argVal
            elif argName == 'resourcesPath':
                resourcesPath = argVal
            elif argName == 'useVerbNomVinfExtender':
                useVerbNomVinfExtender = bool(argVal)
            else:
                raise Exception(' Unsupported argument given: '+argName)
        self.verbInfSubcatLexicon = _loadVerbSubcatRelations( os.path.join( resourcesPath, verbVinfSubcatFile) )
        if useVerbNomVinfExtender:
            self.verbNomAdvVinfExtender = VerbChainNomVInfExtender( resourcesPath = resourcesPath )


    def detectVerbChainsFromSent( self, sentence, **kwargs):
        ''' Detect verb chains from given sentence.

        Parameters
        ----------
        sentence:  list of dict
            A list of sentence words, each word in form of a dictionary containing 
            morphological analysis and clause boundary annotations (must have 'clauseID');
        
        Keyword parameters
        ------------------
        expand2ndTime: boolean
            If True, regular verb chains (chains not ending with 'olema') are expanded twice.
            (default: False)
        removeSingleAraEi: boolean
            if True, verb chains consisting of a single word, 'ära' or 'ei', will be removed.
            (default: True)
        removeOverlapping: boolean
            If True, overlapping verb chains will be removed.
            (default: True)
        
        Returns
        -------
        list of dict
            List of detected verb chains, each verb chain has following attributes (keys):
             'phrase'      -- list of int : indexes pointing to elements in sentence that belong 
                                            to the chain;
             'pattern'     -- list of str : for each word in phrase, marks whether it is 'ega', 'ei', 
                                            'ära', 'pole', 'ole', '&' (conjunction: ja/ning/ega/või) 
                                            'verb' (verb different than 'ole') or 'nom/adv';
             'analysisIDs' -- list of (list of int) : for each word in phrase, points to index(es) of 
                                                      morphological analyses that correspond to words
                                                      in the verb chains;
             'roots'       -- list of str : for each word in phrase, lists its corresponding 'root' 
                                            value from the morphological analysis; e.g. for the verb
                                            chain 'püüab kodeerida', the 'root' will be ['püüd', 
                                            'kodeeri'];
             'morph'       -- list of str : for each word in phrase, lists its part-of-speech value 
                                            and morphological form (in one string, separated by '_',
                                            and multiple variants of the pos/form separated by '/'); 
                                            e.g. for the verb chain 'on tulnud', the 'morph' value 
                                            will be ['V_vad/b', 'V_nud'];
             'otherVerbs'  -- bool : whether there are other verbs in the context, potentially being 
                                     part of the verb chain; if this is True, it is uncertain whether 
                                     the chain is complete or not;
             'pol'         -- 'POS', 'NEG' or '??' : grammatical polarity of the verb chain; Negative
                                                     polarity indicates that the verb phrase begins 
                                                     with 'ei', 'ega', 'ära' or 'pole'; 
        '''
        # 0) Parse given arguments
        expand2ndTime = False
        removeOverlapping = True
        removeSingleAraEi = True
        for argName, argVal in kwargs.items():
            if argName == 'expand2ndTime':
                expand2ndTime = bool(argVal)
            elif argName == 'removeOverlapping':
                removeOverlapping = bool(argVal)
            elif argName == 'removeSingleAraEi':
                removeSingleAraEi = bool(argVal)
            else:
                raise Exception(' Unsupported argument given: '+argName)

        # 1) Preprocessing
        sentence = addWordIDs( sentence )
        clauses  = getClausesByClauseIDs( sentence )

        # 2) Extract predicate-centric verb chains within each clause
        allDetectedVerbChains = []
        for clauseID in clauses:
            clause   = clauses[clauseID]

            # 2.1) Extract predicate-centric verb chains within each clause
            detectedBasicChains = _extractBasicPredicateFromClause(clause, clauseID)
            allDetectedVerbChains.extend( detectedBasicChains )
            
            # 2.2) Extract 'saama' + 'tud' verb phrases (typically rare)
            _expandSaamaWithTud( clause, clauseID, allDetectedVerbChains )

            # 2.3) Extend 'olema' chains with 'nud/tud/mas/mata' verbs (if possible)
            _expandOlemaVerbChains( clause, clauseID, allDetectedVerbChains )
            
            # 2.4) Expand non-olema verb chains inside the clause where possible (verb+verb chains)
            _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False)

            # 2.5) Determine for which verb chains the context should be clear
            #    (no additional verbs can be added to the phrase)
            _determineVerbChainContextualAmbiguity( clause, clauseID, allDetectedVerbChains)
            
            # 2.6) Expand non-olema verb chains inside the clause 2nd time (verb+verb+verb chains)
            #      (Note that while verb+verb+verb+verb+...  chains are also possible, three verbs 
            #       seems to be a critical length: longer chains are rare and thus making longer 
            #       chains will likely lead to errors);
            if expand2ndTime:
                _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False)
            
        # 3) Extract 'ega' negations (considering the whole sentence context)
        expandableEgaFound = _extractEgaNegFromSent( sentence, clauses, allDetectedVerbChains )

        if expandableEgaFound:
            for clauseID in clauses:
                clause = clauses[clauseID]
                # 3.1) Expand non-olema 'ega' verb chains inside the clause, if possible;
                _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False)
            
            #_debugPrint(' | '+getJsonAsTextString(sentence, markTokens = [ verbObj['phrase'] for verbObj in allDetectedVerbChains ]))

        # 4) Extend chains with nom/adv + Vinf relations
        if self.verbNomAdvVinfExtender:
            addGrammaticalFeatsAndRoots( sentence, allDetectedVerbChains )
            for clauseID in clauses:
                clause = clauses[clauseID]
                expansionPerformed = \
                    self.verbNomAdvVinfExtender.extendChainsInClause( clause, clauseID, allDetectedVerbChains )
                if expansionPerformed:
                    _determineVerbChainContextualAmbiguity( clause, clauseID, allDetectedVerbChains)
        
        # ) Remove redundant and overlapping verb phrases
        removeRedundantVerbChains( allDetectedVerbChains, removeOverlapping = removeOverlapping, removeSingleAraAndEi = removeSingleAraEi )

        # ) Add grammatical features (in the end)
        addGrammaticalFeatsAndRoots( sentence, allDetectedVerbChains )

        return allDetectedVerbChains

