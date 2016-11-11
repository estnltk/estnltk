# -*- coding: utf-8 -*- 
#
#    An experimental chunker that detects Estonian noun phrases based on 
#   the output of dependency syntactic parser. 
#

from __future__ import unicode_literals, print_function

import re

from .names import *
from .text  import Text

from .mw_verbs.utils import WordTemplate
from .syntax.parsers import MaltParser
from .syntax.parsers import VISLCG3Parser


# =============================================================================
#   The Main Class
# =============================================================================

class NounPhraseChunker(object):
    ''' An experimental noun phrase chunker for Estonian. Attempts to detect 
        non-overlapping phrases from the text. 
        Uses a hybrid approach:
        *) First, it applies a dependency syntactic parser (MaltParser or VISLCG3Parser)
           to obtain dependency relations between words;
        *) Then it builds NP phrases by joining together consecutive words sharing
           a dependency relation: mostly in the direction from left to right, 
           "from a word to its governor in the right";
        *) Lastly, it applies a number of postprocessing rules to augment and
           correct the obtained phrases;
    '''

    parser = None

    def __init__( self, parser = None, **kwargs):
        if not parser:
            # Initialize the default parser -- MaltParser -- automatically
            self.parser = MaltParser()
        elif parser and (isinstance(parser, MaltParser) or \
                         isinstance(parser, VISLCG3Parser)):
            # Use given parser
            self.parser = parser
        else:
            raise Exception(' (!) Unexpected "parser" argument: should be an instance of (MaltParser or VISLCG3Parser)')


    def analyze_text( self, text, **kwargs ):
        ''' 
        Analyzes given Text for noun phrase chunks. 

         As result of analysis, a layer NOUN_CHUNKS will be attached to the input
        Text object, containing a noun phrases detected from the Text;
        
         Note: for preprocessing the Text, MaltParser is used by default. In order 
        to obtain a decent performance with MaltParser, it is advisable to analyse 
        texts at their full extent with this method. Splitting a text into smaller 
        chunks, such as clauses or sentences, and analysing one-small-chunk-at-time 
        may be rather demanding in terms of performance, because a file-based 
        preprocessing is used for obtaining the dependency relations.

        Parameters
        ----------
        text:  estnltk.text.Text
            The input text that should be analysed for noun phrases; 

        force_parsing : bool 
            If True, uses the *self.parser* to parse the given *text*, and overrides
            the syntactic annotations in *text* with the new layer obtained from the 
            parser;
            (default: False)
        
        syntax_layer : str
            Specifies which layer of syntactic annotations should be used as a
            basis for NP chunking; If the *syntax_layer* exists within the *text*
            (and force_parsing==False), uses the syntactic annotations from 
            *text[syntax_layer]*;
            (default: LAYER_CONLL)

        cutPhrases: bool
            If True, all phrases exceeding the cutMaxThreshold will be 
            cut into single word phrases, consisting only of part-of-speech 
            categories 'S', 'Y', 'H';
            (default: True)

        cutMaxThreshold: int
            Threshold indicating the maximum number of words allowed in a 
            phrase.
            If cutPhrases is set, all phrases exceeding the threshold will be 
            cut into single word phrases, consisting only of part-of-speech 
            categories 'S', 'Y', 'H';
            Automatic analysis of the Balanced Corpus of Estonian suggests 
            that 97% of all NP chunks are likely chunks of length 1-3, thus 
            the default threshold is set to 3;
            (default value: 3)
        
        return_type: string
            If return_type=="text" (Default), 
                returns the input Text object;
            If return_type=="labels", 
                returns a list of NP labels (strings), containing a label for 
                each word token in Text, indicating whether the word is at the 
                beginning of a phrase ('B'), inside a phrase ('I') or does 
                not belong to any phrase ('O').
            If return_type=="tokens", 
                returns a list of phrases, where each phrase is a list of
                tokens, and each token is a dictionary representing word;
            If return_type=="strings", 
                returns a list of text strings, where each string is phrase's 
                text;
            Regardless the return type, a layer named NOUN_CHUNKS will be added 
            to the input Text containing noun phrase annotations;
        
        '''
        # 0) Parse given arguments
        #
        # Output specifics
        all_return_types = ["text", "labels", "tokens", "strings"]
        return_type     = all_return_types[0]
        cutPhrases      = True
        cutMaxThreshold = 3
        annotate_text   = True
        # Syntax layer & Parsing specifics
        syntax_layer_name = LAYER_CONLL
        force_parsing     = False
        for argName, argVal in kwargs.items():
            if argName == 'cutPhrases':
                cutPhrases = bool(argVal)
            elif argName == 'force_parsing':
                force_parsing = bool(argVal)
            elif argName == 'syntax_layer':
                syntax_layer_name = argVal
            elif argName == 'cutMaxThreshold':
                cutMaxThreshold = int(argVal)
            elif argName == 'return_type':
                if argVal.lower() in all_return_types:
                    return_type = argVal.lower()
                else:
                    raise Exception(' Unexpected return type: ', argVal)
            else:
                raise Exception(' Unsupported argument given: '+argName)

        #
        # 1) Acquire the layers of morphological & syntactic annotations:
        #
        if not syntax_layer_name in text or force_parsing:
            # No existing layer found: produce a new layer with the parser
            self.parser.parse_text( text )
            if isinstance(self.parser, MaltParser):
                syntax_layer_name = LAYER_CONLL
            elif isinstance(self.parser, VISLCG3Parser):
                syntax_layer_name = LAYER_VISLCG3
            else:
                raise Exception(' (!) Unknown type of syntactic parser: ',self.parser)

        if not text.is_tagged(ANALYSIS):
            # If missing, add the layer of morphological analyses
            text = text.tag_analysis()

        # 2) Process text sentence by sentence
        all_np_labels = []
        for sentence_text in text.split_by( SENTENCES ):
            tokens       = sentence_text[WORDS]
            syntax_layer = sentence_text[syntax_layer_name]
            # Find phrases
            np_labels = self._find_phrases( tokens, syntax_layer, cutPhrases, cutMaxThreshold )
            # Normalize labels
            np_labels = [ 'O' if not l in ['B', 'I'] else l for l in np_labels ]
            # Collect results
            all_np_labels.extend( np_labels )

        # 3) Return input text, labels, phrases or phrase texts
        if annotate_text:
            self.annotateText( text, NOUN_CHUNKS, all_np_labels )
        if return_type == "text":
            return text
        elif return_type == "labels":
            return all_np_labels
        elif return_type == "tokens":
            return self.get_phrases(text, all_np_labels)
        else:
            return self.get_phrase_texts(text, all_np_labels)


    # =============================================================
    #    Utils
    # =============================================================

    _AdvStartingPhrase = WordTemplate(\
        {ROOT:'^(mitte|ei|ilma|väga|umbes|liiga|peaaegu|pisut)$',POSTAG:'[D]'})
    # TODO: tegelikult on yldse kysitav, kas siin midagi peale 'mitte'/'ei' peaks lubama ...

    _punctPos     = WordTemplate( {POSTAG:'[Z]'} )
    _jaNingEgaVoi = WordTemplate({ROOT:'^(ja|ning|ega|v[\u014D\u00F5]i)$',POSTAG:'[DJ]'})
    _k6ige        = WordTemplate({ROOT:'^(k[\u014D\u00F5]ige)$',POSTAG:'[D]'})
    _verbParticle     = WordTemplate({POSTAG:'[A]', ROOT:'^.+(tav|v|nud|tud)$'})
    _verbPastParticle = WordTemplate({POSTAG:'[A]', ROOT:'^.+(nud|tud)$'})
    
    def _getPOS( self, token, onlyFirst = True ):
        ''' Returns POS of the current token.
        '''
        if onlyFirst:
            return token[ANALYSIS][0][POSTAG]
        else:
            return [ a[POSTAG] for a in token[ANALYSIS] ]

    def _getPhrase( self, i, sentence, NPlabels ):
        ''' Fetches the full length phrase from the position i
            based on the existing NP phrase annotations (from 
            NPlabels);
            Returns list of sentence tokens in the phrase, and 
            indices of the phrase;
        ''' 
        phrase  = []
        indices = []
        if 0 <= i and i < len(sentence) and NPlabels[i] == 'B':
            phrase  = [ sentence[i] ]
            indices = [ i ]
            j = i + 1
            while ( j < len(sentence) ):
                if NPlabels[j] in ['B', '']:
                    break
                else:
                    phrase.append( sentence[j] )
                    indices.append( j )
                j += 1
        return phrase, indices

    def _getCaseAgreement(self, token1, token2):
        '''  Detects whether there is a morphological case agreement 
            between two consecutive nominals (token1 and token2), and 
            returns the common case, or None if no agreement exists;
             Applies a special set of rules for detecting agreement on
            the word in genitive followed by the word in ter, es, ab or
            kom.
        '''
        forms1 = set( [a[FORM] for a in token1[ANALYSIS]] )
        forms2 = set( [a[FORM] for a in token2[ANALYSIS]] )
        if len(forms1.intersection(forms2))==0:
            # Kontrollime ka ni-na-ta-ga k22ndeid:
            if 'sg g' in forms1:
                if 'sg ter' in forms2:
                    return 'sg ter'
                elif 'sg es' in forms2:
                    return 'sg es'
                elif 'sg ab' in forms2:
                    return 'sg ab'
                elif 'sg kom' in forms2:
                    return 'sg kom'
            elif 'pl g' in forms1:
                if 'pl ter' in forms2:
                    return 'pl ter'
                elif 'pl es' in forms2:
                    return 'pl es'
                elif 'pl ab' in forms2:
                    return 'pl ab'
                elif 'pl kom' in forms2:
                    return 'pl kom'
            return None
        else:
            return list(forms1.intersection(forms2))[0]


    # =============================================================
    #   Detect NP phrases based on the local dependency relations
    # =============================================================
    
    def _find_phrases( self, sentence, syntax_layer, cutPhrases, cutMaxThreshold ):
        ''' Detects NP phrases by relying on local dependency relations:
        
            1) Identifies potential heads of NP phrases;
            2) Identifies consecutive words that can form an NP phrase:
               2.1) potential attribute + potential head;
               2.2) quantity word or phrase + nominal;
            3) Identifies non-consecutive words (word1 __ wordN) that
               can form a complete phrase (including the gap part);
            4) Applies post-corrections;
            
            Returns a list of tags, which contains a B-I-O style phrase 
            tag for each word in the sentence ('B'-begins phrase, 'I'-
            inside phrase, or ''-not in phrase);
        '''
        NPattribPos = [ 'Y', 'S', 'A', 'C', 'G', 'H', 'N', 'O', 'K', 'D', 'P' ]
        NPheadPos   = [ 'S', 'Y', 'H' ]
        NPlabels = [ '' for i in range(len(sentence)) ]
        #
        # 0 Faas: M2rgistame k6ik s6nad, mis v6iksid olla nimis6nafraasi peas6nad, nt:
        #        Kas [venelaste] [ambitsioon] on [siiras] ?
        #        [Raskused] algasid [aastal] 2009 , mil oli [majanduskriis] .
        #        [Põllumaad] on ka , aga [kartulikasvatamisega] on üksjagu [jamamist] .
        #
        for i in range(len(sentence)):
            pos1 = self._getPOS(sentence[i])
            if pos1 in NPheadPos:
                NPlabels[i] = 'B'
            # Lisaks märgistame ka peasõnadena ka üksikud pronoomenid, kuigi 
            # eeldame, et need on peasõnadena vaid üksikutes fraasides;
            elif pos1 == 'P':
                NPlabels[i] = 'B'
        #
        # I Faas: liidame yheks nimis6nafraasiks k6ik k6rvutiseisvad nimis6nafraasi
        #     sobivad s6nad, kui esimene on järgmise vahetu alluv, nt:
        #        [Venemaa otsus] alustada Süürias õhurünnakuid ...
        #        Kas [venelaste ambitsioon] on siiras ?
        #        [Järgmine hoop] tuli 2012-2013 ...
        #        [Eelmise nädala reedel] , [19. septembril] leidsid [kolleegid] ...
        #        
        for i in range(len(sentence)):
            label1  = i
            parent1 = syntax_layer[i][PARSER_OUT][0][1]
            #label1  = sentence[i][SYNTAX_LABEL]
            #parent1 = sentence[i][SYNTAX_HEAD]
            if i+1 < len(sentence):
                label2  = i+1
                parent2 = syntax_layer[i+1][PARSER_OUT][0][1]
                #label2  = sentence[i+1][SYNTAX_LABEL]
                #parent2 = sentence[i+1][SYNTAX_HEAD]
                pos1 = self._getPOS(sentence[i])
                pos2 = self._getPOS(sentence[i+1])
                if int(parent1) == int(label2) and pos1 in NPattribPos and \
                   pos2 in NPheadPos:
                    if 'K' in pos1 and NPlabels[i] == '':
                        #
                        #   1) erandjuht: 
                        #    K fraasi alguses viitab peaaegu alati mingile jamale, 
                        #    seega katkestame, et vältida selliseid asju nagu:
                        #      ... , mille [kohta Eestiski] piisavalt näiteid .
                        #      ... lähedaste majandussidemete [tõttu Brasiiliaga] .
                        #      ... kultuuri allutamise [vastu rahavõimule] , vaid töötavad
                        # 
                        pass
                    elif 'D' in pos1 and not self._AdvStartingPhrase.matches(sentence[i]):
                        #
                        #   2) erandjuht: 
                        #   Lubame ainult teatud adverbe fraasi algusesse, et vältida selliseid
                        #   juhte nagu nt:
                        #      ... said sõna [ka lapsed] , aga kingitust
                        #      ... kättesaamatuks [nii Nehatu hamburgeriputka] ,
                        #      ... osta [ka hinnaga 1 kr] 
                        #      ... ette [just Los Angelese autonäitusel] ,
                        
                        #   TODO: M6nikord me ikkagi tahame, et D ka sees oleks, nt:
                        #      ... filmis " Tagasi [tulevikku] " ...
                        pass
                    else:
                        if NPlabels[i] == '':
                            NPlabels[i] = 'B'
                        NPlabels[i+1] = 'I'
        #
        # II Faas: Koondame kõrvutipaiknevad ja üksteisega alluvussuhtes olevad arvsõnad/numbrid 
        #     üheks arvudest koosnevaks "NP-fraasiks", nt:
        #       [Sada nelikümmend viis]
        #       [10 405 miljonit]
        #       [kaheksa miljardit]
        #     
        for i in range(len(sentence)):
            label1  = i
            parent1 = syntax_layer[i][PARSER_OUT][0][1]
            #label1  = sentence[i][SYNTAX_LABEL]
            #parent1 = sentence[i][SYNTAX_HEAD]
            pos1 = self._getPOS(sentence[i])
            if pos1 in ['N', 'O']  and  i+1 < len(sentence):
                label2  = i+1
                parent2 = syntax_layer[i+1][PARSER_OUT][0][1]
                #label2  = sentence[i+1][SYNTAX_LABEL]
                #parent2 = sentence[i+1][SYNTAX_HEAD]
                pos2 = self._getPOS(sentence[i+1])
                if pos2 in ['N', 'O'] and ( int(parent2) == int(label1) or \
                   int(parent1) == int(label2) ):
                    if NPlabels[i] == '':
                        NPlabels[i] = 'B'
                    NPlabels[i+1] = 'I'
        #
        # III Faas: Kleebime otsa NP-fraaside otsa järeltäienditena esinevad numbrilised 
        #     arvud, nt:
        #        Üritus kandis nime [Rahu Missioon 2007.]
        #        Allkirjastas [1. jaanuaril 2004.]
        #        Saabus [uus Peugeot 307] , millest [aastatel 1987-1997] ei osatud unistadagi .
        #        [Perioodil 1997-2001] oli neid rohkem , [vt tabel 1.]
        #
        for i in range(len(sentence)):
            label1  = i
            parent1 = syntax_layer[i][PARSER_OUT][0][1]
            #label1  = sentence[i][SYNTAX_LABEL]
            #parent1 = sentence[i][SYNTAX_HEAD]
            pos1 = self._getPOS(sentence[i])
            if pos1 in ['N', 'O']  and  i-1 > -1:
                label2  = i-1
                parent2 = syntax_layer[i-1][PARSER_OUT][0][1]
                #label2  = sentence[i-1][SYNTAX_LABEL]
                #parent2 = sentence[i-1][SYNTAX_HEAD]
                if int(parent1) == int(label2) and NPlabels[i-1] != '':
                    NPlabels[i] = 'I'
        #
        # IV Faas: Kleebime arvufraaside(hulgafraaside) otsa järeltäienditena esinevad 
        #     nimisõnad, nt:
        #        Meri laius [100 kilomeetri] pikkusena .
        #        Aasta alguseks oli mahust järel [30-40 protsenti] .
        #        Jah , [kümne aasta] tagusega ei maksa siin üldse võrrelda .
        #        Mees nõudis [10 miljonit dollarit] kahjutasu [10-15 cm] kaugusele .
        #        Eelmisel nädalal võttis endalt elu veel [kaks politseiametnikku] .
        #        Kujutlesin [kaheksa miljonit aastat] vana küpressimetsa [mitukümmend aastat] nooremana .
        #
        for i in range(len(sentence)):
            label1  = i
            parent1 = syntax_layer[i][PARSER_OUT][0][1]
            #label1  = sentence[i][SYNTAX_LABEL]
            #parent1 = sentence[i][SYNTAX_HEAD]
            pos1 = self._getPOS(sentence[i])
            if pos1 in ['N', 'O']  and  i+1 < len(sentence):
                label2  = i+1
                parent2 = syntax_layer[i+1][PARSER_OUT][0][1]
                #label2  = sentence[i+1][SYNTAX_LABEL]
                #parent2 = sentence[i+1][SYNTAX_HEAD]
                pos2    = self._getPOS(sentence[i+1])
                if int(parent2) == int(label1) and NPlabels[i+1] != '' and pos2 != 'P':
                    if NPlabels[i]=='':
                        NPlabels[i] = 'B'
                    NPlabels[i+1] = 'I'
        # 
        # V Faas: Kui NP-fraasi l6pus on arvu/numbrifraas ( N_Y voi N_S ), siis t6stame arvufraasi
        #         lahku, isegi kui see teatud m22ral l6huks NP-fraasi, nt 
        #               [pindala 48 ha]            ==> [pindala] [48 ha]
        #               [Järvamaal 36 283 inimest] ==> [Järvamaal] [36 283 inimest]
        #               [kasahhid 3 %]             ==> [kasahhid] [3 %]
        #               [Tallinna Lihatööstuse aktsiatest 80 protsenti] ==>
        #                      [Tallinna Lihatööstuse aktsiatest] [80 protsenti]
        #
        for i in range( len(sentence) ):
            if NPlabels[i] == 'B':
                phrase, indices = self._getPhrase( i, sentence, NPlabels )
                posTags = [ self._getPOS(tok) for tok in phrase ]
                if len(phrase)>2 and posTags[-1] in ['S','Y'] and posTags[-2]=='N' and \
                   posTags[0] not in ['N', 'O']:
                    #
                    # Lisakontroll: tegu ei tohiks olla aastarvuga, nt:
                    #    [Eesti Tervishoiuprojekt] [2015 Lisaks]
                    #    [Prantsusmaa loobumine EXPO] [2004 korraldamisest]
                    # 
                    yearCheck = re.match('.*\d\d\d\d.*', phrase[-2][TEXT])
                    #
                    # Lisakontroll: kui eelneb rohkem kui yks arv, siis tuleb 
                    #    poolitamispunkti nihutada, nt:
                    #       [Viinis 170] [000 USA dollari]
                    #       [Järvamaal 36] [283 inimest]
                    #
                    breakPoint = indices[-2]
                    j = -3
                    while posTags[j] == 'N':
                        breakPoint = indices[j]
                        j -= 1
                    if not yearCheck:
                        NPlabels[breakPoint] = 'B'

        # 
        # VI Faas: Kui NP-fraasi sobiva s6na vanem on +2 v6i rohkema s6na kaugusel s6na j2rel, 
        #          siis pole s6na veel fraasi arvatud;
        #          Arvame ta fraasi j2rgmistel juhtudel:
        #            Eelnev j2rgarv, nt:
        #                ... pühendus meenutab [teisigi] [Põhjala suurmehi] , nagu ...
        #                ... enamikus jäid [esimese] [Eesti Vabariigi aegadesse] ...
        #            Eelnev omaduss6na, nt:
        #                ... makett ühest [olulisest] [jõeäärsest tänavast] sellisena ,
        #                ... soojendades ja [suures] soojaks [köetud telgis] kuuma teed ...
        #
        for i in range(len(sentence)-1, -1, -1):
            label1  = i
            parent1 = syntax_layer[i][PARSER_OUT][0][1]
            #label1  = sentence[i][SYNTAX_LABEL]
            #parent1 = sentence[i][SYNTAX_HEAD]
            pos1 = self._getPOS(sentence[i])
            parentRelativeLoc = int(parent1) - int(label1)
            if pos1 in NPattribPos and NPlabels[i]=='' and parentRelativeLoc > 1 and \
               i+parentRelativeLoc < len(sentence):
                label2  = i+parentRelativeLoc
                parent2 = syntax_layer[i+parentRelativeLoc][PARSER_OUT][0][1]
                #label2  = sentence[i+parentRelativeLoc][SYNTAX_LABEL]
                #parent2 = sentence[i+parentRelativeLoc][SYNTAX_HEAD]
                if int(parent1) == int(label2) and NPlabels[i+parentRelativeLoc] != '':
                    #
                    #   Kogume kokku k6ik kahe s6na vahele j22vad token'id:
                    #  
                    interveningTokens   = []
                    interveningTokenIDs = []
                    j = i + 1
                    while ( j < i + parentRelativeLoc ):
                        interveningTokens.append( sentence[j] )
                        interveningTokenIDs.append( j )
                        j += 1
                    #
                    #   Eemaldame neist tokenid, mis juba kuuluvad fraasi:
                    #
                    if NPlabels[i+parentRelativeLoc] == 'I':
                        while ( len(interveningTokenIDs) > 0 ):
                            lastID = interveningTokenIDs.pop()
                            lastToken = interveningTokens.pop()
                            if NPlabels[lastID] == 'B':
                                # Kui j6udsime fraasi alguseni, siis l6petame
                                break
                    
                    #
                    #    Kontroll1: s6na ja j2rgneva s6na vahele ei tohi j22da 
                    #     punktuatsiooni ega sidendeid, kuna need j2tame alati 
                    #     fraasist v2lja;
                    #
                    punctIntervening = False
                    jaNingEgaVoi     = False
                    for interToken in interveningTokens:
                        if self._punctPos.matches( interToken ):
                            punctIntervening = True
                        if self._jaNingEgaVoi.matches( interToken ):
                            jaNingEgaVoi = True

                    #
                    #   Leiame s6na ja tema ylema vahelise k22ndeyhilduvuse;
                    #
                    caseAgreement = \
                        self._getCaseAgreement(sentence[i], sentence[i+parentRelativeLoc])

                    if pos1 == 'O' and not punctIntervening and not jaNingEgaVoi and \
                       caseAgreement != None:
                        if len(interveningTokenIDs) == 0:
                            #
                            #    VI.a.  Eelnev s6na on k22ndes yhilduv j2rgarv, nt:
                            #      ... nagu ka teised [Eesti pered] , iga ...
                            #        ... mil esimene [Tšetšeenia sõda] käis täie ...
                            #        ... ka mõnedel teistel [mineraalsetel kütetel] peale autobensiini ...
                            #        ... on pärit kolmandast [Moosese raamatust] ehk leviitide ...
                            #
                            NPlabels[i]   = 'B'
                            NPlabels[i+1] = 'I'
                        else:
                            #
                            #    VI.b.  Eelnev s6na on k22ndes yhilduv j2rgarv, ning vahele j22vad
                            #           ainult k22ndes yhilduvad s6nad, nt:
                            #        ... Teised sõjavastased [Euroopa riigid] ilmselt avaldavad ...
                            #        ... tõi ära esimesed pesuehtsad [punased värsid] . ...
                            #        ... Esimene üleriigiline [automatiseeritud haiguseregister] - vähiregister ...
                            #
                            agreements = [self._getCaseAgreement(interTok, sentence[i+parentRelativeLoc]) for interTok in interveningTokens]
                            if all(agreements):
                                NPlabels[i] = 'B'
                                j = i + 1
                                while ( j <= i + parentRelativeLoc ):
                                    NPlabels[j] = 'I'
                                    j += 1

                    if pos1 in ['A','G'] and not punctIntervening and not jaNingEgaVoi and \
                       caseAgreement != None:
                        # 
                        #   Lisakontroll 1:
                        #      Jätame algusesse lisamata kesksõnadena esinevad sõnad, kuna 
                        #      nende puhul on tõenäoliselt tegemist millegi keerukamaga (nn
                        #      lauselühendiga):
                        #        ... Pingilt sekkunud [Chris Anstey] viskas ...
                        #        ... NBA meistriks tüürinud [Phil Jackson] ...
                        #        ... kaasaegsele maailmale mittevastav [teoreetiline lähenemine] ...
                        #
                        isVerbParticle = self._verbParticle.matches(sentence[i])
                        #
                        #  Lisakontroll 2:
                        #      Kui omaduss6na ja fraasi vahele j22b ka teisi s6nu, teeme 
                        #      kindlaks, et need s6nad poleks s6naliikidest V, D, J, mis
                        #      on probleemsed, nt:
                        #       D : ...  skreipi nii [pärilik] kui ka [nakkav haigus]  ...
                        #       V : ...  2002. aasta [keskmine] purunenud [terade saak]  ...
                        #       J : ...  oleks maakondadele [sobilik] kuni [14-rühmaline loend] Eesti  ...
                        #
                        interveningProblematicPOS = False
                        if len(interveningTokenIDs) > 0:
                            iPosTags = [ a[POSTAG] for t1 in interveningTokens for a in t1[ANALYSIS] ]
                            interveningProblematicPOS = \
                              'V' in iPosTags or 'D' in iPosTags or 'J' in iPosTags or 'Z' in iPosTags
                        if not isVerbParticle and len(interveningTokenIDs) == 0:
                            #
                            #    VI.c.  Eelnev s6na on k22ndes yhilduv ja vahetult eelnev 
                            #           omaduss6na (v.a. kesks6na), nt:
                            #           ... peeti pidu karmi [vene korra] ajal ning ...
                            #           ... äravajunud , arhailisest [Suurbritannia nurgast] ...
                            #           ... , võimaldades uutel [vapratel riikidel] kahel pool ...
                            #
                            NPlabels[i]   = 'B'
                            NPlabels[i+1] = 'I'
                        elif not isVerbParticle and len(interveningTokenIDs) > 0 and \
                            not interveningProblematicPOS:
                            #
                            #    VI.d.  Eelnev s6na on k22ndes yhilduv omaduss6na (v.a. kesks6na) 
                            #           ning vahele j22b veel v2hemalt yks sobiva POS tag'iga
                            #           s6na, nt:
                            #           ... korral on [tavaline] tugev [päevane unisus] , ...
                            #           ... mõjus silmadele [vana] mustvalge pisike [ekraan] ...
                            #           ... on enesekindel [valgete] higiste [kätega intelligent] ...
                            #
                            NPlabels[i] = 'B'
                            j = i + 1
                            while ( j <= i + parentRelativeLoc ):
                                NPlabels[j] = 'I'
                                j += 1
                                
                    if pos1 in ['C'] and not punctIntervening and not jaNingEgaVoi and \
                       caseAgreement != None:
                        if i - 1 > -1  and  self._k6ige.matches( sentence[i - 1] ):
                            #
                            #    VI.e.  Eelnev s6na on k22ndes yhilduv keskv6rde omaduss6na, 
                            #           millele eelneb yliv6rde tunnus 'k6ige', nt:
                            #           ... juhib perekonda kõige noorem [täiskasvanud naine] . ...
                            #           ... Kõige suurem [akustiline erinevus] oli vokaalide ...
                            #           ... on kõige levinumad [antikolinergilised ravimid] ...
                            #
                            NPlabels[i-1] = 'B'
                            j = i
                            while ( j <= i + parentRelativeLoc ):
                                NPlabels[j] = 'I'
                                j += 1
                        elif re.match('^(pl\s.+|sg\s(ab|abl|ad|all|el|es|ill|in|kom|ter|tr))$', \
                             caseAgreement):
                            #
                            #    VI.f.  Eelnev s6na on k22ndes yhilduv keskv6rde omaduss6na, 
                            #           mis on kas mitmuses v6i yhildub semantilise k22ndega, nt:
                            #           ... olnud üks aktiivsemaid [NATO rahupartnereid] . ...
                            #           ... meestel lisandub halvemale [füüsilisele tervisele] veel ...
                            #           ... Varasemates [samalaadsetes uurimustes] on laste ...
                            #          (grammatilise ainsusek22nde puhul ei pruugi nii kindel
                            #           olla, et kuulub just nimis6nafraasi juurde: v6ib kuuluda
                            #           ka (olema) verbifraasi juurde)
                            #
                            NPlabels[i] = 'B'
                            j = i + 1
                            while ( j <= i + parentRelativeLoc ):
                                NPlabels[j] = 'I'
                                j += 1
                            
                            #ex = self.__debug_extract_NP_from_pos(sentence, NPlabels, i-1, i+parentRelativeLoc)
                            #try:
                            #    print(sentence[i][TEXT]+' | '+sentence[i+parentRelativeLoc][TEXT]+' | '+pos1+" | "+ex)
                            #except:
                            #    print(' ### Err ###')
                       


        #
        #   Viimane faas: rakendame nn j2relparandusi, proovime pahna v2lja visata ...
        #
        self._apply_post_fixes( sentence, NPlabels, cutPhrases, cutMaxThreshold )
        return NPlabels


    _verbEi  = WordTemplate({ROOT:'^ei$',POSTAG:'[DV]'})  
    _verbOle = WordTemplate({ROOT:'^ole$',POSTAG:'V'})

    def _apply_post_fixes( self, sentence, NPlabels, cutPhrases, cutMaxThreshold ):
        '''  Fraasituvastaja j2relparandused:
            *) Tekstis6renduste eemaldamine (s6rendatud tekst ei pruugi olla 
                fraas, v6ib olla nt terve lause);
            *) Problemaatiliste kesks6nade eemaldamine fraasialgusest;
            *) Ainult arvs6nadest koosnevate fraaside eemaldamine;
            *) ...
            *) B/I m2rkide parandus;
            *) Fraaside l6ikamine sobivasse pikkusse (kui cutPhrases==True ja
               cutMaxThreshold on seadistatud);
        '''
        for i in range( len(sentence) ):
            if NPlabels[i] == 'B':
                phrase, indices = self._getPhrase( i, sentence, NPlabels )
                posTags = [ self._getPOS(tok) for tok in phrase ]
                #
                #   1) Eemaldame tekstis6rendused, mis kogemata kombel on loetud
                #      eraldi s6nadeks ja s6nade liitmise abil saadud fraasid, nt:
                #       et [õ i g e k e e l s u s r a a m a t u i s] sisaldub
                #       , [k u s v õ i m i l l a l] ma
                #
                if len(posTags) > 1 and len( set(posTags).difference(set(['Y'])) )==0:
                    # Kustutame fraasi
                    for k in indices:
                        NPlabels[k] = ''
                if len(posTags) > 1 and posTags[0] == 'A':
                    forms = [ a[FORM] for a in phrase[0][ANALYSIS] ]
                    if 'nud' in forms or 'tud' in forms or 'dud' in forms:
                        #
                        #   2) Eemaldame nud/tud fraasi algusest, kui nud/tud 
                        #      moodustavad toenaolisel liitoeldise, nt:
                        #           täpselt on [jälgitud seadust] .
                        #           Töötud on [kutsunud protestiga] liituma ka töölisi
                        #           ise ei [saanud naeru] pidama . "
                        #
                        if i - 1  >  -1 and ( \
                           self._verbEi.matches(sentence[i-1]) or \
                           self._verbOle.matches(sentence[i-1]) ):
                           NPlabels[i] = ''
                           #print(self.__debug_extract_NP_from_pos(sentence, NPlabels, i))
                if len(phrase) > 1 and set(posTags).issubset(set(['O', 'N'])):
                    #
                    #   3) Eemaldame vaid arvs6nadest koosnevad fraasid, nt:
                    #           , vaid [800 miljonit] .
                    #           põhjustel umbes [100 000.] 
                    #           kolmandat ja [kolmas neljandat] .
                    #           üleeuroopalisel konkursil [esimese kolme] hulka .
                    #           1990. aastate [teisel poolel] .
                    #           võitis küll [esimese veerandi 31] : 13 ,
                    #
                    for k in indices:
                        NPlabels[k] = ''
                if posTags.count( 'N' ) > 7:
                    #
                    #   4) Eemaldame ylipikaks veninud numbrifraasid (kuna on kahtlus,
                    #      et sellisel juhul pole tegu mitte numbrifraasiga, vaid
                    #      mingi loetelu/tabeli vms-ga), nt:
                    #         Vaip , [1 1 1 1 1 0 1 1 1 1 Vaip] [ : 2
                    #         [1 0 0 0 0 1 1 1 1 B] Ühes Eesti ettevõttes
                    #  
                    for k in range( len(indices) ):
                        ind = indices[k]
                        pos = posTags[k]
                        if pos == 'N' and ( k==0 or (k>0 and NPlabels[ind-1]=='') ):
                            NPlabels[ind] = ''
                        elif ( k > 0 and NPlabels[ind-1] == '' ):
                            NPlabels[ind] = 'B'
                        elif ( k > 0 and NPlabels[ind-1] != '' ):
                            NPlabels[ind] = 'I'

                #  Kontrollime, kas fraasis eelneb suurt2helisele s6nale 
                #    mineviku kesks6na, mis pole suurt2heline;                
                verbPartFollowedByTitle = -1
                for j in range( len(phrase) ):
                    if self._verbPastParticle.matches( phrase[j] ) and \
                       not phrase[j][TEXT].istitle() and \
                       j+1 < len(phrase) and \
                       phrase[j+1][TEXT].istitle():
                        verbPartFollowedByTitle = j
                if verbPartFollowedByTitle == 0:
                    #   
                    #  5) P2risnimele eelneva kesks6na kustutamine:
                    #     P2risnimele eelnev kesks6na on sageli probleemne, st v6ib olla:
                    #           a) seotud eelneva verbiga, nt:
                    #               ... Hiibus ei [jätnud Elviiret] kiitmata ...
                    #              ... on isa-ema kodu [vahetanud Kohila] vastu ...
                    #              ... on aastaid [olnud Valgemäe perenaine] ...
                    #           b) olla osa keerukamast nimis6nafraasist (lauselyhendist), nt:
                    #              ... revolutsiooni ellu [viinud Reagan] oli ametist lahkudes ...
                    #              ... olümpiamängude A-normi [täitnud Uusorg] ...
                    #      Seet6ttu kustutame teatud tingimustel eelneva kesks6na maha;
                    #
                    NPlabels[indices[verbPartFollowedByTitle]]   = ''
                    NPlabels[indices[verbPartFollowedByTitle]+1] = 'B'

                if posTags[0] == 'C' and i + 1 > -1 and NPlabels[i-1] == '':
                    #   
                    #  6) Puuduva 'kõige' lisamine fraasile, mille alguses on C, nt:
                    #      ... Kõige [selgemal päeval] läksin ma taas ...
                    #      ... Ka kõige [avarama ruumiihalusega eurooplane] talub Hiinas ...  
                    #      ... Kõige [nõrgema toimega] olid harilik puju ...
                    #
                    if self._k6ige.matches( sentence[i-1] ):
                        NPlabels[i-1] = 'B'
                        NPlabels[i]   = 'I'
                if posTags[0] == 'C' and len( posTags ) == 2 and posTags[1] == 'H' and \
                   NPlabels[i] == 'B':
                    #
                    #  7) Empiiriline tähelepanek - kui pärisnime ees on komparatiiv-
                    #     omadussõna, siis enamasti on tegu katkise fraasiga, nt:
                    #       ... nähtavas tulevikus [tähtsam Balkanitel] toimuv kui ...
                    #       ... oma eluasemekuludeks [varasema Tallinnas] kehtinud ...
                    #       ... 30 kraadi [paremal Jedinstvost] ( Ühtsusest ) ...
                    #     Seetõttu eemaldame fraasist C;
                    #
                    NPlabels[i]   = ''
                    NPlabels[i+1] = 'B'

        # X) Kui kogemata on sattunud m6ni iseseisev 'I' (ilma eelneva 'I' v6i 'B'-ta),
        #    muudame selle 'B'-ks
        for i in range( len(sentence) ):
            if NPlabels[i] == 'I':
                if i == 0 or (i-1>-1 and NPlabels[i-1] not in ['I','B']):
                    NPlabels[i] = 'B'

        #
        # Y) Kui on n6utud fraaside l6ikamine pikkuse j2rgi (j2tta alles vaid fraasid
        #    pikkusega N), l6ikame pikkust N yletavad fraasid juppideks nii, et alles
        #    j22vad vaid fraasi peas6naks sobivad s6nad;
        #
        if cutPhrases and cutMaxThreshold > 0:
            NPheadPos = [ 'S', 'Y', 'H' ]
            for i in range( len(sentence) ):
                if NPlabels[i] == 'B':
                    phrase, indices = self._getPhrase( i, sentence, NPlabels )
                    posTags = [ self._getPOS(tok) for tok in phrase ]
                    if len(phrase) > cutMaxThreshold:
                        for j in range(len(phrase)):
                            posTag = posTags[j]
                            if posTag in NPheadPos:
                                # J2tame alles vaid nimis6nafraasi peas6nadeks
                                # sobivad s6nad, yksikute s6nadena;
                                NPlabels[indices[j]] = 'B'
                            else:
                                # Kui s6na ei sobi peas6naks, kustutame sellelt
                                # yldse m2rgenduse;
                                NPlabels[indices[j]] = ''



    # ===========================================================
    #   Extracting phrases from annotations
    # ===========================================================

    def get_phrases(self, text, np_labels):
        ''' Given a Text and a BIO labels (one label for each word in Text) , 
            extracts phrases and returns as a list of phrases, where each phrase 
            is a list of word tokens belonging to the phrase;
            
            Parameters
            ----------
            text:  estnltk.text.Text
                The input Text, or a list consecutive words (dict objects).
                The method attempts to automatically determine the type of 
                the input;
                
            np_labels : list of str
                A list of strings, containing a B-I-O label for each word in 
                *text*;
                
            Returns
            -------
            list of (list of tokens)
                List of phrases, where each phrase is a list of word tokens 
                belonging to the phrase;
        '''
        # 1) Take different inputs to common list of words format:
        input_words = []
        if isinstance(text, Text):
            # input is Text
            input_words = text.words
        elif isinstance(text, list) and len(text)>0 and isinstance(text[0], dict) and \
             TEXT in text[0]:
            # input is a list of words
            input_words = text
        elif text:
            raise Exception('Unexpected input text:', text)
        if len(input_words) != len(np_labels):
            raise Exception(' (!) Number of words ('+str(len(input_words))+\
                            ') does not match number of labels '+str(len(np_labels)))

        # 2) Extract phrases from input words:
        phrases = []
        for i, word in enumerate(input_words):
            label = np_labels[i]
            if label == 'B':
                phrases.append([])
            if label in ['B', 'I']:
                phrases[-1].append( word )
        return phrases


    def get_phrase_texts(self, text, np_labels):
        ''' Given a Text, and a list describing text annotations in the 
            B-I-O format (*np_label*), extracts phrases and returns as a
            list of phrase texts;
            
            Assumes that the input is same as the input acceptable for 
            the method NounPhraseChunker.get_phrases();
            
            Returns
            -------
            list of string
                Returns a list of phrase texts;
        '''
        phrases = self.get_phrases(text, np_labels)
        texts = []
        for phrase in phrases:
            phrase_str = ' '.join([word[TEXT] for word in phrase])
            texts.append( phrase_str )
        return texts

    # ===========================================================
    #   Annotate Text for NPs
    # ===========================================================

    def annotateText(self, text, layer, np_labels = None):
        ''' Applies this chunker on given Text, and adds results of 
            the chunking as a new annotation layer to the text.
            If the NP annotations are provided (via the input list 
            *np_labels*), uses the given NP annotations, otherwise 
            produces new NP_LABEL annotations via the method 
            self.analyze_text();
            
            Parameters
            ----------
            text:  estnltk.text.Text
                The input text where the new layer of NP chunking 
                annotations is to be added;
            layer: str
                Name of the new layer;
            np_labels : list of str
                Optional: A list of strings, containing a B-I-O label 
                for each word in *text*; If provided, uses annotations
                from *np_labels*, otherwise creates new annotations 
                with this chunker;
                
            Returns
            -------
            text
                The input text where a new layer (containing NP 
                annotations) has been added;
        ''' 
        input_words = None
        if isinstance(text, Text):
            # input is Text
            input_words = text.words
        else:
            raise Exception(' Input text should be of type Text, but it is ', text)
        phrases = []
        #  If NP_LABEL-s are not provided, text needs to be analyzed first:
        if not np_labels:
            np_labels = self.analyze_text( text, return_type="labels" )
        if len(input_words) != len(np_labels):
            raise Exception(' (!) Number of words ('+str(len(input_words))+\
                            ') does not match number of labels '+str(len(np_labels)))
        #  Fetch NP chunks
        phrases = self.get_phrases( text, np_labels )
        # Create and attach annotations to the Text object
        annotations = []
        if phrases:
            for phrase in phrases: 
                phrase_annotation = {}
                phrase_annotation[START] = phrase[0][START]
                phrase_annotation[END]   = phrase[-1][END]
                phrase_annotation[TEXT]  = ' '.join([word[TEXT] for word in phrase ])
                annotations.append( phrase_annotation )
        text[layer] = annotations
        return text


    # ===========================================================
    #   Debugging stuff
    # ===========================================================
    
    def __debug_get_text_snippet(self, sentence, fromIndex, toIndex):
        minIndex = max(fromIndex, 0)
        maxIndex = min(toIndex, len(sentence)-1)
        if minIndex == maxIndex:
            return sentence[minIndex][TEXT]
        elif minIndex < maxIndex:
            return ' '.join([sentence[k][TEXT] for k in range(minIndex, maxIndex+1)])
        else:
            return ''

    def __debug_extract_NP_from_pos(self, sentence, np_labels, minpos, maxpos, context = 2):
        if 0 <= minpos and minpos <= maxpos and maxpos < len(sentence):
            text = []
            j = minpos
            while (j <= maxpos):
                if np_labels[j] == 'B':
                    text.append('['+sentence[j][TEXT])
                else:
                    text.append( sentence[j][TEXT])  
                if j+1 < len(sentence) and np_labels[j+1] in ['B', ''] and np_labels[j] in ['B', 'I']:
                    text[-1] += ']'
                elif j+1 == len(sentence) and np_labels[j] in ['B', 'I']:
                    text[-1] += ']'
                j+=1
            text = ' '.join(text)
            pre  = self.__debug_get_text_snippet(sentence, minpos-context, minpos-1)
            text = pre+' '+text
            post = self.__debug_get_text_snippet(sentence, maxpos+1, maxpos+context)
            text = text+' '+post
            return text
        return ''

