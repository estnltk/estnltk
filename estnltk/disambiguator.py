# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .names import *
from .text import Text

import re

class Disambiguator(object):

    def disambiguate(self, docs, **kwargs):
        # convert input
        kwargs = kwargs
        kwargs['disambiguate'] = False # do not use disambiguation right now
        kwargs['guess']      = True  # should be set for the morph analyzer
        kwargs['propername'] = True  # should be set for the morph analyzer
        
        use_pre_disambiguation    = kwargs.get('pre_disambiguate', True)
        use_post_disambiguation   = kwargs.get('post_disambiguate', True)
        # For testing purposes, vabamorf disambiguation can also be switched off:
        use_vabamorf_disambiguate = kwargs.get('vabamorf_disambiguate', True)
        
        docs = [Text(doc, **kwargs) for doc in docs]

        # morf.analysis without disambiguation
        docs = [doc.tag_analysis() for doc in docs]

        if use_pre_disambiguation:
            docs = self.pre_disambiguate(docs)

        if use_vabamorf_disambiguate:
            docs = self.__vabamorf_disambiguate(docs)

        if use_post_disambiguation:
            docs = self.post_disambiguate(docs)

        return docs

    def __vabamorf_disambiguate(self, docs):
        # TODO for Timo: extract vabamorf disambiguator from analyzer and apply it here
        return docs

    # =========================================================
    # =========================================================
    #     Korpusepõhine pärisnimede eelühestamine 
    #     ( corpus-based pre-disambiguation of proper names )
    # =========================================================
    # =========================================================

    def __create_proper_names_lexicon(self, docs):
        ''' Moodustab dokumendikollektsiooni põhjal pärisnimede sagedussõnastiku
            (mis kirjeldab, mitu korda iga pärisnimelemma esines);
        '''
        lemmaFreq = dict()
        for doc in docs:
            for word in doc[WORDS]:
                # 1) Leiame k6ik s6naga seotud unikaalsed pärisnimelemmad 
                #    (kui neid on)
                uniqLemmas = set()
                for analysis in word[ANALYSIS]:
                    if analysis[POSTAG] == 'H':
                        uniqLemmas.add( analysis[ROOT] )
                # 2) Jäädvustame lemmade sagedused
                for lemma in uniqLemmas:
                    if lemma not in lemmaFreq:
                        lemmaFreq[lemma] = 1
                    else:
                        lemmaFreq[lemma] += 1
        return lemmaFreq


    def __disambiguate_proper_names_1(self, docs, lexicon):
        ''' Teeme esmase yleliigsete analyyside kustutamise: kui sõnal on mitu 
            erineva sagedusega pärisnimeanalüüsi, siis jätame alles vaid
            suurima sagedusega analyysi(d) ...
        '''
        for doc in docs:
            for word in doc[WORDS]:
                # Vaatame vaid s6nu, millele on pakutud rohkem kui yks analyys:
                if len(word[ANALYSIS]) > 1:
                    # 1) Leiame kõigi pärisnimede sagedused sagedusleksikonist
                    highestFreq = 0
                    properNameAnalyses = []
                    for analysis in word[ANALYSIS]:
                        if analysis[POSTAG] == 'H':
                            if analysis[ROOT] in lexicon:
                                properNameAnalyses.append( analysis )
                                if lexicon[analysis[ROOT]] > highestFreq:
                                    highestFreq = lexicon[analysis[ROOT]]
                            else:
                                raise Exception(' Unable to find lemma ',analysis[ROOT], \
                                      ' from the lexicon. ')
                    # 2) J2tame alles vaid suurima lemmasagedusega pärisnimeanalyysid,
                    #    ylejaanud kustutame maha
                    if highestFreq > 0:
                        toDelete = []
                        for analysis in properNameAnalyses:
                            if lexicon[analysis[ROOT]] < highestFreq:
                                toDelete.append(analysis)
                        for analysis in toDelete:
                            word[ANALYSIS].remove(analysis)


    def __find_certain_proper_names(self, docs):
        ''' Moodustame kindlate pärisnimede loendi: vaatame sõnu, millel ongi
            ainult pärisnimeanalüüsid ning võtame sealt loendisse  unikaalsed
            pärisnimed;
        '''
        certainNames = set()
        for doc in docs:
            for word in doc[WORDS]:
                # Vaatame vaid pärisnimeanalüüsidest koosnevaid sõnu
                if all([ a[POSTAG] == 'H' for a in word[ANALYSIS] ]):
                    # Jäädvustame kõik unikaalsed lemmad kui kindlad pärisnimed
                    for analysis in word[ANALYSIS]:
                        certainNames.add( analysis[ROOT] )
        return certainNames


    def __find_sentence_initial_proper_names(self, docs):
        ''' Moodustame lausealguliste pärisnimede loendi: vaatame sõnu, millel nii
            pärisnimeanalüüs(id) kui ka mittepärisnimeanalüüs(id) ning mis esinevad 
            lause või nummerdatud loendi alguses - jäädvustame selliste sõnade 
            unikaalsed lemmad;
        '''
        sentInitialNames = set()
        for doc in docs:
            for sentence in doc.divide( layer=WORDS, by=SENTENCES ): 
                sentencePos = 0 # Tavaline lausealgus
                for i in range(len(sentence)):
                    word = sentence[i]
                    #  Täiendavad heuristikud lausealguspositsioonide leidmiseks:
                    #  1) kirjavahemärk, mis pole koma ega semikoolon, on lausealgus:
                    if all([ a[POSTAG] == 'Z' for a in word[ANALYSIS] ]) and \
                       not re.match('^[,;]+$', word[TEXT]):
                        sentencePos = 0
                        #self.__debug_print_word_in_sentence_str(sentence, word)
                        continue
                    # 2) potentsiaalne loendi algus (arv, millele järgneb punkt või
                    #    sulg ja mis ei ole kuupäev);
                    if not re.match('^[1234567890]*$', word[TEXT] ) and \
                       not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word[TEXT] ) and \
                       re.match("^[1234567890.()]*$", word[TEXT]):
                        sentencePos = 0
                        #self.__debug_print_word_in_sentence_str(sentence, word)
                        continue
                    if sentencePos == 0:
                        # Vaatame lausealgulisi sõnu, millel on nii pärisnimeanalüüs(e) 
                        # kui ka mitte-pärisnimeanalüüs(e)
                        h_postags = [ a[POSTAG] == 'H' for a in word[ANALYSIS] ]
                        if any( h_postags )  and  not all( h_postags ):
                            for analysis in word[ANALYSIS]:
                                # Jätame meelde kõik unikaalsed pärisnimelemmad
                                if analysis[POSTAG] == 'H':
                                    sentInitialNames.add( analysis[ROOT] )
                    sentencePos += 1
        return sentInitialNames


    def __find_sentence_central_proper_names(self, docs):
        ''' Moodustame lausesiseste pärisnimede loendi: vaatame sõnu, millel on 
            pärisnimeanalüüse ning mis esinevad lause keskel (st ei esine lause
            alguses või nummerdatud loendi alguses vms);
        '''
        sentCentralNames = set()
        for doc in docs:
            for sentence in doc.divide( layer=WORDS, by=SENTENCES ): 
                sentencePos = 0 # Tavaline lausealgus
                for i in range(len(sentence)):
                    word = sentence[i]
                    #  Täiendavad heuristikud lausealguspositsioonide leidmiseks:
                    #  1) kirjavahemärk, mis pole koma ega semikoolon, on lausealgus:
                    if all([ a[POSTAG] == 'Z' for a in word[ANALYSIS] ]) and \
                       not re.match('^[,;]+$', word[TEXT]):
                        sentencePos = 0
                        #self.__debug_print_word_in_sentence_str(sentence, word)
                        continue
                    # 2) potentsiaalne loendi algus (arv, millele järgneb punkt või
                    #    sulg ja mis ei ole kuupäev);
                    if not re.match('^[1234567890]*$', word[TEXT] ) and \
                       not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word[TEXT] ) and \
                       re.match("^[1234567890.()]*$", word[TEXT]):
                        sentencePos = 0
                        #self.__debug_print_word_in_sentence_str(sentence, word)
                        continue
                    if sentencePos != 0:
                        # Vaatame lause keskel olevaid sõnu, millel on pärisnimeanalüüs
                        for analysis in word[ANALYSIS]:
                            if analysis[POSTAG] == 'H':
                                # Jätame meelde kõik unikaalsed pärisnimelemmad
                                sentCentralNames.add( analysis[ROOT] )
                                #self.__debug_print_word_in_sentence_str(sentence, word)
                    sentencePos += 1
        return sentCentralNames


    def __remove_redundant_proper_names(self, docs, lemma_set):
        ''' Eemaldame yleliigsed pärisnimeanalüüsid etteantud sõnalemmade
            loendi (hulga) põhjal;
        '''
        for doc in docs:
            for word in doc[WORDS]:
                # Vaatame vaid s6nu, millele on pakutud rohkem kui yks analyys:
                if len(word[ANALYSIS]) > 1:
                    # 1) Leiame analyysid, mis tuleks loendi järgi eemaldada
                    toDelete = []
                    for analysis in word[ANALYSIS]:
                        if analysis[POSTAG] == 'H' and analysis[ROOT] in lemma_set:
                            toDelete.append( analysis )
                    # 2) Eemaldame yleliigsed analyysid
                    if toDelete:
                        for analysis in toDelete:
                            word[ANALYSIS].remove(analysis)


    def __disambiguate_proper_names_2(self, docs, lexicon):
        ''' Kustutame üleliigsed mitte-pärisnimeanalüüsid: 
            -- kui lause keskel on pärisnimeanalüüsiga sõna, jätamegi alles vaid
               pärisnimeanalyys(id);
            -- kui lause alguses on pärisnimeanalüüsiga s6na, ning pärisnimelemma
               esineb korpuses suurema sagedusega kui 1, jätamegi alles vaid
               pärisnimeanalyys(id); vastasel juhul ei kustuta midagi;
        '''
        for doc in docs:
            for sentence in doc.divide( layer=WORDS, by=SENTENCES ): 
                sentencePos = 0 # Tavaline lausealgus
                for i in range(len(sentence)):
                    word = sentence[i]
                    #  Täiendavad heuristikud lausealguspositsioonide leidmiseks:
                    #  1) kirjavahemärk, mis pole koma ega semikoolon, on lausealgus:
                    if all([ a[POSTAG] == 'Z' for a in word[ANALYSIS] ]) and \
                       not re.match('^[,;]+$', word[TEXT]):
                        sentencePos = 0
                        continue
                    #
                    # Vaatame ainult mitmeseid s6nu, mis sisaldavad ka p2risnimeanalyysi
                    #
                    if len(word[ANALYSIS]) > 1 and \
                       any([ a[POSTAG] == 'H' for a in word[ANALYSIS] ]):
                        if sentencePos != 0:
                            # 1) Kui oleme lause keskel, valime alati vaid nimeanalyysid 
                            #    (eeldades, et nyyseks on järgi jäänud vaid korrektsed nimed)
                            toDelete = []
                            for analysis in word[ANALYSIS]:
                                if analysis[POSTAG] not in ['H', 'G']:
                                    toDelete.append( analysis )
                            for analysis in toDelete:
                                word[ANALYSIS].remove(analysis)
                            #if toDelete:
                            #    self.__debug_print_word_in_sentence_str(sentence, word)
                        else:
                            # 2) Kui oleme lause alguses, siis valime ainult nimeanalyysid
                            #    juhul, kui vastav lemma esines ka mujal (st lemma esinemis-
                            #    sagedus on suurem kui 1);
                            # Kas m6ni lemma esineb p2risnimede leksikonis sagedusega > 1 ?
                            hasRecurringProperName = False
                            toDelete = []
                            for analysis in word[ANALYSIS]:
                                if analysis[ROOT] in lexicon and lexicon[analysis[ROOT]] > 1:
                                    hasRecurringProperName = True
                                if analysis[POSTAG] not in ['H', 'G']:
                                    toDelete.append( analysis )
                            if hasRecurringProperName and toDelete:
                                # Kui p2risnimi esines ka mujal, j2tame alles vaid p2risnime-
                                # analyysid:
                                for analysis in toDelete:
                                    word[ANALYSIS].remove(analysis)
                                #self.__debug_print_word_in_sentence_str(sentence, word)
                    sentencePos += 1


    def pre_disambiguate(self, docs):
        '''  Teostab pärisnimede eelühestamine. Üldiseks eesmärgiks on vähendada mitmesust 
             suurtähega algavate sonade morf analüüsil, nt eemaldada pärisnime analüüs, kui
             suurtäht tähistab tõenäoliselt lausealgust.
        '''
        # 1) Leiame pärisnimelemmade sagedusleksikoni
        lexicon = self.__create_proper_names_lexicon(docs)
        # 2) Teeme esialgse kustutamise: kui sõnal on mitu erineva korpuse-
        #    sagedusega pärisnimeanalüüsi, siis jätame alles vaid kõige 
        #    sagedasema analyysi ...
        self.__disambiguate_proper_names_1(docs, lexicon)
        
        # 3) Eemaldame yleliigsed lause alguse pärisnimeanalüüsid;
        #  Kõigepealt leiame: kindlad pärisnimed, lause alguses esinevad 
        #  p2risnimed ja lause keskel esinevad pärisnimed
        certainNames     = self.__find_certain_proper_names(docs)
        sentInitialNames = self.__find_sentence_initial_proper_names(docs)
        sentCentralNames = self.__find_sentence_central_proper_names(docs)
        
        # 3.1) Võrdleme lause alguses ja keskel esinevaid lemmasid: leiame 
        #      lemmad, mis esinesid ainult lause alguses ...
        onlySentenceInitial = sentInitialNames.difference(sentCentralNames)
        # 3.2) Võrdleme ainult lause alguses esinevaid ning kindlaid pärisnime-
        #      lemmasid: kui sõna esines vaid lause alguses ega ole kindel 
        #      pärisnimelemma, pole tõenäoliselt tegu pärisnimega ...
        notProperNames = onlySentenceInitial.difference(certainNames)
        # 3.3) Eemaldame yleliigsed p2risnimeanalyysid (kui selliseid leidus)
        if len(notProperNames) > 0:
            self.__remove_redundant_proper_names(docs, notProperNames)
        
        # 4) Leiame uue pärisnimelemmade sagedusleksikoni (sagedused on 
        #    tõenäoliselt vahepeal muutunud);
        lexicon = self.__create_proper_names_lexicon(docs)
        
        # 5) Teeme üleliigsete mittepärisnimeanalüüside kustutamise sõnadelt,
        #    millel on lisaks pärisnimeanalüüsidele ka teisi analüüse: 
        #    lausealgusesse jätame alles vaid pärisnimeanalüüsid, kui neid 
        #    esineb korpuses ka mujal; 
        #    lause keskele jätame igal juhul alles vaid pärisnimeanalüüsid;
        self.__disambiguate_proper_names_2(docs, lexicon)
        return docs

    # =========================================================
    # =========================================================
    #    Korpusepõhine lemmade järelühestamine 
    #    ( corpus-based post-disambiguation of lemmas )
    # =========================================================
    # =========================================================
    
    def post_disambiguate(self, docs):
        # TODO: sisendiks peaks  docs  asemel olema  list of docs
        # TODO: implementatsioon
        return docs

