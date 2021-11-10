#
#    This is a part of the verb chain detector source from the version 1.4.1:
#       https://github.com/estnltk/estnltk/blob/a8f5520b1c4d26fd58223ffc3f0a565778b3d99f/estnltk/mw_verbs/verbchain_detector.py
#
#     *   *   *   *
#
#    Tools for detecting verb chains from JSON format input sentences. Also aims
#    to detect initial (grammatical) polarity for the verb chains.
#    Requires that the input sentences are:
#      * split into tokens;
#      * morphologically analyzed;
#      * morphologically disambiguated (if not, the accuracy likely suffers);
#      * sentences are split into clauses; 
#        (CLAUSE_IDX must be marked to each token)
#

import re

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import *

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import WordTemplate
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import addWordIDs
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import getClausesByClauseIDs

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _extractBasicPredicateFromClause
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _expandSaamaWithTud
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _expandOlemaVerbChains
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _loadVerbSubcatRelations
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _expandVerbChainsBySubcat
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _determineVerbChainContextualAmbiguity
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _extractEgaNegFromSent
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _getJsonAsTextString

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.verbchain_nom_vinf_extender import VerbChainNomVInfExtender

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
        m2rgime sellel OTHER_VERBS v22rtuseks True, mis m2rgib, et kontekstis on mingi
        segadus teiste verbidega.
    '''
    toDelete = []
    for i in range(len(foundChains)):
        matchObj1 = foundChains[i]
        if removeOverlapping:
            for j in range(i+1, len(foundChains)):
                matchObj2 = foundChains[j]
                if matchObj1 != matchObj2 and matchObj1[CLAUSE_IDX] == matchObj2[CLAUSE_IDX]:
                    phrase1 = set(matchObj1[PHRASE])
                    phrase2 = set(matchObj2[PHRASE])
                    intersect = phrase1.intersection(phrase2)
                    if len(intersect) > 0:
                        #  Yldiselt on nii, et ylekattuvaid ei tohiks olla, kuna fraaside laiendamisel
                        # pyytakse alati kontrollida, et laiendus ei kattuks m6ne olemasoleva fraasiga;
                        #  Peamiselt tekivad ylekattuvused siis, kui morf analyysil on finiitverbi 
                        # analyysidesse j22nud sisse mitmesused (v6i on sattunud valed analyysid) ja 
                        # seega tuvastatakse osalausest rohkem finiitverbe, kui oleks vaja.
                        #  Heuristik: j2tame alles fraasi, mis algab eespool ning lisame selle otsa
                        # kysim2rgi (kuna pole kindel, et asjad on korras)
                        minWid1 = min(matchObj1[PHRASE])
                        minWid2 = min(matchObj2[PHRASE])
                        if minWid1 < minWid2:
                            matchObj1[OTHER_VERBS] = True
                            toDelete.append(j)
                        else:
                            matchObj2[OTHER_VERBS] = True
                            toDelete.append(i)
        if removeSingleAraAndEi:
            if ( len(matchObj1[PATTERN])==1 and re.match('^(ei|ära)$', matchObj1[PATTERN][0]) ):
                toDelete.append(i)
    if toDelete:
        if len(set(toDelete)) != len(toDelete):
            toDelete = list(set(toDelete))  # Eemaldame duplikaadid
        toDelete = [ foundChains[i] for i in toDelete ]
        for verbObj in toDelete:
            foundChains.remove(verbObj)


def addGrammaticalFeatsAndRoots( sentence, foundChains ):
    ''' Täiendab leitud verbiahelaid, lisades iga ahela kylge selle s6nade lemmad (ROOT 
        v2ljad morf analyysist) ning morfoloogilised tunnused (POSTAG+FORM: eraldajaks 
        '_' ning kui on mitu varianti, siis tuuakse k6ik variandid, eraldajaks '/');
        Atribuudid ROOTS ja MORPH sisaldavad tunnuste loetelusid (iga ahela liikme jaoks 
        yks tunnus:
         Nt.  
           ** 'püüab kodeerida' puhul tuleb MORPH väärtuseks ['V_b', 'V_da'] ning
              ROOTS väärtuseks ['püüd', 'kodeeri'];
           ** 'on tulnud' puhul tuleb MORPH väärtuseks ['V_vad/b', 'V_nud'] ning
              ROOTS väärtuseks ['ole', 'tule'];

         Lisaks leiatakse ahela p6hiverbi (esimese verbi) grammatilised tunnused: 
           ** aeg (TENSE):       present, imperfect, perfect, pluperfect, past, ??
           ** k6neviis (MOOD):   indic, imper, condit, quotat, ??
           ** tegumood (VOICE):  personal, impersonal, ??
    '''
    _indicPresent     = ['n','d','b','me','te','vad']
    _indicImperfect   = ['sin', 'sid', 's', 'sime', 'site', 'sid']
    _imperatPlural    = ['gem', 'ge', 'gu']
    _conditPreesens   = ['ksin', 'ksid', 'ks', 'ksime', 'ksite', 'ksid']
    _conditPreteerium = ['nuksin', 'nuksid', 'nuks', 'nuksime', 'nuksite', 'nuksid']
    for i in range(len(foundChains)):
        matchObj1 = foundChains[i]
        roots = []
        grammFeats = []
        grammPosAndForms = []
        #
        # 1) Leiame kogu ahela morfoloogilised tunnused ja lemmad
        #
        for j in range(len( matchObj1[PHRASE] )):
            wid = matchObj1[PHRASE][j]
            token = [token for token in sentence if token[WORD_ID]==wid][0]
            analysisIDs = matchObj1[ANALYSIS_IDS][j]
            analyses = [ token[ANALYSIS][k] for k in range(len( token[ANALYSIS] )) if k in analysisIDs ]
            pos  = set( [a[POSTAG] for a in analyses] )
            form = set( [a[FORM] for a in analyses] )
            root = [a[ROOT] for a in analyses][0]
            grammatical = ("/".join(list(pos))) + '_' + ("/".join(list(form)))
            grammPosAndForms.append( (pos, form) )
            #  Yhtlustame m6ningaid mustreid (st kohendame nende morf analyysi selliseks, nagu
            # mustri poolt on eeldatud) ...
            if root == 'ei' and len(matchObj1[PHRASE])>1:
                grammatical = 'V_neg'
            if matchObj1[PATTERN][j] == '&':
                grammatical = 'J_'
            roots.append( root )
            grammFeats.append( grammatical )
        matchObj1[ROOTS] = roots
        matchObj1[MORPH] = grammFeats
        #
        # 2) Leiame eelneva põhjal ahela põhiverbi tunnused:  grammatilise aja (tense),  
        #      kõneviisi (mood),  tegumoe (voice)
        #
        tense = "??"
        mood  = "??"
        voice = "??"
        if matchObj1[POLARITY] == 'POS':
            #
            #   Jaatuse tunnused
            #
            (pos, form) = grammPosAndForms[0]
            if 'V' in pos:
                #
                #  Indikatiiv e kindel kõneviis
                #
                if len(form.intersection( _indicPresent )) > 0:
                    tense = "present"
                    mood  = "indic"
                    voice = "personal"
                elif len(form.intersection( _indicImperfect )) > 0:
                    tense = "imperfect"
                    mood = "indic"
                    voice = "personal"
                elif 'takse' in form:
                    tense = "present"
                    mood  = "indic"
                    voice = "impersonal"
                elif 'ti' in form:
                    tense = "imperfect"
                    mood  = "indic"
                    voice = "impersonal"
                #
                #  Imperatiiv e käskiv kõneviis
                #
                elif 'o' in form or 'gu' in form:
                    tense = "present"
                    mood  = "imper"
                    voice = "personal"
                elif len(form.intersection( _imperatPlural )) > 0:
                    tense = "present"
                    mood  = "imper"
                    voice = "personal"
                elif 'tagu' in form:
                    tense = "present"
                    mood  = "imper"
                    voice = "impersonal"
                #
                #  Konditsionaal e tingiv kõneviis
                #
                elif len(form.intersection( _conditPreesens )) > 0:
                    tense = "present"
                    mood  = "condit"
                    voice = "personal"
                elif 'taks' in form:
                    tense = "present"
                    mood  = "condit"
                    voice = "impersonal"
                elif len(form.intersection( _conditPreteerium )) > 0:
                    tense = "past"
                    mood  = "condit"
                    voice = "personal"
                elif 'tuks' in form:
                    tense = "past"
                    mood  = "condit"
                    voice = "impersonal"
                #
                #  Kvotatiiv e kaudne kõneviis
                #
                elif 'vat' in form:
                    tense = "present"
                    mood  = "quotat"
                    voice = "personal"
                elif 'tavat' in form:
                    tense = "present"
                    mood  = "quotat"
                    voice = "impersonal"
                elif 'nuvat' in form:
                    tense = "past"
                    mood  = "quotat"
                    voice = "personal"
                elif 'tuvat' in form:
                    tense = "past"
                    mood  = "quotat"
                    voice = "impersonal"
                #
                #  Liitaeg: olema + nud (personaal), olema + tud (impersonaal)
                #
                if len(matchObj1[PATTERN]) > 1 and matchObj1[PATTERN][0] == 'ole':
                    # Kindla kõneviisi liitaeg
                    if mood == "indic" and (grammFeats[1] == "V_nud" or grammFeats[1] == "V_tud"):
                        if tense == "present":
                            #  Täisminevik
                            tense = "perfect"
                            if grammFeats[1] == "V_tud":
                                voice = "impersonal"
                        elif tense == "imperfect":
                            #  Enneminevik
                            tense = "pluperfect"
                            if grammFeats[1] == "V_tud":
                                voice = "impersonal"
                    # Tingiva ja kaudse kõneviisi liitaeg (nn üldminevik)
                    elif mood in ["quotat", "condit"] and tense == "present" and \
                         voice == "personal":
                            if grammFeats[1] == "V_nud":
                                tense = "past"
                            elif grammFeats[1] == "V_tud":
                                if mood == "quotat":
                                    tense = "past"
                                    voice = "impersonal"
                                else:
                                    # tingiv + tud jääb esialgu lahtiseks
                                    tense = "??"
                                    voice = "??"
        elif matchObj1[POLARITY] == 'NEG':
            #
            #   Eituse tunnused
            #
            if len(matchObj1[PATTERN]) > 1 and \
               (matchObj1[PATTERN][0] == 'ei' or matchObj1[PATTERN][0] == 'ega'):
                (pos, form) = grammPosAndForms[1]
                # Indikatiiv
                if 'o' in form or 'neg o' in form:
                    tense = "present"
                    mood  = "indic"
                    voice = "personal"
                elif 'ta' in form:
                    tense = "present"
                    mood  = "indic"
                    voice = "impersonal"
                elif 'nud' in form:
                    tense = "imperfect"
                    mood  = "indic"
                    voice = "personal"
                elif 'tud' in form:
                    tense = "imperfect"
                    mood  = "indic"
                    voice = "impersonal"
                # Konditsionaal
                elif 'ks' in form:
                    tense = "present"
                    mood  = "condit"
                    voice = "personal"
                elif 'taks' in form:
                    tense = "present"
                    mood  = "condit"
                    voice = "impersonal"
                elif 'nuks' in form:
                    tense = "past"
                    mood  = "condit"
                    voice = "personal"
                elif 'tuks' in form:
                    tense = "past"
                    mood  = "condit"
                    voice = "impersonal"
                # Kvotatiiv
                elif 'vat' in form:
                    tense = "present"
                    mood  = "quotat"
                    voice = "personal"
                elif 'tavat' in form:
                    tense = "present"
                    mood  = "quotat"
                    voice = "impersonal"
                elif 'nuvat' in form:
                    tense = "past"
                    mood  = "quotat"
                    voice = "personal"
                elif 'tuvat' in form:
                    tense = "past"
                    mood  = "quotat"
                    voice = "impersonal"
                #
                #  Liitaeg: ei + olema + nud (personaal), ei + olema + tud (impersonaal)
                #
                if len(matchObj1[PATTERN]) > 2 and matchObj1[PATTERN][1] == 'ole':
                    # Kindla kõneviisi liitaeg
                    if mood == "indic" and (grammFeats[2] == "V_nud" or grammFeats[2] == "V_tud"):
                        if tense == "present":
                            #  Täisminevik
                            tense = "perfect"
                            if grammFeats[2] == "V_tud":
                                voice = "impersonal"
                        elif tense == "imperfect":
                            #  Enneminevik
                            tense = "pluperfect"
                            if grammFeats[2] == "V_tud":
                                voice = "impersonal"
                    # Tingiva ja kaudse kõneviisi liitaeg (nn üldminevik)
                    elif mood in ["quotat", "condit"] and tense == "present" and \
                         voice == "personal":
                            if grammFeats[2] == "V_nud":
                                tense = "past"
                            elif grammFeats[2] == "V_tud":
                                if mood == "quotat":
                                    tense = "past"
                                    voice = "impersonal"
                                else:
                                    # tingiv + tud jääb esialgu lahtiseks
                                    tense = "??"
                                    voice = "??"
            elif len(matchObj1[PATTERN]) > 1 and matchObj1[PATTERN][0] == 'ära':
                (pos, form) = grammPosAndForms[1]
                # Imperatiiv
                if 'tagu' in form:
                    tense = "present"
                    mood  = "imper"
                    voice = "impersonal"
                else:
                    tense = "present"
                    mood  = "imper"
                    voice = "personal"
            elif matchObj1[PATTERN][0] == 'pole':
                (pos, form) = grammPosAndForms[0]
                # Indikatiiv
                if 'neg o' in form:
                    tense = "present"
                    mood  = "indic"
                    voice = "personal"
                elif 'neg nud' in form:
                    tense = "imperfect"
                    mood  = "indic"
                    voice = "personal"
                elif 'neg tud' in form:
                    tense = "imperfect"
                    mood  = "indic"
                    voice = "impersonal"
                # Konditsionaal
                elif 'neg ks' in form:
                    tense = "present"
                    mood  = "condit"
                    voice = "personal"
                elif 'neg nuks' in form:
                    tense = "past"
                    mood  = "condit"
                    voice = "personal"
                # Kvotatiiv
                elif 'neg vat' in form:
                    tense = "present"
                    mood  = "quotat"
                    voice = "personal"
                #
                #  Liitaeg: pole + nud (personaal), pole + tud (impersonaal)
                #
                if len(matchObj1[PATTERN]) > 1:
                    # Kindla kõneviisi liitaeg
                    if mood == "indic" and (grammFeats[1] == "V_nud" or grammFeats[1] == "V_tud"):
                        if tense == "present":
                            #  Täisminevik
                            tense = "perfect"
                            if grammFeats[1] == "V_tud":
                                voice = "impersonal"
                        elif tense == "imperfect":
                            #  Enneminevik
                            tense = "pluperfect"
                            if grammFeats[1] == "V_tud":
                                voice = "impersonal"
                    # Tingiva ja kaudse kõneviisi liitaeg (nn üldminevik)
                    elif mood in ["quotat", "condit"] and tense == "present" and \
                         voice == "personal":
                            if grammFeats[1] == "V_nud":
                                tense = "past"
                            elif grammFeats[1] == "V_tud":
                                if mood == "quotat":
                                    tense = "past"
                                    voice = "impersonal"
                                else:
                                    # tingiv + tud jääb esialgu lahtiseks
                                    tense = "??"
                                    voice = "??"
        matchObj1[MOOD] = mood
        matchObj1[TENSE] = tense
        matchObj1[VOICE] = voice


# ================================================================
#    VerbChainDetector -- The Main Class
# ================================================================

class VerbChainDetectorV1_4:
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
            morphological analysis and clause boundary annotations (must have CLAUSE_IDX);
        
        Keyword parameters
        ------------------
        expand2ndTime: boolean
            If True, regular verb chains (chains not ending with 'olema') are expanded twice.
            (default: False)
        breakOnPunctuation: boolean
            If True, expansion of regular verb chains will be broken in case of intervening punctuation.
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
             PHRASE      -- list of int : indexes pointing to elements in sentence that belong 
                                            to the chain;
             PATTERN     -- list of str : for each word in phrase, marks whether it is 'ega', 'ei', 
                                            'ära', 'pole', 'ole', '&' (conjunction: ja/ning/ega/või) 
                                            'verb' (verb different than 'ole') or 'nom/adv';
             ANALYSIS_IDS -- list of (list of int) : for each word in phrase, points to index(es) of 
                                                      morphological analyses that correspond to words
                                                      in the verb chains;
             ROOTS       -- list of str : for each word in phrase, lists its corresponding ROOT 
                                            value from the morphological analysis; e.g. for the verb
                                            chain 'püüab kodeerida', the ROOT will be ['püüd', 
                                            'kodeeri'];
             MORPH       -- list of str : for each word in phrase, lists its part-of-speech value 
                                            and morphological form (in one string, separated by '_',
                                            and multiple variants of the pos/form separated by '/'); 
                                            e.g. for the verb chain 'on tulnud', the MORPH value 
                                            will be ['V_vad/b', 'V_nud'];
             OTHER_VERBS  -- bool : whether there are other verbs in the context, potentially being 
                                     part of the verb chain; if this is True, it is uncertain whether 
                                     the chain is complete or not;
             
             POLARITY     -- 'POS', 'NEG' or '??' : grammatical polarity of the verb chain; Negative
                                                    polarity indicates that the verb phrase begins 
                                                    with 'ei', 'ega', 'ära' or 'pole'; 
             TENSE        -- tense of the main verb:  'present', 'imperfect', 'perfect', 
                                                              'pluperfect', 'past', '??';
             MOOD         -- mood of the main verb:   'indic', 'imper', 'condit', 'quotat', '??';
             VOICE        -- voice of the main verb:  'personal', 'impersonal', '??';

        '''
        # 0) Parse given arguments
        expand2ndTime = False
        removeOverlapping  = True
        removeSingleAraEi  = True
        breakOnPunctuation = False
        for argName, argVal in kwargs.items():
            if argName == 'expand2ndTime':
                expand2ndTime = bool(argVal)
            elif argName == 'removeOverlapping':
                removeOverlapping = bool(argVal)
            elif argName == 'removeSingleAraEi':
                removeSingleAraEi = bool(argVal)
            elif argName == 'breakOnPunctuation':
                breakOnPunctuation = bool(argVal)
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
            _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False, breakOnPunctuation)

            # 2.5) Determine for which verb chains the context should be clear
            #    (no additional verbs can be added to the phrase)
            _determineVerbChainContextualAmbiguity( clause, clauseID, allDetectedVerbChains)
            
            # 2.6) Expand non-olema verb chains inside the clause 2nd time (verb+verb+verb chains)
            #      (Note that while verb+verb+verb+verb+...  chains are also possible, three verbs 
            #       seems to be a critical length: longer chains are rare and thus making longer 
            #       chains will likely lead to errors);
            if expand2ndTime:
                _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False, breakOnPunctuation)
            
        # 3) Extract 'ega' negations (considering the whole sentence context)
        expandableEgaFound = _extractEgaNegFromSent( sentence, clauses, allDetectedVerbChains )

        if expandableEgaFound:
            for clauseID in clauses:
                clause = clauses[clauseID]
                # 3.1) Expand non-olema 'ega' verb chains inside the clause, if possible;
                _expandVerbChainsBySubcat( clause, clauseID, allDetectedVerbChains, self.verbInfSubcatLexicon, False, breakOnPunctuation)
            
            #_debugPrint(' | '+getJsonAsTextString(sentence, markTokens = [ verbObj[PHRASE] for verbObj in allDetectedVerbChains ]))

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

