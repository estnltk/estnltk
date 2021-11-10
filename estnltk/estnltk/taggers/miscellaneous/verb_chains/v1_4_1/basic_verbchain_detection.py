#
#    This is a part of the verb chain detector source from the version 1.4.1:
#       https://github.com/estnltk/estnltk/blob/a8f5520b1c4d26fd58223ffc3f0a565778b3d99f/estnltk/mw_verbs/basic_verbchain_detection.py
#
#     *   *   *   *
#
#     Methods for basic verb-chain detection. The methods support following functionalities:
#          1) detect main verbs of the clause:
#              *) negated main verbs:                 ('ei/ära/pole') + suitable verb;
#              *) (affirmative) 'olema' main verbs:   'olema'; 'olema' + suitable verb;
#              *) (affirmative) regular main verbs    (other than 'olema');
#          2) extend the main verbs with the infinite verb arguments they subcategorize for:
#              *) extend 'saama' verbs with infinite 'tud' verbs;
#              *) extend 'olema' verb chains with infinite 'nud/tud/mas/mata' verbs;
#              *) extent other main verbs with infinite verbs they subcategorize for
#                 (e.g. kutsuma + verb_ma :  'kutsub' + 'langetama',
#                       püüdma  + verb_da :  'püütakse' + 'keelustada');
#          3) detect 'ega' negations ('ega' + suitable verb/verb chain);
#
#     Detailed comments of the methods are in Estonian.
#

import re

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import *

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import WordTemplate
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.utils import addWordIDs
#from .debug_print import _debugPrint

# ================================================================
#    Detecting potential clause breakers, separators, endings
# ================================================================
_breakerJaNingEgaVoi = WordTemplate({ROOT:'^(ja|ning|ega|v[\u014D\u00F5]i)$',POSTAG:'[DJ]'})
_breakerAgaKuidVaid  = WordTemplate({ROOT:'^(aga|kuid|vaid)$',POSTAG:'[DJ]'})
_breakerKomaLopus    = WordTemplate({TEXT:'^.*,$'})
_breakerPunktuats    = WordTemplate({TEXT:r'^(\.\.\.|:|;|-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015)+$'})

def _isSeparatedByPossibleClauseBreakers( tokens, wordID1, wordID2, punctForbidden = True, \
                                                                    commaForbidden = True, \
                                                                    conjWordsForbidden = True ):
    '''
         Teeb kindlaks, kas j2rjendi tokens s6naindeksite vahemikus [wordID1, wordID2) (vahemiku 
        algus on inklusiivne) leidub sides6nu (ja/ning/ega/v6i), punktuatsiooni (koma, 
        sidekriipsud, koolon, kolm j2rjestikkust punkti) v6i adverbe-sidendeid aga/kuid/vaid;
         Lippudega saab kontrolli l6dvendada:
          *) punctForbidden=False lylitab v2lja punktuatsiooni ( kirjavahem2rgid v.a koma ) 
             kontrolli;
          *) commaForbidden=False lylitab v2lja koma kontrolli ( ei puuduta teisi kirjavahem2rke ) 
             kontrolli;
          *) conjWordsForbidden=False lylitab v2lja sides6nade ja adverb-sidendite kontrolli;
         Tagastab True, kui leidub kasv6i yks eelnimetatud juhtudest, vastasel juhul False;
    '''
    global _breakerJaNingEgaVoi, _breakerAgaKuidVaid, _breakerKomaLopus, _breakerPunktuats
    minWID = min(wordID1, wordID2)
    maxWID = max(wordID1, wordID2)
    insideCheckArea = False
    for i in range(len(tokens)):
        token = tokens[i]
        if token[WORD_ID] >= minWID:
            insideCheckArea = True
        if token[WORD_ID] >= maxWID:
            insideCheckArea = False
        if insideCheckArea:
            if punctForbidden and _breakerPunktuats.matches(token):
                return True
            if commaForbidden and _breakerKomaLopus.matches(token):
                return True
            if conjWordsForbidden and (_breakerAgaKuidVaid.matches(token) or \
               _breakerJaNingEgaVoi.matches(token)):
                return True
    return False

def _isClauseFinal( wordID, clauseTokens ):
    '''
        Teeb kindlaks, kas etteantud ID-ga s6na on osalause l6pus:
          -- s6nale ei j2rgne ykski teine s6na;
          -- s6nale j2rgnevad vaid punktuatsioonim2rgid ja/v6i sidendid JA/NING/EGA/VÕI;
        Tagastab True, kui eeltoodud tingimused on t2idetud, vastasel juhul False;
    '''
    jaNingEgaVoi  = WordTemplate({ROOT:'^(ja|ning|ega|v[\u014D\u00F5]i)$',POSTAG:'[DJ]'})
    punktuatsioon = WordTemplate({POSTAG:'Z'})
    for i in range(len(clauseTokens)):
        token = clauseTokens[i]
        if token[WORD_ID] == wordID:
            if i+1 == len(clauseTokens):
                return True
            else:
                for j in range(i+1, len(clauseTokens)):
                    token2 = clauseTokens[j]
                    if not (jaNingEgaVoi.matches(token2) or punktuatsioon.matches(token2)):
                        return False
                return True
    return False

def _isFollowedByComma( wordID, clauseTokens ):
    '''
        Teeb kindlaks, kas etteantud ID-ga s6nale j2rgneb vahetult koma;
        Tagastab True, kui eeltoodud tingimus on t2idetud, vastasel juhul False;
    '''
    koma = WordTemplate({ROOT:'^,+$', POSTAG:'Z'})
    for i in range(len(clauseTokens)):
        token = clauseTokens[i]
        if token[WORD_ID] == wordID:
            if re.match('^.*,$', token[TEXT]):
                return True
            elif i+1 < len(clauseTokens) and koma.matches(clauseTokens[i+1]):
                return True
            break
    return False

# Adverbid, mis tõenäoliselt on osalauses iseseisvad/otsesed verbi alluvad, ning seega ei saa
# kuuluda fraasi kooseisu ...
_phraseBreakerAdvs = \
    WordTemplate({ROOT:'^(ka|samuti|aga|et|nüüd|praegu|varsti|siis(ki)?|ju|just|siin|kohe|veel|'+\
                  'seni|küll|hiljem|varem|ikka(gi)?|jälle(gi)?|vist|juba|isegi|seal|sageli|'+\
                  'mõnikord|muidu|(tavalise|loomuliku|lihtsa|ilmse)lt|taas|harva|eile|ammu|'+\
                  'ainult|kindlasti|kindlalt)$', POSTAG:'[DJ]'})

_verbAraAgreements = [ \
       #   ära_neg.o   + V_o
       WordTemplate({ROOT:'^ära$',FORM:'neg o',POSTAG:'V'}), \
       WordTemplate({POSTAG:'V',FORM:'o'}), \
       #   ära_neg.gu  + V_gu;    ära_neg.gu  + V_tagu
       WordTemplate({ROOT:'^ära$',FORM:'neg gu',POSTAG:'V'}), \
       WordTemplate({POSTAG:'V',FORM:'^(gu|tagu)$'}), \
       #   ära_neg.me  + V_me;    ära_neg.me  + V_o
       WordTemplate({ROOT:'^ära$',FORM:'neg me',POSTAG:'V'}), \
       WordTemplate({POSTAG:'V',FORM:'^(o|me)$'}), \
       #   ära_neg.gem + V_gem
       WordTemplate({ROOT:'^ära$',FORM:'neg gem',POSTAG:'V'}), \
       WordTemplate({POSTAG:'V',FORM:'gem'}), \
       #   ära_neg.ge  + V_ge
       WordTemplate({ROOT:'^ära$',FORM:'neg ge',POSTAG:'V'}), \
       WordTemplate({POSTAG:'V',FORM:'ge'})\
]
def _canFormAraPhrase( araVerb, otherVerb ):
    '''  Teeb kindlaks, kas etteantud 'ära' verb (araVerb) yhildub teise verbiga; 
        Arvestab järgimisi ühilduvusi:
            ains 2. pööre:     ära_neg.o   + V_o
            ains 3. pööre:     ära_neg.gu  + V_gu
            mitm 1. pööre:     ära_neg.me  + V_me
                               ära_neg.me  + V_o
                               ära_neg.gem + V_gem
            mitm 2. pööre:     ära_neg.ge  + V_ge
            mitm 3. pööre:     ära_neg.gu  + V_gu
            passiiv:           ära_neg.gu  + V_tagu
         Kui yhildub, tagastab listide listi, vastasel juhul tagastab tyhja listi. 
         
         Tagastatava listi esimene liige on 'ära' verbi analüüside indeksite list 
        (millised analüüsid vastavad 'ära' verbile) ning listi teine liige on yhilduva 
        verbi analüüside indeksite list (millised analüüsid vastavad ühilduvale verbile);
        Indeksite listid on sellised, nagu neid leitakse meetodi 
        wordtemplate.matchingAnalyseIndexes(token) abil;
    '''
    global _verbAraAgreements
    for i in range(0, len(_verbAraAgreements), 2):
        araVerbTemplate   = _verbAraAgreements[i]
        otherVerbTemplate = _verbAraAgreements[i+1]
        matchingAraAnalyses = araVerbTemplate.matchingAnalyseIndexes(araVerb)
        if matchingAraAnalyses:
            matchingVerbAnalyses = otherVerbTemplate.matchingAnalyseIndexes(otherVerb)
            if matchingVerbAnalyses:
                return [matchingAraAnalyses, matchingVerbAnalyses]
    return []


# ================================================================
# ================================================================
#    Detecting basic verb chains
# ================================================================
# ================================================================

def _extractBasicPredicateFromClause( clauseTokens, clauseID ):
    ''' 
        Meetod, mis tuvastab antud osalausest kesksed verbid + nendega otseselt seotud 
        esmased verbifraasid:
           1) predikaadiga seotud eituse(d): (ei/ära/pole) + sobiv verb;
           2) olema-verbifraasid: olema; olema + sobiv verb;
           3) tavalised (mitte-olema) verbid, mis peaksid olema osalause keskmeks;
        Sisend 'clauseTokens' on list, mis sisaldab yhe osalause k6iki s6nu (pyvabamorfi poolt tehtud
        s6na-analyyse);
        Tagastab listi tuvastatud fraasidest, kus iga liige (dict) on kujul:
           { PHRASE: list,    -- tuvastatud fraasi positsioon lauses (WORD_ID indeksid);
             PATTERN: list,   -- yldine muster, mille alusel tuvastamine toimus;
             POLARITY: str,        -- polaarsus ('NEG', 'POS', '??')
             OTHER_VERBS: bool -- kas kontekstis on veel verbe, mida v6iks potentsiaalselt
                                   s6naga liita?
           }
        Eraldatakse järgmised üldised mustrid (PATTERN j2rjendid):
            verb 
            ole
            ei+V
            ole+V
            pole
            ei+ole
            pole+V
            ole+ole
            ei
            ära+V
            pole+ole
            ära
            ära+ole
        NB! Kui osalauses on veel verbe, mis v6iksid (potentsiaalselt) eraldatud mustriga liituda,
        siis m22ratakse mustris otherVerbs = True;
    '''
    global _phraseBreakerAdvs
    # Verbieituse indikaatorid
    verbEi   = WordTemplate({ROOT:'^ei$',FORM:'neg',POSTAG:'V'})
    verbEi2  = WordTemplate({ROOT:'^ei$',POSTAG:'D'})  # juhuks, kui morf yhestamises valitakse vale analyys
    verbAra  = WordTemplate({ROOT:'^ära$',FORM:'neg.*',POSTAG:'V'})
    verbPole = WordTemplate({ROOT:'^ole$',FORM:'neg.*',POSTAG:'V'})
    # Eituse sisuverbi osad
    verbEiJarel   = WordTemplate({POSTAG:'V',FORM:'o|nud|tud|nuks|nuvat|vat|ks|ta|taks|tavat$'})
    verbEiJarel2  = WordTemplate({POSTAG:'V',FORM:'neg o$'})
    # Infiniitverb, olema ja verbid, mis v6ivad olema-le j2rgneda
    verbInf = WordTemplate({POSTAG:'V', FORM:'^(da|des|ma|tama|ta|maks|mas|mast|nud|tud|v|mata)$'})
    verbOle = WordTemplate({ROOT:'^ole$',POSTAG:'V'})
    verbOleJarel = WordTemplate({POSTAG:'V',FORM:'nud$'})
    verbOleJarelHeur1 = WordTemplate({POSTAG:'V',FORM:'^(tud|da|mas)$'})
    verbOleJarelHeur2 = WordTemplate({POSTAG:'V',FORM:'^(tud|mas)$'})
    # Muud
    verb    = WordTemplate({POSTAG:'V'})
    verbid  = verb.matchingPositions( clauseTokens )
    sonaEga = WordTemplate({ROOT:'^ega$',POSTAG:'[DJ]'})
    # Eraldamise tulemused: eraldatud (verbi)fraasid ja kasutatud reeglid
    foundMatches  = []
    negPhraseWIDs = []
    posPhraseWIDs = []
    for i in range(len(clauseTokens)):
        tokenJson  = clauseTokens[i]
        matchFound = False
        # ===================================================================
        #      V e r b i e i t u s
        # ===================================================================
        if verbEi.matches(tokenJson) or verbEi2.matches(tokenJson):
            # 
            #  1. "Ei" + Verb (käskivas, -nud, -tud, -nuks, -nuvat, -vat,
            #                  -ks, -ta, -taks, tavat)
            #
            if i+1 < len(clauseTokens):
                tokenJson2 = clauseTokens[i+1]
                if verbEiJarel.matches(tokenJson2):
                    wid1 = tokenJson[WORD_ID]
                    wid2 = tokenJson2[WORD_ID]
                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ei", "verb"] }
                    matchobj[CLAUSE_IDX] = clauseID
                    if verbOle.matches(tokenJson2):
                        matchobj[PATTERN][1] = 'ole'
                    matchobj[OTHER_VERBS] = (len(verbid) > 2)
                    matchobj[POLARITY] = 'NEG'
                    matchobj[ANALYSIS_IDS] = []
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, [verbEi, verbEi2] ) )
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, verbEiJarel ) )
                    foundMatches.append( matchobj )
                    negPhraseWIDs.extend( [wid1, wid2] )
                    matchFound = True
                #
                #   Lisamuster:
                #     -neg o:   Ainult "lähe" korral, kuna selle s6na käskiv
                #               ("mine") ei lange kokku eituse vormiga;
                #
                if not matchFound and verbEiJarel2.matches(tokenJson2):
                    wid1 = tokenJson[WORD_ID]
                    wid2 = tokenJson2[WORD_ID]
                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ei", "verb"] }
                    matchobj[CLAUSE_IDX] = clauseID
                    matchobj[OTHER_VERBS] = (len(verbid) > 2)
                    matchobj[POLARITY] = 'NEG'
                    matchobj[ANALYSIS_IDS] = []
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, [verbEi, verbEi2] ) )
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, verbEiJarel2 ) )
                    foundMatches.append( matchobj )
                    negPhraseWIDs.extend( [wid1, wid2] )
                    matchFound = True
            #
            #   1.2. Kui "ei" on (osa)lause alguses, ja lauses ongi vaid kaks verbi, siis 
            #        võib eituse ja verbi vahel olla ka teisi sõnu ...
            #          Nt. Ei_0 ta ole_0 , ütlesin selge sõnaga .
            #              Hävita vaenlane - ei_0 sammugi tagane_0 .
            #
            if not matchFound and verbEi.matches(tokenJson) and i+1 < len(clauseTokens):
                #   Leiame k6ik verbid: kui ongi vaid kaks verbi, esimene 'ei'
                #  ja teine sellega sobiv verb ning kehtivad kitsendused:
                #      ** teine verb j2rgneb 'ei'-le;
                #      ** vahetult p2rast 'ei'-d pole koma (Nt 'Aga ei_0, sõna antud_0.')
                #      ** teine verb on osalause l6pus;
                if len(verbid)==2 and verbid[0]==i:
                    if verbEiJarel.matches(clauseTokens[verbid[1]]):
                        if not _isFollowedByComma( tokenJson[WORD_ID], clauseTokens ) and \
                               _isClauseFinal( clauseTokens[verbid[1]][WORD_ID], clauseTokens ):
                            wid1 = tokenJson[WORD_ID]
                            wid2 = clauseTokens[verbid[1]][WORD_ID]
                            matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ei", "verb"] }
                            matchobj[CLAUSE_IDX] = clauseID
                            if verbOle.matches(clauseTokens[verbid[1]]):
                                matchobj[PATTERN][1] = 'ole'
                            matchobj[OTHER_VERBS] = False
                            matchobj[POLARITY] = 'NEG'
                            matchobj[ANALYSIS_IDS] = []
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbEi ) )
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( clauseTokens[verbid[1]], verbEiJarel ) )
                            foundMatches.append( matchobj )
                            negPhraseWIDs.extend( [wid1, wid2] )
                            matchFound = True
            #
            #   1.X. Ei oska "ei" predikaadikonteksti m22rata (v6imalik, et ei eitatagi verbi,
            #        vaid hoopis nimis6nafraasi vms).
            #
            if not matchFound:
                wid1 = tokenJson[WORD_ID]
                matchobj = { PHRASE: [wid1], PATTERN: ["ei"] }
                matchobj[CLAUSE_IDX] = clauseID
                # Leiame, kas j2rgneb s6nu, millega potentsiaalselt saaks eituse moodustada
                matchobj[OTHER_VERBS] = \
                    any([ verbEiJarel.matches(clauseTokens[j]) for j in range(i+1, len(clauseTokens)) ])
                matchobj[POLARITY] = 'NEG'
                matchobj[ANALYSIS_IDS] = []
                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, [verbEi, verbEi2] ) )
                foundMatches.append( matchobj )
                negPhraseWIDs.extend( [wid1] )
                matchFound = True
        elif verbAra.matches(tokenJson):
            # 
            #   2. "Ära" + Verb (käskivas, -ge, -gem, -gu, -tagu, -me)
            #
            #       Kui "ära"-le järgneb (osa)lauses veel teisi verbe, proovime 
            #      moodustada ära-fraasi esimese järgneva verbiga, mis ühildub:
            #        Nt.  Ärme_0 enam nii tee_0 !
            #             Ärge_0 palun minge_0 . 
            #             Ärge_0 ainult naerma puhkege_0 .
            #
            if i+1 < len(clauseTokens) and len(verbid) >= 2:
                for verbIndex in verbid:
                    tokenJson2 = clauseTokens[ verbIndex ]
                    if tokenJson[WORD_ID] < tokenJson2[WORD_ID]:
                        # Teeme kindlaks, kas järgnev verb võib ühilduda 'ära'-ga:
                        analyses = _canFormAraPhrase( tokenJson, tokenJson2 )
                        if analyses:
                            wid1 = tokenJson[WORD_ID]
                            wid2 = tokenJson2[WORD_ID]
                            matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ära", "verb"] }
                            matchobj[CLAUSE_IDX] = clauseID
                            if verbOle.matches(tokenJson2):
                                matchobj[PATTERN][1] = 'ole'
                            matchobj[OTHER_VERBS] = (len(verbid) > 2)
                            matchobj[POLARITY] = 'NEG'
                            matchobj[ANALYSIS_IDS] = []
                            matchobj[ANALYSIS_IDS].append( analyses[0] )
                            matchobj[ANALYSIS_IDS].append( analyses[1] )
                            foundMatches.append( matchobj )
                            negPhraseWIDs.extend( [wid1, wid2] )
                            matchFound = True
                            break
                            #
                            #  Teadaolevad veakohad:  
                            #    yks koma vahel:  Ära_0 piina ennast , jäta_0 laps mulle.
                            #    (aga siin on p6hiliseks veaks puudulik morf analyys)
                            #
            #
            #   2.X. Ei oska "ära" predikaadikonteksti m22rata ...
            #
            if not matchFound:
                wid1 = tokenJson[WORD_ID]
                matchobj = { PHRASE: [wid1], PATTERN: ["ära"] }
                matchobj[CLAUSE_IDX] = clauseID
                matchobj[OTHER_VERBS] = (len(verbid) > 1)
                #  Kui kontekstis on ka teisi verbe, võib ära täita hoopis määrsõna rolli, ja
                # kuna eitusmustrid on välistatud, pole enam kindel, et tegu on eitusega;
                matchobj[POLARITY] = '??'
                matchobj[ANALYSIS_IDS] = []
                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbAra ) )
                foundMatches.append( matchobj )
                negPhraseWIDs.extend( [wid1] )
                matchFound = True
        elif verbPole.matches(tokenJson):
            # 
            #  3. "Pole" + Verb (-nud)
            #
            if i+1 < len(clauseTokens):
                tokenJson2 = clauseTokens[i+1]
                if verbOleJarel.matches(tokenJson2):
                    wid1 = tokenJson[WORD_ID]
                    wid2 = tokenJson2[WORD_ID]
                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                    matchobj[CLAUSE_IDX] = clauseID
                    if verbOle.matches(tokenJson2):
                        matchobj[PATTERN][1] = 'ole'
                    matchobj[OTHER_VERBS] = (len(verbid) > 2)
                    matchobj[POLARITY] = 'NEG'
                    matchobj[ANALYSIS_IDS] = []
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole ) )
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, verbOleJarel ) )
                    foundMatches.append( matchobj )
                    negPhraseWIDs.extend( [wid1, wid2] )
                    matchFound = True
            if not matchFound and i+1 < len(clauseTokens):
                tokenJson2 = clauseTokens[i+1]
                #
                #   3.2. Heuristik: Kui "pole" j2rel on vahetult verb (-tud, -mas), ning m6lemad
                #        paiknevad (osa)lause l6pus ning osalauses ongi vaid kaks verbi, loeme 
                #        selle ka eituse fraasiks:
                #          Nt.  Autode ostuhinda pole avalikustatud .
                #               Skriptid näitavad veateateid , kui tingimused pole täidetud .
                #               Aktsia- ja rahaturud on rahutud ning stabiilsust pole näha .
                #               ... kas ehk kedagi liikumas_0 pole_0 , keda võiks asjasse pühendada ...
                #
                if len(verbid)==2 and verbOleJarelHeur2.matches(tokenJson2) and \
                   _isClauseFinal( tokenJson2[WORD_ID], clauseTokens ):
                    wid1 = tokenJson[WORD_ID]
                    wid2 = tokenJson2[WORD_ID]
                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                    matchobj[CLAUSE_IDX] = clauseID
                    if verbOle.matches(tokenJson2):
                        matchobj[PATTERN][1] = 'ole'
                    matchobj[OTHER_VERBS] = False
                    matchobj[POLARITY] = 'NEG'
                    matchobj[ANALYSIS_IDS] = []
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole ) )
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, verbOleJarelHeur2 ) )
                    foundMatches.append( matchobj )
                    negPhraseWIDs.extend( [wid1, wid2] )
                    matchFound = True
                #
                #   3.3. Heuristik: Kui ongi vaid kaks verbi, ning "pole" j2rel on osalause l6pus
                #        "nud", loeme selle samuti yheks fraasiks. 
                #          Nt.
                #              Ladina keel pole välja surnud .
                #              Nii odavalt pole Eesti oma laevu kunagi välja andnud .
                #              Tööga pole keegi rikkaks saanud .
                #
                if not matchFound and len(verbid)==2 and verbid[0] == i:
                    if verbOleJarel.matches( clauseTokens[verbid[1]] ) and \
                       _isClauseFinal( clauseTokens[verbid[1]][WORD_ID], clauseTokens ):
                        wid1 = tokenJson[WORD_ID]
                        wid2 = clauseTokens[verbid[1]][WORD_ID]
                        matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                        matchobj[CLAUSE_IDX] = clauseID
                        matchobj[OTHER_VERBS] = False
                        if verbOle.matches( clauseTokens[verbid[1]] ):
                            matchobj[PATTERN][1] = 'ole'
                        matchobj[POLARITY] = 'NEG'
                        matchobj[ANALYSIS_IDS] = []
                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole ) )
                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( clauseTokens[verbid[1]], verbOleJarel ) )
                        foundMatches.append( matchobj )
                        negPhraseWIDs.extend( [wid1, wid2] )
                        matchFound = True
                if not matchFound:
                    #
                    #  3.4. Heuristik: Kui 'pole'-le j2rgneb osalauses kusagil kaugemal -nud, 
                    #       mis ei saa olla fraasi eestäiend, siis loeme selle olema-verbiga 
                    #       kokkukuuluvaks;
                    #
                    seenNudVerbs = 0
                    for k in range(i+1, len(clauseTokens)):
                        tokenJson2 = clauseTokens[k]
                        if verb.matches(tokenJson2) and not verbInf.matches(tokenJson2):
                            #  Kui j6uame finiitverbini, siis katkestame otsingu
                            break
                        if sonaEga.matches(tokenJson2):
                            #  Kui j6uame 'ega'-ni, siis katkestame otsingu
                            break
                        if verbOleJarel.matches(tokenJson2):
                            seenNudVerbs += 1
                            #
                            #     Kui -nud verb eelneb vahetult m6nele teisele infiniitverbile, 
                            #  on v2ga t6en2oline, et -nud on peaverb "pole" otsene alluv ning 
                            #  pole eestäiend, nt:
                            #
                            #       kuid ta polnud_0 ka teatris õppinud_1 improviseerima ning
                            #       Ega me pole_0 siia tulnud_1 paastuma ja palvetama , "
                            #       ja Raul poleks_0 teda härrasmehena kodust välja tahtnud_1 ajada .
                            #       ma pole_0 iial kasutanud_1 keelatud aineid .
                            #
                            #    Kontrollime, et nud-ile j2rgneks infiniitverb, ning
                            #  vahel poleks teisi nud-verbe ...
                            #
                            if k+1 in verbid and verbInf.matches(clauseTokens[k+1]) and \
                                seenNudVerbs < 2:
                                wid1 = tokenJson[WORD_ID]
                                wid2 = tokenJson2[WORD_ID]
                                matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                                matchobj[CLAUSE_IDX] = clauseID
                                if verbOle.matches(tokenJson2):
                                    matchobj[PATTERN][1] = 'ole'
                                matchobj[OTHER_VERBS] = True
                                matchobj[POLARITY] = 'NEG'
                                matchobj[ANALYSIS_IDS] = []
                                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole, discardAnalyses = verbInf ) )
                                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel] ) )
                                foundMatches.append( matchobj )
                                negPhraseWIDs.extend( [wid1, wid2] )
                                matchFound = True
                                #_debugPrint( (('+'.join(matchobj[PATTERN]))+' | '+_getJsonAsTextString(clauseTokens, markTokens = [ matchobj[PHRASE] ] )))
                                break
                            #
                            #     Kui -nud verb eelneb vahetult m6nele adverbile, mis t6en2oliselt
                            #  on lauses iseseisev s6na (nt 'ka', 'siis', 'veel', 'juba' jms), siis ei 
                            #  saa -nud olla eest2iend ning peaks olema peaverb "pole" otsene alluv, nt:
                            #
                            #       Varem pole_0 ma kirjandile jõudnud_0 aga sellepärast ,
                            #       " Ma pole_0 Belgias saanud_0 isegi parkimistrahvi ! "
                            #       Polnud_0 õllelembid saanud_0 veel õieti jõuluvaimu sisse elada ,
                            #       mulle polnud_0 Väike jõudnud_0 ju veel rääkida ,
                            #
                            #   Lisaks kontrollime, et vahel poleks teisi -nud verbe;
                            #
                            elif k+1<len(clauseTokens) and _phraseBreakerAdvs.matches(clauseTokens[k+1]) and \
                                seenNudVerbs < 2:
                                wid1 = tokenJson[WORD_ID]
                                wid2 = tokenJson2[WORD_ID]
                                matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                                matchobj[CLAUSE_IDX] = clauseID
                                if verbOle.matches(tokenJson2):
                                    matchobj[PATTERN][1] = 'ole'
                                matchobj[OTHER_VERBS] = (len(verbid) > 2)
                                matchobj[POLARITY] = 'NEG'
                                matchobj[ANALYSIS_IDS] = []
                                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole, discardAnalyses = verbInf ) )
                                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel] ) )
                                foundMatches.append( matchobj )
                                negPhraseWIDs.extend( [wid1, wid2] )
                                matchFound = True
                                #_debugPrint( (('+'.join(matchobj[PATTERN]))+' | '+_getJsonAsTextString(clauseTokens, markTokens = [ matchobj[PHRASE] ] )))
                                break
            if not matchFound and _isClauseFinal( tokenJson[WORD_ID], clauseTokens ):
                #
                #   3.5. Heuristik: Kui "pole" on osalause l6pus, ning sellele eelneb vahetult
                #        "nud", v6i eelneb vahetult tud/da/mas ning osalauses pole teisi verbe,
                #        loeme liiteituseks:
                #          Nt.
                #              Huvitav ainult , miks ta mulle helistanud_0 pole_0 .
                #              Mingit kuulsust ma küll kogunud_0 pole_0 .
                #
                if i-1 > -1:
                    tokenJson2 = clauseTokens[i-1]
                    if verbOleJarel.matches(tokenJson2) or (len(verbid)==2 and \
                       verbOleJarelHeur2.matches(tokenJson2)):
                        wid1 = tokenJson[WORD_ID]
                        wid2 = tokenJson2[WORD_ID]
                        matchobj = { PHRASE: [wid1, wid2], PATTERN: ["pole", "verb"] }
                        matchobj[CLAUSE_IDX] = clauseID
                        matchobj[OTHER_VERBS] = (len(verbid) > 2)
                        if verbOle.matches( tokenJson2 ):
                            matchobj[PATTERN][1] = 'ole'
                        matchobj[POLARITY] = 'NEG'
                        matchobj[ANALYSIS_IDS] = []
                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole ) )
                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel, verbOleJarelHeur2] ) )
                        foundMatches.append( matchobj )
                        negPhraseWIDs.extend( [wid1, wid2] )
                        matchFound = True
            #
            #   3.X. Ei oska "pole" predikaadikonteksti m22rata ...
            #
            if not matchFound:
                wid1 = tokenJson[WORD_ID]
                matchobj = { PHRASE: [wid1], POLARITY: 'NEG', PATTERN: ["pole"] }
                matchobj[CLAUSE_IDX]   = clauseID
                matchobj[OTHER_VERBS] = (len(verbid) > 1)
                matchobj[ANALYSIS_IDS] = []
                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbPole ) )
                foundMatches.append( matchobj )
                negPhraseWIDs.extend( [wid1] )
                matchFound = True
        # ===================================================================
        #      V e r b i   j a a t u s
        # ===================================================================
        elif tokenJson[WORD_ID] not in negPhraseWIDs and verb.matches(tokenJson) and \
             not verbInf.matches(tokenJson):
            #
            #  Tavaline verb ( mitte olema-verb )
            #
            if not verbOle.matches( tokenJson ):
                wid1 = tokenJson[WORD_ID]
                matchobj = { PHRASE: [wid1], POLARITY: 'POS', PATTERN: ["verb"] }
                matchobj[CLAUSE_IDX]   = clauseID
                matchobj[OTHER_VERBS] = (len(verbid) > 1)
                matchobj[ANALYSIS_IDS] = []
                matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verb, discardAnalyses = verbInf ) )
                foundMatches.append( matchobj )
                posPhraseWIDs.extend( [wid1] )
                matchFound = True
            #
            #  Olema-verb
            #
            else:
                if (len(verbid) == 1):
                    #  Yksik olema-verb
                    wid1 = tokenJson[WORD_ID]
                    matchobj = { PHRASE: [wid1], POLARITY: 'POS', PATTERN: ["ole"] }
                    matchobj[CLAUSE_IDX]   = clauseID
                    matchobj[OTHER_VERBS] = False
                    matchobj[ANALYSIS_IDS] = []
                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                    foundMatches.append( matchobj )
                    posPhraseWIDs.extend( [wid1] )
                    matchFound = True
                else:
                    #
                    #  Lauses on veel verbe: yritame teha kindlaks, kas tegu on liitkonstruktsiooniga
                    #
                    if i+1 < len(clauseTokens):
                        if verbOleJarel.matches(clauseTokens[i+1]) and \
                           clauseTokens[i+1][WORD_ID] not in negPhraseWIDs:
                            #
                            #   Vahetult j2rgnev '-nud':
                            #       Ta ise on_0 kasutanud_0 mitme turvafima teenuseid .
                            #       Luule on_0 võtnud_0 Linnutee kuju .
                            #       Õhtul oli_0 olnud_0 org , aga hommikul järv .
                            #
                            tokenJson2 = clauseTokens[i+1]
                            wid1 = tokenJson[WORD_ID]
                            wid2 = tokenJson2[WORD_ID]
                            matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                            matchobj[CLAUSE_IDX] = clauseID
                            if verbOle.matches(tokenJson2):
                                matchobj[PATTERN][1] = 'ole'
                            matchobj[OTHER_VERBS] = (len(verbid) > 2)
                            matchobj[POLARITY] = 'POS'
                            matchobj[ANALYSIS_IDS] = []
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, verbOleJarel ) )
                            #matchobj[PATTERN][1] += '??'
                            foundMatches.append( matchobj )
                            posPhraseWIDs.extend( [wid1, wid2] )
                            matchFound = True
                            #
                            #  NB! See reegel võib eksida eksistentsiaallausete korral,
                            #  mis, tõsi kyll, tunduvad olevat mittesagedased:
                            #        Põlvamaal oli_0 möödunud_0 nädala teine pool traagiline .
                            #        Kevadisel läbivaatusel oli_0 kogenud_0 mesinik abiks .
                            #
                        elif len(verbid)==2:
                            otherVerbIndex = verbid[1] if verbid[0]==i else verbid[0]
                            otherVerb = clauseTokens[ otherVerbIndex ]
                            #
                            #   Osalauses ongi vaid kaks verbi ning 'nud/tud/mas' on osalause 
                            #   l6pus:
                            #        Söögimaja ja kiriku uksed olid_0 suletud_0 ,
                            #        Nööp on_0 olemas_0 , kunagi õmmeldakse mantel ka külge !
                            #        Naine oli_0 Kalevi selleni viinud_0 .
                            #        Etnofuturismi esivanemaid on_0 veel vähe uuritud_0 .
                            #
                            if (verbOleJarel.matches(otherVerb) or verbOleJarelHeur2.matches(otherVerb)) and \
                               _isClauseFinal( otherVerb[WORD_ID], clauseTokens ) and \
                               otherVerb[WORD_ID] not in negPhraseWIDs:
                                wid1 = tokenJson[WORD_ID]
                                wid2 = otherVerb[WORD_ID]
                                #
                                #   Siin v6ib tekkida vigu/kaheldavaid kohti, kui kahe s6na vahel on 
                                #   sides6nu/punktuatsiooni/teatud_adverbe, n2iteks:
                                #        on_0 kaasasündinud või elu jooksul omandatud_0
                                #        Mariboris oli_0 äkki medal käes ja Tallinnas 240kilone Ruano võidetud_0
                                #        Mina olen_0 päritolult põhjaeestlane , 50 aastat Põhja-Eestis elanud_0 .
                                #   J2tame sellistel puhkudel yhtse verbifraasina eraldamata ...
                                #
                                if not _isSeparatedByPossibleClauseBreakers( clauseTokens, tokenJson[WORD_ID], otherVerb[WORD_ID], True, True, True):
                                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                                    matchobj[CLAUSE_IDX] = clauseID
                                    if verbOle.matches(otherVerb):
                                        matchobj[PATTERN][1] = 'ole'
                                    matchobj[OTHER_VERBS] = (len(verbid) > 2)
                                    matchobj[POLARITY] = 'POS'
                                    matchobj[ANALYSIS_IDS] = []
                                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( otherVerb, [verbOleJarel, verbOleJarelHeur2] ) )
                                    foundMatches.append( matchobj )
                                    posPhraseWIDs.extend( [wid1, wid2] )
                                    matchFound = True
                            elif (verbOleJarel.matches(otherVerb) or verbOleJarelHeur2.matches(otherVerb)) and \
                                  otherVerb[WORD_ID] not in negPhraseWIDs and \
                                  i+1 == otherVerbIndex:
                                  #
                                  #   Osalauses ongi vaid kaks verbi ning 'nud/tud/mas' j2rgneb vahetult
                                  #   olema verbile (umbisikuline kõneviis):
                                  #        Oktoobris-detsembris 1944. a on_0 registreeritud_0 318 haigusjuhtu .
                                  #        Enamik uuringuid on_0 korraldatud_0 täiskasvanutel .
                                  #        Graafikud on_0 tehtud_0 programmis Exel 2003 .
                                  #   Üsna sagedane just teadustekstides;
                                  #
                                    wid1 = tokenJson[WORD_ID]
                                    wid2 = otherVerb[WORD_ID]
                                    matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                                    matchobj[CLAUSE_IDX] = clauseID
                                    if verbOle.matches(otherVerb):
                                        matchobj[PATTERN][1] = 'ole'
                                    matchobj[OTHER_VERBS] = (len(verbid) > 2)
                                    matchobj[POLARITY] = 'POS'
                                    matchobj[ANALYSIS_IDS] = []
                                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                                    matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( otherVerb, [verbOleJarel, verbOleJarelHeur2] ) )
                                    foundMatches.append( matchobj )
                                    posPhraseWIDs.extend( [wid1, wid2] )
                                    matchFound = True
                                    #
                                    #   Kuna '-tud' võib potentsiaalselt olla ka eestäiend, võib tekkida 
                                    #   ka vigu:
                                    #      Tema tegevuses on_0 teatud_0 plaan ehk tegevuskava .
                                    #      Kõige tähtsam võistlusala on_0 kombineeritud_0 võistlus .
                                    #      Lõpetuseks on_0 grillitud_0 mereandide valik .
                                    #
                        #
                        #    Kui olema-verbile j2rgneb osalauses kusagil kaugemal -nud, mis ei saa
                        #   olla fraasi eestäiend, siis loeme selle olema-verbiga kokkukuuluvaks;
                        #
                        if not matchFound:
                            seenNudVerbs = 0
                            for k in range(i+1, len(clauseTokens)):
                                tokenJson2 = clauseTokens[k]
                                if verb.matches(tokenJson2) and not verbInf.matches(tokenJson2):
                                    #  Kui j6uame finiitverbini, siis katkestame otsingu
                                    break
                                if sonaEga.matches(tokenJson2):
                                    #  Kui j6uame 'ega'-ni, siis katkestame otsingu
                                    break
                                if verbOleJarel.matches(tokenJson2):
                                    seenNudVerbs += 1
                                    #
                                    #     Kui -nud verb eelneb vahetult m6nele teisele infiniitverbile, 
                                    #  on v2ga t6en2oline, et -nud on peaverb "olema" otsene alluv ning 
                                    #  pole eestäiend, nt:
                                    #
                                    #       Midagi niisugust olin_0 ma kogu aeg lootnud_1 leida .
                                    #       siis varem või hiljem on_0 ta pidanud_1 taanduma
                                    #       siis oleks_0 ta mingisuguse plaani tõesti võinud_1 koostada
                                    #       jälle on_0 ühest investeeringust saanud_1 surnud kapital
                                    #
                                    #    Kontrollime, et nud-ile j2rgneks infiniitverb, ning
                                    #  vahel poleks teisi nud-verbe ...
                                    #
                                    if k+1 in verbid and verbInf.matches(clauseTokens[k+1]) and \
                                       seenNudVerbs < 2:
                                        wid1 = tokenJson[WORD_ID]
                                        wid2 = tokenJson2[WORD_ID]
                                        matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                                        matchobj[CLAUSE_IDX] = clauseID
                                        if verbOle.matches(tokenJson2):
                                            matchobj[PATTERN][1] = 'ole'
                                        matchobj[OTHER_VERBS] = True
                                        matchobj[POLARITY] = 'POS'
                                        matchobj[ANALYSIS_IDS] = []
                                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel] ) )
                                        foundMatches.append( matchobj )
                                        posPhraseWIDs.extend( [wid1, wid2] )
                                        matchFound = True
                                        #_debugPrint( (('+'.join(matchobj[PATTERN]))+' | '+_getJsonAsTextString(clauseTokens, markTokens = [ matchobj[PHRASE] ] )))
                                        break
                                        #
                                        # Probleemset:
                                        #  *) Kui kaks -nud-i on kõrvuti, võib minna valesti, kui pimesi siduda 
                                        #     esimene, näiteks:
                                        #          küllap ta oli_0 siis ka alati armunud_0 olnud .
                                        #          Eksamikomisjon oli_0 veidi ehmunud_0 olnud ,
                                        #          Samuti on_0 mitmed TTga õnnetuses osalenud_0 lausunud ,
                                        #
                                    #
                                    #     Kui -nud verb eelneb vahetult m6nele adverbile, mis t6en2oliselt
                                    #  on lauses iseseisev s6na (nt 'ka', 'siis', 'veel', 'juba' jms), siis ei 
                                    #  saa -nud olla eest2iend ning peaks olema peaverb "olema" otsene alluv, nt:
                                    #
                                    #       Kasiinodega on_0 rikkaks saanud_1 siiski vaid hõimud ,
                                    #       See näitaja on_0 jällegi tõusnud_1 ainult Hansapangal .
                                    #       Me oleme_0 tegelikult Kristiga ikka laval laulnud_1 ka .
                                    #       Georg Ots on_0 noorte hulgas tõusnud_1 küll sümboli staatusesse
                                    #
                                    #    Lisaks kontrollime, et vahel poleks teisi -nud verbe;
                                    #
                                    elif k+1<len(clauseTokens) and _phraseBreakerAdvs.matches(clauseTokens[k+1]) and \
                                         seenNudVerbs < 2:
                                        wid1 = tokenJson[WORD_ID]
                                        wid2 = tokenJson2[WORD_ID]
                                        matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                                        matchobj[CLAUSE_IDX] = clauseID
                                        if verbOle.matches(tokenJson2):
                                            matchobj[PATTERN][1] = 'ole'
                                        matchobj[OTHER_VERBS] = (len(verbid) > 2)
                                        matchobj[POLARITY] = 'POS'
                                        matchobj[ANALYSIS_IDS] = []
                                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel] ) )
                                        foundMatches.append( matchobj )
                                        posPhraseWIDs.extend( [wid1, wid2] )
                                        matchFound = True
                                        #_debugPrint( (('+'.join(matchobj[PATTERN]))+' | '+_getJsonAsTextString(clauseTokens, markTokens = [ matchobj[PHRASE] ] )))
                                        break
                                        #
                                        #  Probleemset:
                                        #   *) kui -nud-ile vahetult eelneb sidend, v6ib -nud kuuluda v2ljaj2ttelise 
                                        #      olema verbi juurde:
                                        #          Mart Timmi on_0 maakonna üks edukamaid talupidajaid ja olnud_1 ka taluseltsi esimees .
                                        #          Ulvi oli_0 ometigi loov kunstnik ega võinud_1 ka eraelus esineda epigoonina .
                                        #
                    if i-1 > -1 and not matchFound:
                        if _isClauseFinal( tokenJson[WORD_ID], clauseTokens ) and \
                           clauseTokens[i-1][WORD_ID] not in negPhraseWIDs and \
                           (verbOleJarel.matches(clauseTokens[i-1]) or (len(verbid)==2 and \
                           verbOleJarelHeur2.matches(clauseTokens[i-1]))) and \
                           clauseTokens[i-1][WORD_ID] not in negPhraseWIDs:
                            #
                            #   Vahetult eelnev '-nud':
                            #       Ma õpetan õievalemeid , mida ma ise viiendas klassis vihanud_0 olin_0 .
                            #       ... siis kui nemad juba ära sõitnud_0 on_0 ...
                            #   Vahetult eelnev 'tud/mas' ning osalauses pole rohkem verbe:
                            #       Ja sellepärast jäigi kõik nii , nagu kirjutatud_0 oli_0 .
                            #
                            tokenJson2 = clauseTokens[i-1]
                            wid1 = tokenJson[WORD_ID]
                            wid2 = tokenJson2[WORD_ID]
                            matchobj = { PHRASE: [wid1, wid2], PATTERN: ["ole", "verb"] }
                            matchobj[CLAUSE_IDX] = clauseID
                            if verbOle.matches(tokenJson2):
                                matchobj[PATTERN][1] = 'ole'
                            matchobj[OTHER_VERBS] = (len(verbid) > 2)
                            matchobj[POLARITY] = 'POS'
                            matchobj[ANALYSIS_IDS] = []
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                            matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson2, [verbOleJarel, verbOleJarelHeur2] ) )
                            #matchobj[PATTERN][1] += '??'
                            foundMatches.append( matchobj )
                            posPhraseWIDs.extend( [wid1, wid2] )
                            matchFound = True
                    if not matchFound:
                        #
                        #    Ei oska m22rata, millega t2pselt "olema" verb seotud on ...
                        #
                        wid1 = tokenJson[WORD_ID]
                        matchobj = { PHRASE: [wid1], POLARITY: 'POS', PATTERN: ["ole"] }
                        matchobj[CLAUSE_IDX]   = clauseID
                        matchobj[OTHER_VERBS] = True
                        matchobj[ANALYSIS_IDS] = []
                        matchobj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( tokenJson, verbOle, discardAnalyses = verbInf ) )
                        #matchobj[PATTERN][0]+='??'
                        foundMatches.append( matchobj )
                        posPhraseWIDs.extend( [wid1] )
                        matchFound = True
    return foundMatches


def _expandOlemaVerbChains( clauseTokens, clauseID, foundChains ):
    '''
         Meetod, mis proovib laiendada 'olema'-l6pulisi (predikaadi) verbiahelaid, lisades 
        võimalusel nende otsa teisi verbe, nt 
            "on olnud" + "tehtud", "ei olnud" + "tehtud", "ei oleks" + "arvatud";
        Vastavalt leitud laiendustele t2iendab andmeid sisendlistis foundChains;
    '''
    verbOle       = WordTemplate({ROOT:'^ole$',POSTAG:'V'})
    verbOleJarel1 = WordTemplate({POSTAG:'V',FORM:'(nud)$'})
    verbOleJarel2 = WordTemplate({POSTAG:'V',FORM:'^(mas|tud)$'})
    verbMata      = WordTemplate({POSTAG:'V',FORM:'^(mata)$'})
    verbMaDa      = WordTemplate({POSTAG:'V',FORM:'^(da|ma)$'})
    # J22dvustame s6nad, mis kuuluvad juba mingi tuvastatud verbifraasi koosseisu
    annotatedWords = []
    for verbObj in foundChains:
        if verbObj[CLAUSE_IDX] != clauseID:
            continue
        if (len(verbObj[PATTERN])==1 and re.match('^(ei|ära|ega)$', verbObj[PATTERN][0])):
            # V2lja j22vad yksikuna esinevad ei/ära/ega, kuna need tõenäoliselt ei sega
            continue
        annotatedWords.extend( verbObj[PHRASE] )
    for verbObj in foundChains:
        if verbObj[CLAUSE_IDX] != clauseID:
            continue
        if verbObj[PATTERN][-1] == 'ole' and verbObj[OTHER_VERBS]:
            #
            #  Kui on tegemist 'olema' l6pulise verbiahelaga, mille kontekstis on teisi verbe,
            #  st saab veel laiendada ...
            #
            eiOlePattern = (len(verbObj[PATTERN])==2 and verbObj[PATTERN][0] == 'ei')
            lastVerbWID = verbObj[PHRASE][-1]
            lastTokIndex = [i for i in range(len(clauseTokens)) if clauseTokens[i][WORD_ID] == lastVerbWID]
            lastTokIndex = lastTokIndex[0]
            expansion   = None
            appliedRule = 0
            if not _isClauseFinal( lastVerbWID, clauseTokens ):
                maDaVerbsBetween = 0
                oleInfFollowing  = 0
                for i in range(lastTokIndex + 1, len(clauseTokens)):
                    token = clauseTokens[i]
                    tokenWID = token[WORD_ID]
                    if tokenWID in annotatedWords:
                        break
                    if verbMaDa.matches(token):
                        maDaVerbsBetween += 1
                    if (verbOleJarel1.matches(token)) or verbOleJarel2.matches(token):
                        #
                        #    Heuristik:
                        #      Kui olema j2rel, osalause l6pus on nud/tud/mas ja nende vahel pole yhtegi 
                        #     punktuatsioonim2rki, sides6na, adverbe aga/kuid/vaid, juba m2rgendatud verbiahelat
                        #     ega teist nud/tud/mas s6na, loeme selle s6na olema-fraasi laienduseks:
                        #
                        #           Pere ei_0 ole_0 Eestis toimuvast vaimustatud_0 .
                        #           " Viimasel ajal on_0 see asi jälle susisema hakanud_0 " ,
                        #           Esiteks ei_0 olnud_0 vajalikul ajal tavaliselt bussi tulemas_0
                        #
                        if _isClauseFinal(tokenWID, clauseTokens ) and \
                           not _isSeparatedByPossibleClauseBreakers( clauseTokens, verbObj[PHRASE][-1], \
                           tokenWID, True, True, True):
                           expansion = token
                           #   Veakoht: kui -mas j2rel on da/ma, pole kindel, et tegu otsese rektsiooniseosega:
                           #      Islamlannale on_0 harjumatu näha meest midagi maast korjamas_0 ,
                        elif verbOleJarel1.matches(token) and eiOlePattern and i-lastTokIndex<=2:
                           #
                           #   Heuristik: "ei"+"ole"-ahela j2rel "nud" ning nende vahel pole rohkem kui
                           #   yks muu s6na:
                           #            Tagantjärele mõeldes ei_0 oleks_0 ma pidanud_0 seda tegema .
                           #            Mina ei_0 ole_0 suutnud_0 siiani maad osta .
                           #
                           expansion = token
                        oleInfFollowing += 1
                        break
                    elif verbMata.matches(token) and maDaVerbsBetween == 0:
                        #
                        #    Heuristik:
                        #      Kui olema j2rel, osalause l6pus on mata ja nende vahel pole yhtegi 
                        #     punktuatsioonim2rki, sides6na, adverbe aga/kuid/vaid, juba m2rgendatud 
                        #     verbiahelat, m6nd nud/tud/mas/ma/da verbi, loeme selle s6na olema-fraasi 
                        #     laienduseks:
                        #
                        #           Maanaine on_0 veel leidmata_0 .
                        #           linnaarhitekti koht oli_0 aasta aega täitmata_0
                        #
                        if _isClauseFinal(tokenWID, clauseTokens ) and \
                           not _isSeparatedByPossibleClauseBreakers( clauseTokens, verbObj[PHRASE][-1], \
                           tokenWID, True, True, True):
                            expansion = token
                            break
                            #   Veakoht: kui vahel on 'ilma', siis see heuristik eksib t6en2oliselt:
                            #          on_0 lihtsalt tõlgendatavad ka ilma situatsioonis osalemata_0
                        oleInfFollowing += 1
                #
                #    Heuristik:
                #     Kui osalauses ei j2rgne 'olema'-verbiga yhilduvaid verbe, kyll aga eelneb vahetult 
                #    m6ni selline ning seda pole veel m2rgendatud, loeme selle potentsiaalselt olema-verbiga
                #    yhilduvaks, nt:
                #
                #                Unustatud_0 ei_0 ole_0 ka mänge .
                #                Tõhustatud_0 on_0 ka turvameetmeid .
                #                milleks looja ta maailma loonud_0 on_0 , nimelt soo jätkamiseks .
                #
                if oleInfFollowing == 0 and not expansion:
                    minWID = min( verbObj[PHRASE] )
                    lastTokIndex = [i for i in range(len(clauseTokens)) if clauseTokens[i][WORD_ID] == minWID]
                    lastTokIndex = lastTokIndex[0]
                    token = clauseTokens[lastTokIndex-1]
                    if lastTokIndex-1 > -1 and token[WORD_ID] not in annotatedWords:
                        if (verbOleJarel1.matches(token) or verbOleJarel2.matches(token)):
                            expansion = token
                            appliedRule = 1
                    
                #
                #    Eituse (aga ka vastavates jaatuse) fraasides j22vad siin eraldamata 
                #       ei + ole + Adv/Nom + Verb_da    
                #    mustrid, nt:
                #       Ei_0 ole_0 mõtet teha sellist söögikohta .
                #       Ei_0 ole_0 võimalik väiksema vastu vahetada .
                #       Ei_0 ole_0 pankuril vaja teada .
                #    Nendega proovime tegeleda hiljem.
                #
            else:
                #
                #   Leiame ahela alguspunkti (minimaalse ID-ga verbi)
                #
                minWID = min( verbObj[PHRASE] )
                lastTokIndex = [i for i in range(len(clauseTokens)) if clauseTokens[i][WORD_ID] == minWID]
                if lastTokIndex:
                    lastTokIndex = lastTokIndex[0]
                    if lastTokIndex-1 > -1 and clauseTokens[lastTokIndex-1][WORD_ID] not in annotatedWords:
                        #
                        #    Heuristik:
                        #   Kui "olema"-l6puline ahel on osalause l6pus, ning vahetult eelneb nud/tud/mas,
                        #  siis loeme selle olema juurde kuuluvaks, nt:
                        #          mis juba olnud ja veel tulemas_0 on_0 ,
                        #          Eesti selle alamprojektiga seotud_0 ei_0 ole_0 .
                        #          trombootilisi episoode kordunud_0 ei_0 ole_0 .
                        #  (Yldiselt paistab suhteliselt v2heproduktiivne reegel olevat)
                        # 
                        token = clauseTokens[lastTokIndex-1]
                        if (verbOleJarel1.matches(token) or verbOleJarel2.matches(token)):
                            expansion = token
            if expansion:
                tokenWID = expansion[WORD_ID]
                verbObj[PHRASE].append( tokenWID )
                verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( expansion, [verbOleJarel1, verbOleJarel2, verbMata] ) )
                if verbOle.matches(expansion):
                    verbObj[PATTERN].append('ole')
                else:
                    verbObj[PATTERN].append('verb')
                annotatedWords.append( tokenWID )


def _loadVerbSubcatRelations(infile):
    ''' 
        Meetod, mis loeb failist sisse verbide rektsiooniseosed infiniitverbidega;
        Eeldab, et rektsiooniseosed on tekstifailis, kujul:
           häbene	da mast
           igatse	da
        St rea alguses on verbilemma ning TAB-iga on sellest eraldatud võimalike
        rektsioonide (käändeliste verbide vormitunnuste) loetelu, tähtsuse 
        järjekorras;
        
        Tagastab rektsiooniseosed sõnastikuna, mille võtmeteks lemmad ning väärtusteks
        vastavad vormitunnuste loetelud.
    '''
    relations = dict()
    with open(infile, mode='r', encoding='utf-8') as in_f:
        for line in in_f:
            line = line.rstrip()
            if len(line) > 0 and not re.match("^#.+$", line):
                (verb, forms) = line.split('\t')
                relations[verb] = forms.split()
    return relations

_verbInfNonExpansible = WordTemplate({POSTAG:'V', FORM:'^(maks|mas|mast|mata)$'})

def _isVerbExpansible( verbObj, clauseTokens, clauseID ):
    '''
         Kontrollib, kas tavaline verb on laiendatav etteantud osalauses:
          *) verbi kontekstis (osalauses) on veel teisi verbe;
          *) verb kuulub etteantud osalausesse;
          *) tegemist ei ole olema-verbiga (neid vaatame mujal eraldi);
          *) tegemist pole maks|mas|mast|mata-verbiga;
          *) tegemist pole verbiahelaga, mille l6pus on ja/ning/ega/v6i-fraas;
         Tagastab True, kui k6ik tingimused t2idetud;
    '''
    global _verbInfNonExpansible
    # Leiame, kas fraas kuulub antud osalausesse ning on laiendatav
    if verbObj[OTHER_VERBS] and verbObj[CLAUSE_IDX] == clauseID and \
       re.match('^(verb)$', verbObj[PATTERN][-1], re.I):
        # Leiame viimasele s6nale vastava token'i
        lastToken = [token for token in clauseTokens if token[WORD_ID] == verbObj[PHRASE][-1]]
        if not lastToken:
            raise Exception(' Last token not found for '+str(verbObj)+' in '+str( getJsonAsTextString(clauseTokens) ))
        lastToken = lastToken[0]
        # Leiame, ega tegu pole maks/mas/mast/mata verbidega (neid esialgu ei laienda edasi)
        # NB! Tegelikult peaks v2hemalt -mas verbe saama siiski laiendada:
        #      Ma ei_0 käinud_0 teda palumas_0 ümber otsustada_0 .
        # Aga kuidas seda teha v6imalikult v2heste vigadega, vajab edasist uurimist ...
        if not _verbInfNonExpansible.matches(lastToken):
           #   Kontrollime, et fraasi l6pus poleks ja/ning/ega/v6i fraasi:
           #  kui on, siis esialgu targu seda fraasi laiendama ei hakka:
           if len(verbObj[PATTERN]) >=3 and verbObj[PATTERN][-2] == '&':
                return False
           return True
           #
           #  TODO: siin tuleks ilmselt keelata ka 'saama + Verb_tud' konstruktsioonide laiendused,
           #        kuna need kipuvad olema pigem vigased (kuigi haruldased); Nt.
           #
           #   ringi hääletades sai_0 rongidega jänest sõita_0 ja vagunisaatjatest neidudega öösiti napsu võetud_0 .
           #
    return False

def _suitableVerbExpansion( foundSubcatChain ):
    '''
         V6tab etteantud jadast osa, mis sobib:
          *) kui liikmeid on 3, keskmine on konjuktsioon ning esimene ja viimane 
             klapivad, tagastab selle kolmiku;
             Nt.   ei_0 saa_0 lihtsalt välja astuda_? ja_? uttu tõmmata_? 
                   => astuda ja tõmmata
          *) kui liikmeid on rohkem kui 3, teine on konjuktsioon ning esimene ja 
             kolmas klapivad, ning l6pus pole verbe, tagastab esikolmiku;
          *) kui liikmeid on rohkem kui yks, v6tab liikmeks esimese mitte-
             konjunktsiooni (kui selline leidub);
         Kui need tingimused pole t2idetud, tagastab tyhis6ne;
    '''
    markings      = []
    tokens        = []
    nonConjTokens = []
    for (marking, token) in foundSubcatChain:
        markings.append( marking )
        tokens.append( token )
        if marking != '&':
            nonConjTokens.append( token )
    if (len(markings) == 3 and markings[0]==markings[2] and markings[0]!='&' and markings[1]=='&'):
        return tokens
    elif (len(markings) > 3 and markings[0]==markings[2] and markings[0]!='&' and markings[1]=='&' and \
          all([m == '&' for m in markings[3:]]) ):
        return tokens[:3]
    elif (len(nonConjTokens) > 0):
        return nonConjTokens[:1]
    return []

def _expandSaamaWithTud( clauseTokens, clauseID, foundChains ):
    ''' 
         Meetod, mis määrab spetsiifilised rektsiooniseosed: täiendab 'saama'-verbiga lõppevaid 
        verbijadasid, lisades (v6imalusel) nende l6ppu 'tud'-infiniitverbi 
        (nt. sai tehtud, sai käidud ujumas);
         Vastavalt leitud laiendustele t2iendab andmeid sisendlistis foundChains;
    '''
    verbTud   = WordTemplate({POSTAG:'V', FORM:'^(tud|dud)$'})
    verb      = WordTemplate({POSTAG:'V'})
    verbOlema = WordTemplate({POSTAG:'V', ROOT:'^(ole)$'})
    for verbObj in foundChains:
        # Leiame, kas fraas kuulub antud osalausesse ning on laiendatav
        if _isVerbExpansible(verbObj, clauseTokens, clauseID):
            lastVerbWID = verbObj[PHRASE][-1]
            lastToken = [token for token in clauseTokens if token[WORD_ID] == lastVerbWID]
            lastIndex = [i for i in range(len(clauseTokens)) if clauseTokens[i][WORD_ID] == lastVerbWID]
            lastToken = lastToken[0]
            lastIndex = lastIndex[0]
            mainVerb  = [analysis[ROOT] for analysis in verb.matchingAnalyses(lastToken)]
            mainVerbLemma = mainVerb[0]
            # Leiame, kas tegemist on 'saama' verbiga
            if mainVerbLemma == 'saa':
                #
                #    Saama + 'tud', lubame eraldada verbiahelana vaid siis, kui:
                #     *) 'tud' on osalause l6pus ning vahel pole punktuatsioonim2rke, nt:
                #          Kord sai_0 laadalt isegi aprikoosipuu koduaeda viidud_0 .
                #     *) 'saama' on osalause l6pus ning vahetult eelneb 'tud', nt:
                #          Ja et see vajaduse korral avalikustatud_1 saaks_1 .
                #
                expansion = None
                if not _isClauseFinal(lastVerbWID, clauseTokens ):
                    for i in range(lastIndex + 1, len(clauseTokens)):
                        token = clauseTokens[i]
                        tokenWID = token[WORD_ID]
                        if verbTud.matches(token) and _isClauseFinal(tokenWID, clauseTokens ) and \
                           not _isSeparatedByPossibleClauseBreakers( clauseTokens, verbObj[PHRASE][-1], tokenWID, True, True, False):
                            expansion = token
                            break
                elif lastIndex-1 > -1:
                    if verbTud.matches(clauseTokens[lastIndex-1]):
                        expansion = clauseTokens[lastIndex-1]
                if expansion:
                    tokenWID = expansion[WORD_ID]
                    verbObj[PHRASE].append( tokenWID )
                    verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( expansion, verbTud ) )
                    if verbOlema.matches(expansion):
                        verbObj[PATTERN].append('ole')
                    else:
                        verbObj[PATTERN].append('verb')



def _expandVerbChainsBySubcat( clauseTokens, clauseID, foundChains, verbSubcat, \
                                                        skipQuestionable=False, \
                                                        breakOnPunctuation=True ):
    ''' 
        Meetod, mis proovib laiendada (mitte-'olema') verbidega l6ppevaid predikaadifraase, 
        lisades nende lõppu rektsiooniseoste järgi uusi infiniitverbe, 
        nt "kutsub" + "langetama"
           "püütakse" + "keelustada" "või" "takistada"
           "ei julgenud" + "arvata", 
           "ei hakka" + "tülitama";

        Sisend 'clauseTokens' on list, mis sisaldab yhe osalause k6iki s6nu (pyvabamorfi poolt
        tehtud s6na-analyyse); Sisend 'verbSubcat' sisaldab andmeid verb-infiniitverb 
        rektsiooniseoste kohta;
        Tulemusena t2iendatakse olemasolevat verbijadade listi (foundChains), pikendades seal
        olevaid verbiga lõppevaid fraase, millal võimalik;
    '''
    global _breakerJaNingEgaVoi, _breakerKomaLopus, _breakerPunktuats
    verb      = WordTemplate({POSTAG:'V'})
    verbInf1  = WordTemplate({POSTAG:'V', FORM:'^(da|ma|maks|mas|mast|mata)$'})
    verbOlema = WordTemplate({POSTAG:'V', ROOT:'^(ole)$'})
    sonaMitte = WordTemplate({ROOT:'^mitte$',POSTAG:'D'})
    # J22dvustame s6nad, mis kuuluvad juba mingi tuvastatud verbifraasi koosseisu
    annotatedWords = []
    for verbObj in foundChains:
        if (len(verbObj[PATTERN])==1 and re.match('^(ei|ära|ega)$', verbObj[PATTERN][0])):
            # V2lja j22vad yksikuna esinevad ei/ära/ega, kuna need tõenäoliselt ei sega
            continue
        annotatedWords.extend( verbObj[PHRASE] )
    # Leiame, millised verbid on veel vabad (st v6ivad potentsiaalselt liituda)
    freeVerbsWIDs = [t[WORD_ID] for t in clauseTokens if verbInf1.matches(t) and t[WORD_ID] not in annotatedWords]
    for verbObj in foundChains:
        # Leiame, kas fraas kuulub antud osalausesse ning on laiendatav
        if _isVerbExpansible(verbObj, clauseTokens, clauseID):
            # Leiame viimasele s6nale vastava token'i, selle lemma ja vormitunnuse
            lastToken = [token for token in clauseTokens if token[WORD_ID] == verbObj[PHRASE][-1]]
            lastIndex = [i for i in range(len(clauseTokens)) if clauseTokens[i][WORD_ID] == verbObj[PHRASE][-1]]
            lastToken = lastToken[0]
            lastIndex = lastIndex[0]
            mainVerb  = [(analysis[ROOT], analysis[FORM]) for analysis in verb.matchingAnalyses(lastToken)]
            mainVerbLemma = mainVerb[0][0]
            mainVerbForm  = mainVerb[0][1]
            positivePhrase = (verbObj[POLARITY] == 'POS')
            egaPhrase      = (verbObj[PATTERN][0] == 'ega')
            #  Teeme kindlaks, kas verbi lemma on ylesm2rgitud rektsiooniseoste leksikoni
            if mainVerbLemma in verbSubcat:
                subcatForms = verbSubcat[ mainVerbLemma ]
                for subcatForm in subcatForms:
                    foundSubcatChain = []
                    addingCompleted = False
                    #  Kui on tegu vaieldava rektsiooniseosega: j2tame vahele v6i, kui vaieldavad
                    #  on lubatud, eemaldame vaieldavuse m2rgi 
                    if re.match(r"^.+\?$", subcatForm):
                        if skipQuestionable:
                            continue
                        else:
                            subcatForm = subcatForm.replace('?', '')
                    #
                    #  1) Otsime sobivat verbi v6i verbifraasi s6na tagant, osalause teisest poolest
                    #
                    j = lastIndex + 1
                    while (j < len(clauseTokens)):
                        token = clauseTokens[j]
                        tokenWID = token[WORD_ID]
                        #  Katkestame kui:
                        #  *) satume juba m2rgendatud s6nale;
                        #  *) satume punktuatsioonile;
                        if tokenWID in annotatedWords:
                            break
                        if breakOnPunctuation and _breakerPunktuats.matches(token):
                            break
                        #  Lisame kui:
                        #  *) satume konjunktsioonile;
                        #  *) satume sobivas vormis verbile;
                        if _breakerJaNingEgaVoi.matches(token):
                            foundSubcatChain.append(('&', token))
                        if verb.matches(token):
                            tokenForms = [analysis[FORM] for analysis in verb.matchingAnalyses(token)]
                            if subcatForm in tokenForms:
                                foundSubcatChain.append( (subcatForm, token) )
                        #  Katkestame kui:
                        #  *) satume komale (kuna koma v6ib kinnituda sobiva s6na l6ppu);
                        if _breakerKomaLopus.matches(token):
                            break
                        j += 1
                    #
                    #     Kui osalause teisest poolest midagi ei leidnud, vaatame 
                    #     osalause esimest poolt:
                    #
                    #  2) Otsime sobivat verbi v6i verbifraasi vahetult s6na algusest
                    #     (seda vaid siis, kui tegemist pole nö 'ega'-verbifraasiga - 
                    #      nondele midagi eelneda ei saagi);
                    #     ( NB! 'ega' fraaside puhul tuleks tegelikult ka tagasi vaadata,
                    #       aga ainult verbi ja 'ega' vahele, ja mitte mingil juhul 
                    #       'ega'-st ettepoole );
                    #
                    if not _suitableVerbExpansion( foundSubcatChain ) and not egaPhrase:
                        minWid = min( verbObj[PHRASE] )
                        j = lastIndex - 1
                        while (j > -1):
                            token = clauseTokens[j]
                            tokenWID = token[WORD_ID]
                            #  Katkestame kui:
                            #  *) satume juba m2rgendatud s6nale (mis pole sellest fraasist);
                            #  *) satume komale v6i muule punktuatsioonile;
                            #  *) satume s6nale, mis on k6ige esimesest fraasiliikmest tagapool kui 2 s6na;
                            if tokenWID in annotatedWords and tokenWID not in verbObj[PHRASE]:
                                break
                            if _breakerKomaLopus.matches(token) or (breakOnPunctuation and _breakerPunktuats.matches(token)):
                                break
                            if token[WORD_ID]+1 < minWid:
                                break
                            #  Lisame kui:
                            #  *) satume konjunktsioonile;
                            #  *) satume sobivas vormis verbile;
                            if _breakerJaNingEgaVoi.matches(token):
                                foundSubcatChain.append(('&', token))
                            if verb.matches(token):
                                tokenForms = [analysis[FORM] for analysis in verb.matchingAnalyses(token)]
                                if subcatForm in tokenForms:
                                    foundSubcatChain.append( (subcatForm, token) )
                            j -= 1
                    suitablePhrase = _suitableVerbExpansion( foundSubcatChain )
                    if suitablePhrase:
                        #
                        #   Kui sobiv fraasikandidaat leidus, teostamine liitmise
                        #
                        for token in suitablePhrase:
                            tokenWID = token[WORD_ID]
                            verbObj[PHRASE].append( tokenWID )
                            annotatedWords.append( tokenWID )
                            if _breakerJaNingEgaVoi.matches(token):
                                verbObj[PATTERN].append('&')
                                verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( token, _breakerJaNingEgaVoi ) )
                            elif len(suitablePhrase) == 1 and verbOlema.matches(token):
                                verbObj[PATTERN].append('ole')
                                verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( token, verbOlema ) )
                                freeVerbsWIDs.remove( tokenWID )
                            else:
                                verbObj[PATTERN].append('verb')
                                analysisIDs = [i for i in range(len(token[ANALYSIS])) if subcatForm == token[ANALYSIS][i][FORM]]
                                assert len(analysisIDs) > 0
                                verbObj[ANALYSIS_IDS].append( analysisIDs )
                                freeVerbsWIDs.remove( tokenWID )
                        if not freeVerbsWIDs:
                            verbObj[OTHER_VERBS] = False
                        addingCompleted = True
                    if addingCompleted:
                        break
    #
    #   Lahtisi probleeme:
    #   *) Kui liidetavat infiniitverbi eitatakse 'mitte' abil, j22b 'mitte' fraasist v2lja, nt:
    #      Häkker peab_0 uskuma_0 oma võimetesse ja_0 mitte põrkama_0 tagasi esimeselt takistuselt
    #
    #   *) Kui fraasi l6pus on konjunktsioon, siis selle alamosi laiendama ei hakata, nt:
    #      Programm peab_0 suutma_0 arvestada ka grammatikakirjutaja vajadusi ning_0 omama_0 nö silumisrežiimi.
    #      (verbi "suutma" ei laiendata verbiga "arvestada")
    #
    #   *) Teatud verbidel on tegelikult rektsiooniseos hoopis nimis6naga, mis omakorda on siis 
    #      rektsiooniseoses infiniitverbiga, nt
    #         *) tegema + ettepanekut/jne + V_da
    #         *) tekkima + vajadus/soov/tahtmine/jne + V_da
    #         *) andma + aega/võimalust/õiguse/jne + V_da
    #         *) saama + aega/võimalust/õiguse/jne + V_da
    #         *) nägema + võimalust/põhjust/jne + V_da
    #      Praegu jäetakse sellised seosed kas yldse eraldamata, v6i siis eraldatakse vaid verb + 
    #      l6pus olev 'da' tegus6na, kui see langeb kokku vastava verbi rektsiooniga ...
    #
    #   *) Laiendatakse vaid yhe verbiga, kui:
    #        1) vahel on mitu sides6na:
    #           Elektrit ei_0 luba_0 katsuda_0 ega makki ja telekat käppida .
    #        2) vahel on /:
    #           mida inimene ei_0 oska_0 ( ei ole jõudnud ) märgata_0 / välja tuua
    #        3) vahel on koma:
    #           Ei_0 oska_0 midagi soovida_0 , tahta . "
    #           Nad ei_0 taha_0 mõista_0 , veel vähem mõistmisega vaeva näha .
    #
    #   *) J2etakse laiendamata, kui:
    #        1) s6nade vahel on verbitu komadega-kiil:
    #           Siis ei_0 peaks_0 ka nemad kui külakerjused , käsi pikalt ees , käima raha juurde küsimas .
    #        2) laiendatav verb eelneb verbifraasile kaugemal kui 1 s6na;
    #           kuid hakata Tõllaseppa magamistoast välja ajama ta ka ei_0 tihanud_0 .
    #           Sisse tulla ju ei_0 või_0 ,
    #        3) ma-rektsiooniseoste kohal ei arvestata praegu ma-verbivormi umbisikulisi vorme (tama), nt
    #           Kaup pidi_0 kohale veetama, aga ei olnud veetud .
    #           (paistab olevat üsna haruldane nähtus)
    #
    #   *) Laiendatakse yleliigselt:
    #        1) kui vahel on 'kui'-fraase:
    #             " Ja Užin ei_0 oskagi_0 muud teha_0 kui sigatseda_0 . "
    #             Sa ei_0 pea_0 muud tegema_0 kui vaid paar asja ära õiendama_0
    #             teeb_0 rohkem kahju kui selle võrra enam müüdud ajalehenumbrid iial korvata_0 suudavad
    #        2) kui vahel on 'ja' ning mingi teine infiniitverb (-nud, -tud), mis nõuab sama laiendit:
    #             Mõisahärra lasnud_0 sepa priiks ja käskinud priinime võtta_0 .
    #             Aina kõhklesin_0 ega osanud otsustada_0 .
    #        3) kui yks alamverb allub teisele alamverbile, ning rektsiooniseos langeb kokku ylemverbi
    #           seosega:
    #             Kui vaataja sel hetkel juhtus_0 kööki vett jooma_0 või_0 teise tuppa telefonile minema_0 , 
    #             siis jäi ta emotsionaalsest episoodist ilma .
    #
    #   *) Laiendatakse katkiselt:
    #        1) kui vahel on mitu sidendit (ja/ning/ega/või):
    #           et tuli_0 kulutusi teha_0 ja lupja ning kivisid maale toimetada_0 ,
    #
    #

def _extractEgaNegFromSent( sentTokens, clausesDict, foundChains ):
    ''' Meetod, mis tuvastab antud lausest 'ega'-predikaadiga seotud eituse(d): ega + sobiv verb.
        *) Juhtudel kui 'ega'-le j2rgneb juba tuvastatud, positiivse polaarsusega verbiahel (nt 
           ahel mille alguses on käskivas kõneviisis verb), liidetakse 'ega' olemasoleva ahela ette
           ning muudetakse ahela polaarsus negatiivseks;
        *) Muudel juhtudel otsitakse 'ega'-le j2rgnevat 'ei'-ga sobivat verbi (enamasti on selleks
           'nud'-verb) ning liidetakse see (teatud heuristikute j2rgi) 'ega'-ga yheks fraasiks;

        Tagastab True, kui uute 'ega' fraaside seas leidus m6ni selline, mida potentsiaalselt saaks 
        veel m6ne teise verbi liitmisega laiendada, muudel juhtudel tagastab False;
        
        Miks see meetod opereerib tervel lausel, mitte yksikul osalausel?
        >> Kuna 'ega' on sageli m2rgitud osalause piiriks (p2rast 'ega'-t v6ib l6ppeda osalause), 
           ei saa 'ega'-le j2rgnevaid verbe alati otsida yhe osalause seest, vaid tuleb vaadata 
           korraga mitut k6rvutiolevat osalauset; k2esolevalt lihtsustame ja vaatame tervet 
           lauset.
    '''
    sonaEga     = WordTemplate({ROOT:'^ega$',POSTAG:'[DJ]'})
    verbEiJarel  = WordTemplate({POSTAG:'V',FORM:'(o|nud|tud|nuks|nuvat|vat|ks|ta|taks|tavat)$'})
    verbEiJarel2 = WordTemplate({ROOT:'^mine$', POSTAG:'V',FORM:'neg o$'})
    verbTud     = WordTemplate({POSTAG:'V',FORM:'(tud)$'})
    verb        = WordTemplate({POSTAG:'V'})
    verbOlema   = WordTemplate({POSTAG:'V', ROOT:'^(ole)$'})
    # J22dvustame s6nad, mis kuuluvad juba mingi tuvastatud verbifraasi koosseisu
    annotatedWords = []
    for verbObj in foundChains:
        if (len(verbObj[PATTERN])==1 and re.match('^(ei|ära|ega)$', verbObj[PATTERN][0])):
            # V2lja j22vad yksikuna esinevad ei/ära/ega, kuna need tõenäoliselt ei sega
            continue
        annotatedWords.extend( verbObj[PHRASE] )
    expandableEgaFound = False
    for i in range(len(sentTokens)):
        token = sentTokens[i]
        if sonaEga.matches(token) and token[WORD_ID] not in annotatedWords:
            matchFound = False
            if i+1 < len(sentTokens) and sentTokens[i+1][WORD_ID] in annotatedWords:
                #
                #    K6ige lihtsam juht: eelnevalt on verbifraas juba tuvastatud (ja 
                #   eeldatavasti maksimaalses pikkuses), seega pole teha muud, kui sellele
                #   ega ette panna ning polaarsuse negatiivseks muuta:
                #         Te saate kaebusi palju ega_0 jõua_0 nendele reageerida_0 .
                #         vene keelt ta ei mõista ega_0 või_0 seepärast olla_0 vene spioon
                #   NB! Lisamist ei teosta siiski juhtudel kui:
                #    *) J2rgnev fraas on juba negatiivse polaarsusega (selline laiendamine 
                #       tekitaks lihtsalt mustreid juurde, aga sisulist infot juurde ei 
                #       annaks);
                #    *) J2rgnev s6na pole 'ei'-ga yhilduv verb (t6en2oliselt on mingi jama,
                #       nt morf yhestamisel);
                #    *) J2rgnev s6na kuulub verbiahelasse, mis algab enne 'ega'-t (see viitab 
                #       tegelikult sellele, et k6nealune verbiahel on katkiselt eraldatud);
                #
                for verbObj in foundChains:
                    if sentTokens[i+1][WORD_ID] in verbObj[PHRASE] and verbObj[POLARITY] != 'NEG' and \
                       (verbEiJarel.matches( sentTokens[i+1] ) or verbEiJarel2.matches( sentTokens[i+1] )) \
                       and i < min( verbObj[PHRASE] ):
                            verbObj[PHRASE].insert(0, token[WORD_ID])
                            verbObj[PATTERN].insert(0, 'ega')
                            verbObj[POLARITY] = 'NEG'
                            verbObj[ANALYSIS_IDS].insert(0, _getMatchingAnalysisIDs( token, sonaEga ) )
                            annotatedWords.append( token[WORD_ID] )
                            matchFound = True
                            break
            elif i+1 < len(sentTokens) and verbEiJarel.matches( sentTokens[i+1] ) and \
             sentTokens[i+1][WORD_ID] not in annotatedWords:
                #
                #    Heuristik:
                #      kui 'ega'-le j2rgneb vahetult 'ei'-ga sobiv verb (peaks olema
                #     infiniitne nud/tud verb, kuna finiitsed leitakse ja seotakse
                #     t6en2oliselt eelmises harus), siis eraldame uue fraasina:
                #
                #        Hakkasin Ainikiga rääkima ega_0 pööranud_0 Ivole enam tähelepanu .
                #        Tereese oli tükk aega vait ega_0 teadnud_0 , kas tõtt rääkida või mitte .
                #
                # >> clauseID-iks saab j2rgneva verbi ID, kuna 'ega' j2relt l2heb sageli
                #    osalausepiir ning ega-le eelnevad verbid kindlasti sellega seotud olla 
                #    ei saa.
                clauseID = sentTokens[i+1][CLAUSE_IDX]
                wid1 = sentTokens[i][WORD_ID]
                wid2 = sentTokens[i+1][WORD_ID]
                verbObj = { PHRASE: [wid1, wid2], PATTERN: ["ega", "verb"] }
                verbObj[CLAUSE_IDX] = clauseID
                if verbOlema.matches(sentTokens[i+1]):
                    verbObj[PATTERN][1] = 'ole'
                verbObj[POLARITY] = 'NEG'
                verbObj[ANALYSIS_IDS] = []
                verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( sentTokens[i], sonaEga ) )
                verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( sentTokens[i+1], verbEiJarel ) )
                # Teeme kindlaks, kas j2rgneb veel verbe, mis v6iksid potentsiaalselt liituda
                verbObj[OTHER_VERBS] = False
                if i+2 < len(sentTokens):
                    for j in range(i+2, len(sentTokens)):
                        token2 = sentTokens[j]
                        if token2[CLAUSE_IDX] == clauseID and verb.matches(token2):
                            verbObj[OTHER_VERBS] = True
                            break
                if verbObj[OTHER_VERBS]:
                    expandableEgaFound = True
                else:
                    #
                    #    Kui osalausest on tuvastatud teisi predikaadieituseid ning need
                    #   eelnevad praegusele 'ega'-eitusele , nt:
                    #        Ei lükka ma ümber ega kinnita.
                    #        Ta ei oota ega looda_0 ( enam ).
                    #    V6ib olla tegu keerukama tervikfraasiga, nt:
                    #        Ta ise pole kuidagi saanud ega tahnud_0 end samastada nendega.
                    #    Sellistel juhtudel m2rgime konteksti mitmeseks, kuna 'ega'-fraas
                    #    v6ib toetuda varasemale verbiahelale;
                    #
                    for j in range(i-1, -1, -1):
                        token2 = sentTokens[j]
                        if token2[CLAUSE_IDX] == clauseID:
                            for verbObj2 in foundChains:
                                if token2[WORD_ID] in verbObj2[PHRASE] and verbObj2[POLARITY] != 'POS':
                                    verbObj[OTHER_VERBS] = True
                                    break
                foundChains.append( verbObj )
                annotatedWords.extend( verbObj[PHRASE] )
                matchFound = True
            if not matchFound:
                #
                #    2.  'ega' + kaugemal järgnev verb
                # 
                #    2.1   Kui 'ega'-le ei j2rgne ega eelne yhtegi eitust, kyll aga j2rgneb 
                #          (osalause piires) 'ei'-le sobiv verb, loeme teatud juhtudel, et 
                #          tegu on sobiva eitusfraasiga.
                #          Nt.
                #              Nii et ega_0 Diana jõulureedel sünnitanudki .
                #              Ega_0 ta tahtnud algul rääkida .
                #           Yldiselt paistab see muster olevat sage just ilukirjanduses ja 
                #          suulise k6ne l2hedases keelekasutuses, harvem ajakirjanduses ning
                #          veel v2hem kasutusel teaduskirjanduses;
                #
                egaClauseID = sentTokens[i][CLAUSE_IDX]
                precedingNeg = False
                followingNeg = False
                followingPos = None
                for verbObj1 in foundChains:
                    if verbObj1[CLAUSE_IDX] == egaClauseID:
                        if verbObj1[POLARITY] != 'POS':
                            if any([ wid < sentTokens[i][WORD_ID] for wid in verbObj1[PHRASE] ]):
                                precedingNeg = True
                            if any([ wid > sentTokens[i][WORD_ID] for wid in verbObj1[PHRASE] ]):
                                followingNeg = True
                        elif verbObj1[POLARITY] == 'POS' and \
                             all([wid > sentTokens[i][WORD_ID] for wid in verbObj1[PHRASE]]):
                            followingPos = verbObj1
                if not precedingNeg and not followingNeg:
                    if followingPos:
                        #
                        #    K6ige lihtsam juht: kui j2rgneb positiivne verbiahel (ja eeldatavasti 
                        #   maksimaalses pikkuses) ning:
                        #        *) ahelverbi ja 'ega' vahel pole punktuatsiooni;
                        #        *) ahelverb sisaldab 'ei'-ga yhilduvat verbivormi;
                        #   liidame ahelale 'ega' ette ning muudame polaarsuse negatiivseks:
                        #        Ega_0 neil seal kerge ole_0 . "
                        #        Ega_0 70 eluaastat ole_0 naljaasi !
                        #        Ega_0 sa puusärgis paugutama_0 hakka_0 . "
                        #
                        minWID = min(followingPos[PHRASE])
                        phraseTokens = [t for t in sentTokens if t[WORD_ID] in followingPos[PHRASE]]
                        if any( [verbEiJarel.matches( t ) for t in phraseTokens] ) and \
                           not _isSeparatedByPossibleClauseBreakers( sentTokens, token[WORD_ID], minWID, True, True, False):
                            followingPos[PHRASE].insert(0, token[WORD_ID])
                            followingPos[PATTERN].insert(0, 'ega')
                            followingPos[POLARITY] = 'NEG'
                            followingPos[ANALYSIS_IDS].insert(0, _getMatchingAnalysisIDs( token, sonaEga ) )
                            annotatedWords.append( token[WORD_ID] )
                            matchFound = True
                            #
                            #   Veakoht - vahel on 'kui':
                            #      " Ega_0 muud kui pista_0 heinad põlema_0
                            #
                    elif i+1 < len(sentTokens):
                        #
                        #    Heuristik:
                        #      Kui 'ega'-le j2rgneb samas osalauses 'ei'-ga sobiv verb ning:
                        #        *) see verb ei ole 'tud'-verb (seega t6en2oliselt on 'nud');
                        #        *) see verb asub osalause l6pus v6i pole 'ega'-st kaugemal kui 
                        #           2 s6na;
                        #        *) see verb ei kuulu juba m2rgendatud verbiahelate sisse;
                        #      siis eraldame uue 'ega'-fraasina, nt:
                        #
                        #            Ega_0 poiss teda enam vahtinudki_0 .
                        #            Ega_0 keegi sellist tulemust ju soovinud_0 ,
                        #            Ja ega_0 ta soovinudki_0 Semperi kombel ümber õppida .
                        #
                        for j in range(i+1, len(sentTokens)):
                            token2 = sentTokens[j]
                            if token2[CLAUSE_IDX] == egaClauseID and verbEiJarel.matches(token2) and \
                               not verbTud.matches(token2) and token2[WORD_ID] not in annotatedWords and \
                               (_isClauseFinal( token2[WORD_ID], clausesDict[token2[CLAUSE_IDX]] ) or \
                               j-i <= 2):
                                    wid1 = sentTokens[i][WORD_ID]
                                    wid2 = token2[WORD_ID]
                                    verbObj = { PHRASE: [wid1, wid2], PATTERN: ["ega", "verb"] }
                                    verbObj[CLAUSE_IDX] = token2[CLAUSE_IDX]
                                    if verbOlema.matches(token2):
                                        verbObj[PATTERN][1] = 'ole'
                                    verbObj[POLARITY] = 'NEG'
                                    verbObj[ANALYSIS_IDS] = []
                                    verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( sentTokens[i], sonaEga ) )
                                    verbObj[ANALYSIS_IDS].append( _getMatchingAnalysisIDs( token2, verbEiJarel ) )
                                    # Teeme kindlaks, kas osalauses on veel verbe, mis v6iksid potentsiaalselt liituda
                                    verbObj[OTHER_VERBS] = False
                                    if i+2 < len(sentTokens):
                                        for j in range(i+2, len(sentTokens)):
                                            token3 = sentTokens[j]
                                            if token3[CLAUSE_IDX] == verbObj[CLAUSE_IDX] and \
                                               token2 != token3 and verb.matches(token3):
                                                    verbObj[OTHER_VERBS] = True
                                                    break
                                    if verbObj[OTHER_VERBS]:
                                        expandableEgaFound = True
                                    foundChains.append( verbObj )
                                    annotatedWords.extend( verbObj[PHRASE] )
                                    matchFound = True
                                    break
    return expandableEgaFound


def _determineVerbChainContextualAmbiguity( clauseTokens, clauseID, foundChains ):
    '''
         Meetod, mis püüab otsustada iga leitud verbiahela (foundChains liikme) puhul, kas 
        osalauses leidub veel vabu verbe, millega verbiahelat oleks võimalik täiendada;
         Kui vabu verbe ei leidu, muudab verbiahela OTHER_VERBS väärtuse negatiivseks, vastasel 
        juhul ei tee midagi.
         Sisend 'clauseTokens' on list, mis sisaldab yhe osalause k6iki s6nu (pyvabamorfi poolt
        tehtud s6na-analyyse), clauseID on vastava osalause indentifikaator; 
    '''
    verb      = WordTemplate({POSTAG:'V'})
    verbOlema = WordTemplate({POSTAG:'V', ROOT:'^(ole)$'})
    verbSaama = WordTemplate({POSTAG:'V', ROOT:'^(saa)$'})
    verbEiAra = WordTemplate({ROOT:'^(ära|ei)$',FORM:'neg.*',POSTAG:'V'})
    verbInf        = WordTemplate({POSTAG:'V', FORM:'^(da|des|ma|tama|ta|mas|mast|nud|tud|v|mata)$'})
    regularVerbInf = WordTemplate({POSTAG:'V', FORM:'^(da|ma|maks|mas|mast|mata)$'})
    olemaVerbInf   = WordTemplate({POSTAG:'V', FORM:'^(nud|tud|da|ma|mas|mata)$'})
    saamaVerbInf   = WordTemplate({POSTAG:'V', FORM:'^(tud|da|ma)$'})
    sonaMitte = WordTemplate({ROOT:'^mitte$',POSTAG:'D'})
    # J22dvustame s6nad, mis kuuluvad juba mingi tuvastatud verbifraasi koosseisu
    annotatedWords = []
    for verbObj in foundChains:
        if (len(verbObj[PATTERN])==1 and re.match('^(ei|ära|ega)$', verbObj[PATTERN][0])):
            # V2lja j22vad yksikuna esinevad ei/ära/ega, kuna need tõenäoliselt ei sega
            continue
        annotatedWords.extend( verbObj[PHRASE] )
    finVerbs      = [t for t in clauseTokens if verb.matches(t) and not verbInf.matches(t) ]
    negFinVerbs   = [t for t in finVerbs if verbEiAra.matches(t)]
    looseNegVerbs = [t for t in negFinVerbs if t[WORD_ID] not in annotatedWords]
    #
    #  Kontrollime, milline on osalause finiitverbiline kontekst. Kui seal on mingi potentsiaalne
    # segadus, jätamegi küsimärgid alles / kustutamata.
    #
    if len(negFinVerbs)==0 and len(finVerbs) >= 2:
        #  *) Kui negatiivseid finiitverbe pole, aga positiivseid on rohkem kui 2, jääb 
        #     praegu lahtiseks, mis seal kontekstis toimub. Jätame kõik küsimärgiga;
        return
    elif len(looseNegVerbs) > 0:
        #  *) Kui leidub negatiivseid finiitverbe, mida pole 6nnestunud pikemaks ahelaks
        #     pikendada, jääb samuti lahtiseks, mis seal kontekstis toimub. Jätame kõik
        #     küsimärgiga;
        return
    elif not looseNegVerbs and negFinVerbs and len(negFinVerbs)-len(finVerbs)>0:
        #  *) Kui negatiivseid verbe leidub rohkem, kui positiivseid, j22b ka lahtiseks,
        #     mis seal kontekstis täpselt toimub. NB! Mineviku eitus jääb paraku samuti
        #     lahtiseks, aga praegu ei oska selle vältimiseks lihtsat reeglit anda;
        return
    rVerbFreeVerbs = None
    olemaFreeVerbs = None
    saamaFreeVerbs = None
    for verbObj in foundChains:
        #
        #    Vaatame verbe, mille osalausekontekstis on teisi (infiniit)verbe; Kui kontekstis 
        #   ei leidu vabu (potentsiaalselt liituda võivaid verbe), märgime konteksti vabaks.
        #   Nt. alltoodud kontekstis ei ole märgitud verbidele enam yhtki teist verbi 
        #       liita (kuigi kontekstis leidub teisi infiniitverbe):
        #
        #         1920 vastu võetud Tallinna tehnikumi põhikiri kaotas_0 kehtivuse .
        #         kuid häirest haaratud õunad nakatuvad_0 kiiresti mädanikesse ,
        #
        if verbObj[CLAUSE_IDX] == clauseID and verbObj[OTHER_VERBS]:
            contextClear = False
            #
            #   Leiame viimasele s6nale vastava token'i, selle lemma ja vormitunnuse
            #
            lastToken = [ token for token in clauseTokens if token[WORD_ID] == verbObj[PHRASE][-1] ]
            lastToken = lastToken[0]
            analyses  = [ lastToken[ANALYSIS][j] for j in range(len(lastToken[ANALYSIS])) if j in verbObj[ANALYSIS_IDS][-1] ]
            mainVerb  = [ analysis[ROOT] for analysis in analyses ]
            mainVerbLemma = mainVerb[0]
            #
            #   Leiame, millised verbid on veel vabad (st v6ivad potentsiaalselt rektsiooni-
            #  seoses liituda); 'saama' ja 'olema' verbide puhul on potentsiaalsed liitujad
            #  natuke teistsugused kui ylej22nud verbidel;
            #
            if 'saa' == mainVerbLemma:
                if saamaFreeVerbs == None:
                    saamaFreeVerbs = [t[WORD_ID] for t in clauseTokens if saamaVerbInf.matches(t) and t[WORD_ID] not in annotatedWords]
                if not saamaFreeVerbs:
                    contextClear = True
            elif 'ole' == mainVerbLemma:
                if olemaFreeVerbs == None:
                    olemaFreeVerbs = [t[WORD_ID] for t in clauseTokens if olemaVerbInf.matches(t) and t[WORD_ID] not in annotatedWords]
                if not olemaFreeVerbs:
                    contextClear = True
            else:
                if rVerbFreeVerbs == None:
                    rVerbFreeVerbs = [t[WORD_ID] for t in clauseTokens if regularVerbInf.matches(t) and t[WORD_ID] not in annotatedWords]
                if not rVerbFreeVerbs:
                    contextClear = True
            #
            #   Kui yhtegi vaba verbi ei leidunud, märgime konteksti puhtaks
            #
            if contextClear:
                verbObj[OTHER_VERBS] = False
        #
        #  NB! Kui kontekstis on rohkem kui yks finiitverb, siis on v6imalik, et tegu
        #      veaga morf yhestamises, lausestamises, osalausestamises; J2tame sellised
        #      juhud kysim2rgiga;
        #


# ================================================================
#    Various supporting functions
# ================================================================

def _getMatchingAnalysisIDs( tokenJson, requiredWordTemplate, discardAnalyses = None ):
    '''   Tagastab listi tokenJson'i analyysidest, mis sobivad etteantud yksiku 
         sõnamalli või sõnamallide listi mõne elemendiga (requiredWordTemplate võib 
         olla üks WordTemplate või list WordTemplate elementidega);
         
          Kui discardAnalyses on defineeritud (ning on WordTemplate), visatakse minema
         analyysid, mis vastavad sellele s6namallile;
    '''
    final_ids = set()
    if isinstance(requiredWordTemplate, list):
        for wt in requiredWordTemplate:
            ids = wt.matchingAnalyseIndexes(tokenJson)
            if ids:
                final_ids.update(ids)
    elif isinstance(requiredWordTemplate, WordTemplate):
        ids = requiredWordTemplate.matchingAnalyseIndexes(tokenJson)
        final_ids = set(ids)
    if discardAnalyses:
        if isinstance(discardAnalyses, WordTemplate):
            ids2 = discardAnalyses.matchingAnalyseIndexes(tokenJson)
            if ids2:
                final_ids = final_ids.difference(set(ids2))
        else:
            raise Exception(' The parameter discardAnalyses should be WordTemplate.')
    if len(final_ids) == 0:
        raise Exception(' Unable to find matching analyse IDs for: '+str(tokenJson))
    return list(final_ids)


def _getJsonAsTextString(sentence, markTokens = None):
    textTokens = [tokenStruct[TEXT] for tokenStruct in sentence]
    if markTokens != None:
        for i in range(len(markTokens)):
            wordIDlist = markTokens[i]
            for wordID in wordIDlist:
                for j in range(len(sentence)):
                    if sentence[j][WORD_ID] == wordID:
                        textTokens[j] = textTokens[j]+"_"+str(i)
                        break
    return " ".join(textTokens)
