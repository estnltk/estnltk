#
#    This is a part of the verb chain detector source from the version 1.4.1:
#       https://github.com/estnltk/estnltk/blob/a8f5520b1c4d26fd58223ffc3f0a565778b3d99f/estnltk/mw_verbs/verbchain_nom_vinf_extender.py
#
#     *   *   *   *
#
#     Methods for extending verb chains with 'nom/adv' + 'verb_inf' subcategorization relations.
#     Attempt is made to detect cases where the last verb of the chain subcategorizes for a
#     nominal/adverb which, in turn, subcategorizes for a infinite verb, e.g.
#            andma + aega + Vda       :  andsime_0 talle aega_0 järele mõelda_0 
#            leidma + võimalust + Vda :  Nad ei_0 leidnud_0 võimalust_0 tööd lõpetada_0
#            puuduma + mõte + Vda     :  puudub_0 ju mõte_0 osta_0 kallis auto 
#            olema + vaja + Vda       :  pole_0 siin vaja_0 sellel teemal pläkutada_0
#
#     Detailed comments of the methods are in Estonian.
#

import re

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import *

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import WordTemplate
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import getClausesByClauseIDs
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _getJsonAsTextString
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _getMatchingAnalysisIDs
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.basic_verbchain_detection import _isFollowedByComma
#from .debug_print import _debugPrint

class VerbChainNomVInfExtender:
    ''' Class for extending verb chains with nom/adv-vinf relations.
    '''
    nomAdvWordTemplates = None
    verbRules = None
    verbToVinf = None
    
    wtNom = WordTemplate({POSTAG:'[SACP]'})
    wtNomSemCase = WordTemplate({FORM:r'^((sg|pl)\s(ab|abl|ad|all|el|es|ill|in|kom|ter|tr)|adt)$'})
    wtNotSyntAttrib = \
        WordTemplate({ROOT:'^(ka|samuti|aga|et|nüüd|praegu|varsti|siis(ki)?|ju|just|siin|kohe|veel|'+\
                               'seni|küll|hiljem|varem|ikka(gi)?|jälle(gi)?|vist|juba|isegi|seal|sageli|'+\
                               'mõnikord|muidu|(tavalise|loomuliku|lihtsa|ilmse)lt|taas|harva|eile|ammu|'+\
                               'ainult|kindlasti|kindlalt)$', POSTAG:'[DJ]'})


    def __init__( self, **kwargs):
        ''' Initializes the verb chain extender.
        
        Parameters
        ----------
        resourcesPath : str
            The path to the resource files (path to the 'mw_verbs' directory);
            (Default: current path)
        subcatLexiconFile : str
            Name of the file containing required subcategorization relations.
            (Default: 'verb_nom_vinf_subcat_relations.txt')
        '''
        from os import curdir
        import os.path
        subcatLexiconFile = 'verb_nom_vinf_subcat_relations.txt'
        resourcesPath = curdir
        for argName, argVal in kwargs.items():
            if argName == 'subcatLexiconFile':
                subcatLexiconFile = argVal
            elif argName == 'resourcesPath':
                resourcesPath = argVal
            else:
                raise Exception(' Unsupported argument given: '+argName)
        self._loadSubcatRelations( os.path.join( resourcesPath, subcatLexiconFile) )

    def _loadSubcatRelations( self, inputFile ):
        ''' Laeb sisendfailist (inputFile) verb-nom/adv-vinf rektsiooniseoste mustrid.
            Iga muster peab olema failis eraldi real, kujul:
                (verbikirjeldus)\\TAB(nom/adv-kirjeldus)\\TAB(vinfkirjeldus)
            nt
                leid NEG	aeg;S;((sg|pl) (p)|adt)	da
                leid POS	võimalus;S;(sg|pl) (n|p|g)	da
            Salvestab laetud tulemused klassimuutujatesse nomAdvWordTemplates, verbRules
            ja verbToVinf;
        '''
        self.nomAdvWordTemplates = dict()
        self.verbRules  = dict()
        self.verbToVinf = dict()
        with open(inputFile, mode='r', encoding='utf-8') as in_f:
            for line in in_f:
                line = line.rstrip()
                if len(line) > 0 and not re.match("^#.+$", line):
                    items = line.split('\t')
                    if len(items) == 3:
                        verb    = items[0]
                        nounAdv = items[1]
                        vinf    = items[2]
                        if nounAdv not in self.nomAdvWordTemplates:
                            (root,pos,form) = nounAdv.split(';')
                            if not root.startswith('^') and not root.endswith('$'):
                                root = '^'+root+'$'
                            constraints = {ROOT:root, POSTAG:pos}
                            if form:
                                constraints[FORM] = form
                            self.nomAdvWordTemplates[nounAdv] = WordTemplate(constraints)
                        if verb not in self.verbRules:
                            self.verbRules[verb] = []
                        if verb not in self.verbToVinf:
                            self.verbToVinf[verb] = []
                        self.verbRules[verb].append( (nounAdv, 'V_'+vinf) )
                        if 'V_'+vinf not in self.verbToVinf[verb]:
                            self.verbToVinf[verb].append( 'V_'+vinf )
                    else:
                        raise Exception(' Unexpected number of items in the input lexicon line: '+line)


    def tokenMatchesNomAdvVinf( self, token, verb, vinf): 
        ''' Teeb kindlaks, kas etteantud token v6iks olla verb'i alluv ning vinf'i ylemus (st
            paikneda nende vahel). Kui see nii on, tagastab j2rjendi vahele sobiva s6na morf 
            analyysidega (meetodi _getMatchingAnalysisIDs abil), vastasel juhul tagastab tyhja 
            j2rjendi;
        '''
        if verb in self.verbRules:
            for (nounAdv, vinf1) in self.verbRules[verb]:
                if vinf == vinf1 and (self.nomAdvWordTemplates[nounAdv]).matches(token):
                    return _getMatchingAnalysisIDs( token, self.nomAdvWordTemplates[nounAdv] )
        return []


    def extendChainsInSentence( self, sentence, foundChains ):
        ''' Rakendab meetodit self.extendChainsInClause() antud lause igal osalausel.
        '''
        # 1) Preprocessing
        clauses = getClausesByClauseIDs( sentence )

        # 2) Extend verb chains in each clause
        allDetectedVerbChains = []
        for clauseID in clauses:
            clause = clauses[clauseID]
            self.extendChainsInClause(clause, clauseID, foundChains)


    def _isLikelyNotPhrase( self, headVerbRoot, headVerbWID, nomAdvWID, widToToken):
        ''' Kontrollib, et nom/adv ei kuuluks mingi suurema fraasi kooseisu (poleks fraasi peas6na).
            Tagastab True, kui:
               *) nom/adv j2rgneb vahetult peaverbile
               *) või nom/adv on vahetult osalause alguses
               *) või nom-ile eelneb vahetult selline s6na, mis kindlasti ei saa olla
                  eestäiendiks
               *) või nom/adv puhul on tegemist olema-verbi adv-ga;
        '''
        minWID = min(widToToken.keys())
        nomAdvToken = widToToken[nomAdvWID]
        isNom = self.wtNom.matches(nomAdvToken)
        if headVerbWID+1 == nomAdvWID:
            #   1) Kui nom/adv j2rgneb vahetult verbile, siis on ysna turvaline arvata,
            #      et need kuuluvad kokku, nt:
            #             ja seda tunnet on_0 raske_0 millegi vastu vahetada_0 .
            #             mida nad peavad_0 vajalikuks_0 läände müüa_0
            return True
        elif minWID == nomAdvWID:
            #   2) Kui nom/adv on vahetult osalause alguses, siis on samuti üsna turvaline
            #      eeldada, et see kuulub verbiga kokku, nt:
            #             Tarvis_0 on_0 muretseda_0 veel auhinnafond 250 000 dollarit .
            #             Raske_0 on_0 temaga vaielda_0 .
            return True
        elif isNom and nomAdvWID-1 in widToToken:
            prevToken = widToToken[nomAdvWID-1]
            if self.wtNotSyntAttrib.matches(prevToken):
                #
                #   3.1) Kui nom-ile eelneb vahetult adverb, mis tavaliselt allub otse 
                #        verbile ning ei funktsioneeri eest2iendina (nt 'ju', 'ikka',
                #        'vist', 'veel' jms), siis on ysna turvaline eeldada, et nom
                #        ei ole mingi fraasi osa:
                #             Kaudseid näitajaid on_0 aga võimalik_0 analüüsida_0
                #             Pole_0 ju mõtet_0 hakata_0 teile ette laduma asjaolusid
                #             on_0 veel raske_0 kommenteerida_0
                #
                return True
            elif self.wtNom.matches(prevToken):
                if self.wtNomSemCase.matches(prevToken):
                    if not self.wtNomSemCase.matches(nomAdvToken):
                        #
                        #   3.2) Kui nom-ile vahetult eelnev s6na on semantilises k22ndes, aga nom
                        #        mitte, pole nad suure t6en2osusega seotud, nt:
                        #             Siis jääb_0 ootajal võimalus_0 öelda_0 
                        #             vahendajate juurdehindlust on_0 riigil võimalik_0 kontrollida_0 .
                        #             Ka üürnikul on_0 selle seadusega õigus_0 maksta_0 vähem üüri
                        #
                        return True
                    else:
                        #
                        #   3.3) Kui nii nom kui vahetult eelnev s6na on m6lemad semantilises k22ndes, 
                        #        aga k22nded on erinevad, ei moodusta nad t6en2oliselt yhte fraasi, nt:
                        #            pole_0 ettevõttel plaanis_0 Tartus kaugküttesooja hinda tõsta_0 .
                        #            Ginrichi teatel on_0 vabariiklastel kavas_0 luua_0 erikomisjon ,
                        #            et ühegi parkimismaja rajamist pole_0 linnal kavas_0 toetada_0 .
                        #
                        analyses1 = self.wtNomSemCase.matchingAnalyses(prevToken)
                        analyses2 = self.wtNomSemCase.matchingAnalyses(nomAdvToken)
                        forms1 = set([a[FORM] for a in analyses1])
                        forms2 = set([a[FORM] for a in analyses2])
                        if len(forms1.intersection(forms2))==0:
                            return True
        elif not isNom and headVerbRoot.startswith('ole '):
            #
            #   X) Kui tegemist on olema-ga liituva adv-ga, eeldame, et see on suurema t6en2osusega yksik, 
            #      st pole mingi fraasi koosseisus:
            #            Theresel polnud_0 raskeid seasöögiämbreid tarvis_0 ubida_0 .
            #            Seepärast pole_0 meil ka häbi vaja_0 tunda_0
            #
            #      NB! Alati see siiski nii ei ole, st võib liituda tähendust intensiivistav 'väga',
            #      'pisut', 'palju' jms adverb, nt:
            #            Meil pole_0 siin palju vaja_0 pingutada_0
            #
            return True
        return False


    def _canBeExpanded( self, headVerbRoot, headVerbWID, suitableNomAdvExpansions, expansionVerbs, widToToken ):
        ''' Teeb kindlaks, kas kontekst on verbiahela laiendamiseks piisavalt selge/yhene:
              1) Nii 'nom/adv' kandidaate kui ka Vinf kandidaate on täpselt üks;
              2) Nom/adv ei kuulu mingi suurema fraasi kooseisu (meetodi _isLikelyNotPhrase() abil);
            Kui tingimused täidetud, tagastab lisatava verbi listist expansionVerbs, vastasel juhul
            tagastab None;
        '''
        if len(suitableNomAdvExpansions)==1 and expansionVerbs:
            # Kontrollime, kas leidub t2pselt yks laiendiks sobiv verb (kui leidub
            # rohkem, on kontekst kahtlane ja raske otsustada, kas tasub laiendada 
            # v6i mitte)
            suitableExpansionVerbs = \
                [expVerb for expVerb in expansionVerbs if expVerb[2] == suitableNomAdvExpansions[0][2]]
            if len( suitableExpansionVerbs ) == 1:
                # Kontrollime, et nom/adv ei kuuluks mingi suurema fraasi kooseisu (ei oleks fraasi
                # peas6na);
                nomAdvWID = suitableNomAdvExpansions[0][0]
                if self._isLikelyNotPhrase( headVerbRoot, headVerbWID, nomAdvWID, widToToken ):
                    return suitableExpansionVerbs[0]
        return None


    def extendChainsInClause( self, clause, clauseID, foundChains ):
        '''  Proovime etteantud osalauses leiduvaid verbiahelaid täiendada 'verb-nom/adv-vinf' 
            rektsiooniseostega, nt:
                andma + võimalus + Vda :  talle anti_0 võimalus_0 olukorda parandada_0
                olema + vaja + Vda    :   nüüd on_0 küll vaja_0 asi lõpetada_0
             Teeme seda kahel moel:
            1) kui mingi olemasoleva verbiahela keskelt on puudu 'nom/adv' (nt 'andma', 'jätma'
               verbide vinf rektsiooniseoste leidmisel võib tekkida selliseid lünki), siis
               lisame ahela keskele 'nom/adv' sõna.
            2) kui verbiahela lõpus on verb, mis on sageli ülemuseks 'nom/adv' sõnale, millest
               omakorda sõltub mingi Vinf verb (Vma, Vda), ning need on osalausekontekstis olemas,
               lisame need verbiahela lõppu;
        '''
        expansionPerformed = False
        # J22dvustame s6nad, mis kuuluvad juba mingi tuvastatud verbifraasi koosseisu
        annotatedWords = []
        for verbObj in foundChains:
            if clauseID == verbObj[CLAUSE_IDX] and (len(verbObj[PATTERN])==1 and \
               re.match('^(ei|ära|ega)$', verbObj[PATTERN][0])):
                # V2lja j22vad yksikuna esinevad ei/ära/ega, kuna need tõenäoliselt ei sega
                continue
            annotatedWords.extend( verbObj[PHRASE] )
        widToToken = { token[WORD_ID] : token for token in clause }
        verbDaMa   = WordTemplate({POSTAG:'V', FORM:'^(da|ma)$'})
        verbOle    = WordTemplate({ROOT:'^ole$',POSTAG:'V'})
        #
        #   1) Yritame leida, millised juba tuvastatud verbiahelatest on sellised, kust on
        #      vahelt puudu nom/adv s6na, nt:
        #            annab_0 kunstnik jälle põhjuse endast kirjutada_0
        #            see annab_0 võimaluse laua tagant tõusta_0 ja_0 minema jalutada_0
        #      Kui leiame ahelast puuduoleva s6na ja lisame selle ahelasse ...
        #
        for verbObj in foundChains:
            if clauseID == verbObj[CLAUSE_IDX]:
                headVerb      = ''
                headVerbWID   = -1
                dependentVerb = ''
                dependentVerbWIDs = []
                firstDependentVerbID = -1
                #  Leiame ahela l6pust ylemus-verbi ja sellele alluva verbi
                if len(verbObj[PATTERN]) > 3 and verbObj[PATTERN][-2] == '&':
                    headVerb = verbObj[ROOTS][-4]+" "+verbObj[POLARITY]
                    dependentVerb = verbObj[MORPH][-3]
                    headVerbWID = verbObj[PHRASE][-4]
                    dependentVerbWIDs.append( verbObj[PHRASE][-3] )
                    dependentVerbWIDs.append( verbObj[PHRASE][-1] )
                    firstDependentVerbID = len(verbObj[PHRASE])-3
                elif len(verbObj[PATTERN]) > 1 and verbObj[PATTERN][-2]=='verb':
                    headVerb = verbObj[ROOTS][-2]+" "+verbObj[POLARITY]
                    dependentVerb = verbObj[MORPH][-1]
                    headVerbWID = verbObj[PHRASE][-2]
                    dependentVerbWIDs.append(verbObj[PHRASE][-1])
                    firstDependentVerbID = len(verbObj[PHRASE])-1
                # Kontrollime, kas ylemusverb ja sellele alluv verb v6iksid olla yhendatud
                # mingi nom/adv s6na kaudu
                if headVerb in self.verbRules and headVerb in self.verbToVinf and \
                   dependentVerb in self.verbToVinf[headVerb]:
                    # Teeme kindlaks, kas s6nade vahele j22b puuduolev nom/adv
                    minInd = min(min(dependentVerbWIDs), headVerbWID-1)
                    maxInd = max(max(dependentVerbWIDs)-1, headVerbWID)
                    if minInd < maxInd:
                        for i in range(minInd, maxInd+1):
                            if i in widToToken and i not in annotatedWords:
                                token = widToToken[i]
                                matchingAnalyses = self.tokenMatchesNomAdvVinf( token, headVerb, dependentVerb )
                                if matchingAnalyses and not expansionPerformed:
                                    #   Kontrollime, kas vaheletorgatav sõna paikneb nii, et see on suure
                                    #  tõenäosusega üksiksõna, mitte fraas.
                                    if self._isLikelyNotPhrase( headVerb, headVerbWID, token[WORD_ID], widToToken ):
                                        # Torkame nimis6na/adverbi vahele
                                        verbObj[PHRASE].insert( firstDependentVerbID, token[WORD_ID] )
                                        verbObj[PATTERN].insert( firstDependentVerbID, 'nom/adv' )
                                        verbObj[ANALYSIS_IDS].insert( firstDependentVerbID, matchingAnalyses )
                                        annotatedWords.append( token[WORD_ID] )
                                        expansionPerformed = True
                                    else:
                                        # Kui me ei saa olla kindlad, et vaheletorgatav sõna pole fraas, paneme
                                        # küsimärgi, näitamaks, et verbiahelast on suure tõenäosusega midagi
                                        # puudu ...
                                        verbObj[OTHER_VERBS] = True
                                        #_debugPrint( ' '+('+'.join(verbObj[PATTERN]))+' | '+_getJsonAsTextString(clause, markTokens = [ verbObj[PHRASE] ] ))

        #
        #   2) Yritame luua uusi ahelaid, laiendades verbe olemasolevate ahelate l6pus:
        #
        #          millega antakse_0 võimalus_1 sõlmida_1 uus kokkulepe .
        #          puudub_0 võimalus_1 spetsialiste täistööajaga rakendada_1 .
        #          kui on_0 võimalus_1 rahulikult vooluga kaasa minna_1
        #
        clauseMaxWID = max( list(widToToken.keys()) )
        for verbObj in foundChains:
            if clauseID == verbObj[CLAUSE_IDX] and verbObj[OTHER_VERBS]:
                if (len(verbObj[PATTERN])==1 or (len(verbObj[PATTERN])>1 and \
                   verbObj[PATTERN][-2] != '&')):
                    headVerb = verbObj[ROOTS][-1]+" "+verbObj[POLARITY]
                    headVerbWID = verbObj[PHRASE][-1]
                    #
                    #   2.1) Esimeses l2henduses vaatame tavalisi verbe (mitte-olema);
                    #
                    if headVerb in self.verbRules and not headVerb.startswith('ole '):
                        minInd = headVerbWID-1 if verbObj[PATTERN][0]!='ega' else headVerbWID
                        suitableNomAdvExpansions = []
                        expansionVerbs = []
                        for i in range(minInd, clauseMaxWID+1):
                            if i in widToToken and i not in annotatedWords:
                                token = widToToken[i]
                                if _isFollowedByComma( i, clause ):
                                    #  Katkestame, kui satume koma otsa (kuna ei saa kindel olla,
                                    # et teisel pool koma on olevad jupid kuuluvad ikka verbi 
                                    # juurde)
                                    break
                                if verbDaMa.matches( token ):
                                    analysisIDs = _getMatchingAnalysisIDs( token, verbDaMa )
                                    form = token[ANALYSIS][analysisIDs[0]][FORM]
                                    expansionVerbs.append( [i, token, "V_"+form ] )
                                else:
                                    for (nounAdv, vinf1) in self.verbRules[headVerb]:
                                        if (self.nomAdvWordTemplates[nounAdv]).matches(token):
                                            suitableNomAdvExpansions.append( [i, token, vinf1, \
                                                (self.nomAdvWordTemplates[nounAdv]), nounAdv ] )
                        # Teeme kindlaks, kas kontekst on laiendamiseks piisavalt yhene/selge ...
                        suitableExpansionVerb = \
                            self._canBeExpanded( headVerb, headVerbWID, suitableNomAdvExpansions, \
                                expansionVerbs, widToToken )
                        if suitableExpansionVerb:
                            phraseExt  = [suitableNomAdvExpansions[0][0], suitableExpansionVerb[0]]
                            expIsOle   = verbOle.matches(suitableExpansionVerb[1])
                            patternExt = ['nom/adv', 'ole' if expIsOle else 'verb']
                            analysisIDsExt = [ \
                                    _getMatchingAnalysisIDs( suitableNomAdvExpansions[0][1], \
                                    suitableNomAdvExpansions[0][3] ), \
                                    _getMatchingAnalysisIDs( suitableExpansionVerb[1], verbDaMa ) ]
                            # Lisame ahelale pikendused
                            verbObj[PHRASE].extend( phraseExt )
                            verbObj[PATTERN].extend( patternExt )
                            verbObj[ANALYSIS_IDS].extend( analysisIDsExt )
                            annotatedWords.extend( phraseExt )
                            expansionPerformed = True
                            #if headVerb.startswith('and '):
                            #    _debugPrint( ('+'.join(verbObj[PATTERN]))+' | '+getJsonAsTextString(clause, markTokens = [ verbObj[PHRASE] ] ))
                            #_debugPrint( ('+'.join(verbObj[PATTERN]))+' | '+getJsonAsTextString(clause, markTokens = [ verbObj[PHRASE] ] ))
                    elif headVerb in self.verbRules and headVerb.startswith('ole '):
                    #
                    #   2.2) Vaatame olema-verbi rektsiooniseoseid;
                    #
                        minInd = headVerbWID-1 if verbObj[PATTERN][0]!='ega' else headVerbWID
                        suitableNomAdvExpansions = []
                        expansionVerbs = []
                        for i in range(minInd, clauseMaxWID+1):
                            if i in widToToken and i not in annotatedWords:
                                token = widToToken[i]
                                if verbDaMa.matches( token ):
                                    analysisIDs = _getMatchingAnalysisIDs( token, verbDaMa )
                                    form = token[ANALYSIS][analysisIDs[0]][FORM]
                                    expansionVerbs.append( [i, token, "V_"+form ] )
                                else:
                                    for (nounAdv, vinf1) in self.verbRules[headVerb]:
                                        if (self.nomAdvWordTemplates[nounAdv]).matches(token):
                                            suitableNomAdvExpansions.append( [i, token, vinf1, \
                                                (self.nomAdvWordTemplates[nounAdv]), nounAdv] )
                                if _isFollowedByComma( i, clause ):
                                    #  Katkestame, kui satume koma otsa (kuna ei saa kindel olla,
                                    # et teisel pool koma on olevad jupid kuuluvad ikka verbi 
                                    # juurde)
                                    break
                        # Teeme kindlaks, kas kontekst on laiendamiseks piisavalt yhene/selge ...
                        suitableExpansionVerb = \
                            self._canBeExpanded( headVerb, headVerbWID, suitableNomAdvExpansions, \
                                expansionVerbs, widToToken )
                        if suitableExpansionVerb:
                            phraseExt  = [suitableNomAdvExpansions[0][0], suitableExpansionVerb[0]]
                            expIsOle   = verbOle.matches(suitableExpansionVerb[1])
                            patternExt = ['nom/adv', 'ole' if expIsOle else 'verb']
                            analysisIDsExt = [ \
                                _getMatchingAnalysisIDs( suitableNomAdvExpansions[0][1], \
                                suitableNomAdvExpansions[0][3] ), \
                                _getMatchingAnalysisIDs( suitableExpansionVerb[1], verbDaMa ) ]
                            # Lisame ahelale pikendused
                            verbObj[PHRASE].extend( phraseExt )
                            verbObj[PATTERN].extend( patternExt )
                            verbObj[ANALYSIS_IDS].extend( analysisIDsExt )
                            annotatedWords.extend( phraseExt )
                            expansionPerformed = True
                            #_debugPrint( ('+'.join(verbObj[PATTERN]))+' | '+getJsonAsTextString(clause, markTokens = [ verbObj[PHRASE] ] ))
                            #if suitableNomAdvExpansions[0][4].startswith('aeg;'):
                            #    _debugPrint( ('+'.join(verbObj[PATTERN]))+' | '+_getJsonAsTextString(clause, markTokens = [ verbObj[PHRASE] ] ))
        return expansionPerformed
        #
        #      Probleemsed kohad:
        #
        #      1) Kui nom/adv pole yksik s6na, vaid mitmes6naline fraas, j2etakse see eraldamata (v6i
        #         kui verb + vinf on juba eraldatud, j2etakse nom/adv vahele torkamata), nt:
        #            annab + hea võimaluse + Vda:
        #                    annavad_0 kodanikule hea võimaluse seadusi eirata_0 .
        #            annab + paremad võimalused + Vda:
        #                    sest annab_0 neile paremad võimalused oma huve kaitsta_0 .
        #
        #      2) Kui nimis6na on tegelikult mingi j2rgneva sõna eestäiend, eraldatakse yleliigne v6i
        #         katkine seos:
        #           Teada_0 on_0 isegi võimalik_0 rünnakuvahend - lõhkelaengut kandvad juhitavad mudellennukid .
        #           siis oleks_0 Jumala käes lihtne_0 asi meid hävitada_0.
        #         (probleemne just adjektiivide puhul)
        #
        #      3) Kui vahel on 'ja'/'ega' jms, võib olla tegu ellipsiga ja on vaieldav, mida sellistel 
        #         puhkudel peale hakata (praegu siiski eraldatakse):
        #           Et nad annavad_0 ju pärismaalastele töökohad ja võimaluse_0 tsiviliseeritult elada_0
        #           hooaja suve lõppedes tekib_0 inimestel maasikaisu ja soov_0 marju osta_0 
        #           paljud ei_0 paku_0 infot ega võimalust_0 kaubelda_0 reaalajas
        #           kuidas lubadusi_0 antakse_0 ja kuidas neid ära tunda_0 ?
        # 
        #      4) eraldamisel j22b 'mitte' vahelt puudu:
        #            muidu tõesti tekib_0 tahtmine_0 mitte olla_0 inimene .
        #            Mistõttu pean_0 paremaks_0 transpordiprobleeme mitte arutada_0 .
        #
        #      5) Mõningad konstruktsioonid nõuavad polaarsuse muutust:
        #         ** 'puudub'-fraasid:
        #             puudub vajadus arvestada, puudub võimalus teha jne
        #         ** 'olema'+'võimatu/asjatu/mõttetu' fraasid:
        #             rahvusliku soengu- ja rõivastustavandi jubedust on_0 võimatu_0 varjata_0
        #         ** on raske/keeruline -- v6imalik NEG
        #             NB! aga see oleneb fraasist, nt pole liiga lihtne muudab polaarsuse 
        #                 teistsuguseks
        #         ** pole raske/keeruline -- v6imalik POS
        #         ** 'vähe' eestäiend:
        #            ühel korralikul riigil oleks_0 kõige vähem põhjust_0 soovida_0
        #
        #      X) Muid näiteid katkistest kohtadest:
        #         Teoreetilise mõtestuse_0 andis_0 postmodernismile 1986. aastal Ants Juske artikliga " Millega täita_0 tühja valget ruumi ? "
        #         Esmakordselt tekkis_0 reaalne šanss realiseerida_0 Unixi suured võimalused_0 tasuta tarkvarana odava ja laia levikuga riistvara peal .
        #         millistega talle [ tsaarile ] oli_0 iga kord jäänud õigus_0 õigeusu maksu nõuda_0 .
        #         Arendada ja muuta_0 on_0 vaja_0 iga süsteemi .
        #         Ottawa tegi_0 otsuse_0 hoolimata USA palvest jätta_0 Kanada jalaväeüksused Afganistani
        #
        #
