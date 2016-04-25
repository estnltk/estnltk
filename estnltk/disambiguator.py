# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .names import *
from .text import Text
from .vabamorf.morf import disambiguate
import re


# A hack for defining a string type common in Py 2 and Py 3
try:
    # Check whether basestring is supported (should be in Py 2.7)
    basestring
except NameError as e:
    # If not supported (in Py 3.x), redefine it as str
    basestring = str


class Disambiguator(object):
    """ Class for merging together different morphological disambiguation steps:
        *) pre-disambiguation of proper names based on lemma counts in the corpus;
        *) vabamorf's statistical disambiguation;
        *) post-disambiguation of analyses based on lemma counts in the corpus;
    """
    
    def disambiguate(self, docs, **kwargs):
        """ Performs morphological analysis along with different morphological 
            disambiguation steps (pre-disambiguation, vabamorf's disambiguation
            and post-disambiguation) in the input document collection `docs`.
        
        Note
        ----
             It is assumed that the documents in the input document collection `docs`
            have some similarities, e.g. they are parts of the same story, they are 
            on the same topic etc., so that morphologically ambiguous words (for 
            example: proper names) reoccur in different parts of the collection. 
            The information about reoccurring ambiguous words is then used in 
            pre-disambiguation and post-disambiguation steps for improving the overall
            quality of morphological disambiguation.
            
             Additionally, the input collection `docs` can have two levels: it can be
            list of list of estnltk.text.Text . For example, if we have a corpus of
            daily newspaper issues from one month, and each issue consists of articles
            (published on a single day), we can place the issues to the outer list, 
            and the articles of the issues to the inner lists. 
        
        Parameters
        ----------
        docs: list of estnltk.text.Text
              List of texts (documents) in which the morphological disambiguation
              is performed. Additionally, the list can have two levels: it can be
              list of list of estnltk.text.Text (this can improve quality of the
              post-disambiguation);
        post_disambiguate : boolean, optional
              Applies the lemma-based post-disambiguation on the collection. 
              Default: True;
        disambiguate : boolean, optional
              Applies vabamorf's statistical disambiguation on the collection. 
              Default: True;
              Note: this step shouldn't be turned off, unless for testing purposes;
        pre_disambiguate : boolean, optional
              Applies the pre-disambiguation of proper names on the collection. 
              Default: True;
        vabamorf : boolean, optional
              Applies vabamorf's morphological analyzer on the collection. 
              Default: True;
              Note: this step shouldn't be turned off, unless for testing purposes.
              
        Returns
        -------
        list of estnltk.text.Text
          List of morphologically disambiguated texts (documents). Preserves the
          structure, if the input was  list of list of estnltk.text.Text;
          
        """
        # For testing purposes, morph analysis and morph disambiguation can both
        # be switched off:
        use_vabamorf              = kwargs.get('vabamorf', True)
        use_vabamorf_disambiguate = kwargs.get('disambiguate', True)
        # Configuration for pre- and post disambiguation:
        use_pre_disambiguation    = kwargs.get('pre_disambiguate', True)
        use_post_disambiguation   = kwargs.get('post_disambiguate', True)

        kwargs = kwargs
        # Inner/default configuration for text objects:
        kwargs['disambiguate'] = False # do not use vabamorf disambiguation at first place
        kwargs['guess']        = True  # should be set for the morph analyzer
        kwargs['propername']   = True  # should be set for the morph analyzer
        
        # Check, whether the input is a list of lists of docs, or just a list of docs
        if not self.__isListOfLists( docs ):
            if not self.__isListOfTexts( docs ):
                raise Exception("Unexpected input argument 'docs': should be a list of strings or Text-s;")
            collections = [ docs ]
        else:
            collections = docs
        
        #  I. perform morphological analysis, pre_disambiguation, and 
        #     statistical (vabamorf) disambiguation with-in a single 
        #     document collection;
        for i in range(len(collections)):
            docs = [Text(doc, **kwargs) for doc in collections[i]]

            # morf.analysis without disambiguation
            if use_vabamorf:
                docs = [doc.tag_analysis() for doc in docs]

            if use_pre_disambiguation:
                docs = self.pre_disambiguate(docs)

            if use_vabamorf_disambiguate:
                docs = self.__vabamorf_disambiguate(docs)
            
            collections[i] = docs

        #
        #  II. perform post disambiguation over all document collections;
        #
        if use_post_disambiguation:
           collections = self.post_disambiguate( collections )
        return collections if len(collections)>1 else collections[0]


    def __vabamorf_disambiguate(self, docs):
        for doc in docs:
            sentences = doc.divide()
            for sentence in sentences:
                disambiguated = disambiguate(sentence)
                # replace the analysis
                for orig, new in zip(sentence, disambiguated):
                    orig[ANALYSIS] = new[ANALYSIS]
        return docs


    def __isListOfTexts(self, docs):
        """ Checks whether the input is a list of strings or Text-s; 
        """
        return isinstance(docs, list) and \
               all(isinstance(d, (basestring, Text)) for d in docs)


    def __isListOfLists(self, docs):
        """ Checks whether the input is a list of list of strings/Text-s; 
        """
        return isinstance(docs, list) and \
               all(self.__isListOfTexts(ds) for ds in docs)


    # =========================================================
    # =========================================================
    #     Korpusepõhine pärisnimede eelühestamine 
    #     ( corpus-based pre-disambiguation of proper names )
    #
    #     Algne algoritm ja teostus:  Heiki-Jaan Kaalep
    #     Python-i implementatsioon:  Siim Orasmaa
    # =========================================================
    # =========================================================

    def __create_proper_names_lexicon(self, docs):
        """ Moodustab dokumendikollektsiooni põhjal pärisnimede sagedussõnastiku
            (mis kirjeldab, mitu korda iga pärisnimelemma esines);
        """
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
        """ Teeme esmase yleliigsete analyyside kustutamise: kui sõnal on mitu 
            erineva sagedusega pärisnimeanalüüsi, siis jätame alles vaid
            suurima sagedusega analyysi(d) ...
        """
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
        """ Moodustame kindlate pärisnimede loendi: vaatame sõnu, millel ongi
            ainult pärisnimeanalüüsid ning võtame sealt loendisse  unikaalsed
            pärisnimed;
        """
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
        """ Moodustame lausealguliste pärisnimede loendi: vaatame sõnu, millel nii
            pärisnimeanalüüs(id) kui ka mittepärisnimeanalüüs(id) ning mis esinevad 
            lause või nummerdatud loendi alguses - jäädvustame selliste sõnade 
            unikaalsed lemmad;
        """
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
        """ Moodustame lausesiseste pärisnimede loendi: vaatame sõnu, millel on 
            pärisnimeanalüüse ning mis esinevad lause keskel (st ei esine lause
            alguses või nummerdatud loendi alguses vms);
        """
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
        """ Eemaldame yleliigsed pärisnimeanalüüsid etteantud sõnalemmade
            loendi (hulga) põhjal;
        """
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
        """ Kustutame üleliigsed mitte-pärisnimeanalüüsid: 
            -- kui lause keskel on pärisnimeanalüüsiga sõna, jätamegi alles vaid
               pärisnimeanalyys(id);
            -- kui lause alguses on pärisnimeanalüüsiga s6na, ning pärisnimelemma
               esineb korpuses suurema sagedusega kui 1, jätamegi alles vaid
               pärisnimeanalyys(id); vastasel juhul ei kustuta midagi;
        """
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
        """  Teostab pärisnimede eelühestamine. Üldiseks eesmärgiks on vähendada mitmesust 
             suurtähega algavate sonade morf analüüsil, nt eemaldada pärisnime analüüs, kui
             suurtäht tähistab tõenäoliselt lausealgust.
        """
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
    #    Lemmade-põhine järelühestamine korpusele
    #    ( lemma-based post-disambiguation for the corpus )
    #
    #     Algne algoritm ja teostus:  Heiki-Jaan Kaalep
    #     Python-i implementatsioon:  Siim Orasmaa
    # =========================================================
    # =========================================================

    def __analyses_match(self, analysisA, analysisB):
        """ Leiame, kas tegu on duplikaatidega ehk täpselt üht ja sama
            morfoloogilist infot sisaldavate analüüsidega. """
        return POSTAG in analysisA and POSTAG in analysisB and \
               analysisA[POSTAG]==analysisB[POSTAG] and \
               ROOT in analysisA and ROOT in analysisB and \
               analysisA[ROOT]==analysisB[ROOT] and \
               FORM in analysisA and FORM in analysisB and \
               analysisA[FORM]==analysisB[FORM] and \
               CLITIC in analysisA and CLITIC in analysisB and \
               analysisA[CLITIC]==analysisB[CLITIC] and \
               ENDING in analysisA and ENDING in analysisB and \
               analysisA[ENDING]==analysisB[ENDING]


    def __remove_duplicate_and_problematic_analyses(self, docs):
        """ 1) Eemaldab sisendkorpuse kõigi sõnade morf analüüsidest duplikaadid 
               ehk siis korduvad analüüsid; Nt sõna 'palk' saab kaks analyysi: 
               'palk' (mis käändub 'palk\palgi') ja 'palk' (mis käändub 'palk\palga'),
               aga pärast duplikaatide eemaldamist jääb alles vaid üks;
            2) Kui verbi analüüside hulgas on alles nii '-tama' kui ka '-ma', siis
               jätta alles vaid '-ma' analüüsid;
        """
        for doc in docs:
            for word in doc[WORDS]:
                # 1) Leiame k6ik analyysi-duplikaadid (kui neid on)
                toDelete = []
                for i in range(len(word[ANALYSIS])):
                    if i+1 < len(word[ANALYSIS]):
                        for j in range(i+1, len(word[ANALYSIS])):
                            analysisI = word[ANALYSIS][i]
                            analysisJ = word[ANALYSIS][j]
                            if self.__analyses_match(analysisI, analysisJ):
                                if j not in toDelete:
                                    toDelete.append(j)
                # 2) Kustutame yleliigsed analyysid
                if toDelete:
                    for a in sorted(toDelete, reverse=True):
                        del word[ANALYSIS][a]
                #
                # *) Kui verbi analüüside puhul on olemas nii '-tama' kui ka '-ma' 
                #    lõpp, siis jätta alles vaid -ma, ülejäänud kustutada;
                #    Nt   lõpetama:    lõp+tama,   lõppe+tama,  lõpeta+ma
                #         teatama:     tead+tama,  teata+ma
                #
                if any([ a[POSTAG]=='V' and a[ENDING]=='tama' for a in word[ANALYSIS] ]) and \
                   any([ a[POSTAG]=='V' and a[ENDING]=='ma' for a in word[ANALYSIS] ]):
                    toDelete = []
                    for a in range( len(word[ANALYSIS]) ):
                        if word[ANALYSIS][a][POSTAG]=='V' and \
                           word[ANALYSIS][a][ENDING]=='tama':
                            toDelete.append(a)
                    if toDelete:
                        for a in sorted(toDelete, reverse=True):
                            del word[ANALYSIS][a]


    def __find_hidden_analyses(self, docs):
        """ Jätab meelde, millised analüüsid on nn peidetud ehk siis mida ei 
            tule arvestada lemmade järelühestamisel:
             *) kesksõnade nud, dud, tud mitmesused; 
             *) muutumatute sõnade sõnaliigi mitmesus;
             *) oleviku 'olema' mitmesus ('nad on' vs 'ta on');
             *) asesõnade ainsuse-mitmuse mitmesus;
             *) arv- ja asesõnade vaheline mitmesus; 
            Tagastab sõnastiku peidetud analüüse sisaldanud sõnade asukohtadega, 
            iga võti kujul (doc_index, word_index); """
        hidden = dict()
        nudTudLopud = re.compile('^.*[ntd]ud$')
        for d in range(len(docs)):
            for w in range(len(docs[d][WORDS])):
                word = docs[d][WORDS][w]
                if ANALYSIS in word and len(word[ANALYSIS]) > 1:
                    #
                    # 1) Kui enamus analüüse on nud/tud/dud analüüsid, peida mitmesus:
                    #    kõla+nud //_V_ nud, //    kõla=nud+0 //_A_ //    kõla=nud+0 //_A_ sg n, //    kõla=nud+d //_A_ pl n, //
                    nudTud = [ nudTudLopud.match(a[ROOT]) != None or \
                               nudTudLopud.match(a[ENDING]) != None \
                               for a in word[ANALYSIS] ]
                    if nudTud.count( True ) > 1:
                        hidden[(d, w)] = 1
                    #
                    # 2) Kui analyysidel on sama lemma ja puudub vormitunnus, siis peida mitmesused ära:
                    #    Nt    kui+0 //_D_ //    kui+0 //_J_ //
                    #          nagu+0 //_D_ //    nagu+0 //_J_ //
                    lemmas = set([ a[ROOT] for a in word[ANALYSIS] ])
                    forms  = set([ a[FORM] for a in word[ANALYSIS] ])
                    if len(lemmas) == 1 and len(forms) == 1 and (list(forms))[0] == '':
                        hidden[(d, w)] = 1
                    #
                    # 3) Kui 'olema'-analyysidel on sama lemma ning sama l6pp, peida mitmesused:
                    #    Nt  'nad on' vs 'ta on' saavad sama olema-analyysi, mis jääb mitmeseks;
                    endings  = set([ a[ENDING] for a in word[ANALYSIS] ])
                    if len(lemmas) == 1 and (list(lemmas))[0] == 'ole' and len(endings) == 1 \
                       and (list(endings))[0] == '0':
                        hidden[(d, w)] = 1
                    #
                    # 4) Kui asesõnadel on sama lemma ja lõpp, peida ainsuse/mitmuse mitmesus:
                    #    Nt     kõik+0 //_P_ sg n //    kõik+0 //_P_ pl n //
                    #           kes+0 //_P_ sg n //    kes+0 //_P_ pl n //
                    postags  = set([ a[POSTAG] for a in word[ANALYSIS] ])
                    if len(lemmas) == 1 and len(postags) == 1 and 'P' in postags and \
                       len(endings) == 1:
                        hidden[(d, w)] = 1
                    #
                    # 5) Kui on sama lemma ja lõpp, peida arv- ja asesõnadevaheline mitmesus:
                    #    Nt     teine+0 //_O_ pl n, //    teine+0 //_P_ pl n, //
                    #           üks+l //_N_ sg ad, //    üks+l //_P_ sg ad, //
                    if len(lemmas) == 1 and 'P' in postags and ('O' in postags or \
                       'N' in postags) and len(endings) == 1:
                        hidden[(d, w)] = 1
        return hidden


    def __supplement_lemma_frequency_lexicon(self, docs, hiddenWords, lexicon, amb_lexicon):
        """ Täiendab etteantud sagedusleksikone antud korpuse (docs) põhjal:
            *) yldist sagedusleksikoni, kus on k6ik lemmad, v.a. lemmad, 
               mis kuuluvad nn peidetud sõnade hulka (hiddenWords); 
            *) mitmeste sagedusleksikoni, kus on vaid mitmeste analyysidega
               s6nades esinenud lemmad, v.a. (hiddenWords) lemmad, koos
               nende yldiste esinemissagedustega (esimesest leksikonist);
        """
        for d in range(len(docs)):
            for w in range(len(docs[d][WORDS])):
                word = docs[d][WORDS][w]
                # Jätame vahele nn peidetud sõnad
                if (d, w) in hiddenWords:
                    continue
                isAmbiguous = (len(word[ANALYSIS])>1)
                # Jäädvustame sagedused, verbide omad eraldiseisva märkega:
                for a in word[ANALYSIS]:
                    lemma = a[ROOT]+'ma' if a[POSTAG]=='V' else a[ROOT]
                    # 1) Jäädvustame üldise sageduse
                    if lemma not in lexicon:
                        lexicon[lemma] = 1
                    else:
                        lexicon[lemma] += 1
                    # 2) Jäädvustame mitmeste sõnade esinemise
                    if isAmbiguous:
                        amb_lexicon[lemma] = 1
        #  Kanname yldisest sagedusleksikonist sagedused yle mitmeste lemmade
        # sagedusleksikoni
        for lemma in amb_lexicon.keys():
            amb_lexicon[lemma] = lexicon[lemma]


    def __disambiguate_with_lexicon(self, docs, lexicon, hiddenWords):
        """ Teostab lemmade leksikoni järgi mitmeste morf analüüside 
            ühestamise - eemaldab üleliigsed analüüsid;
            Toetub ideele "üks tähendus teksti kohta": kui mitmeseks jäänud 
            lemma esineb tekstis/korpuses ka mujal ning lõppkokkuvõttes 
            esineb sagedamini kui alternatiivsed analüüsid, siis tõenäoliselt
            see ongi õige lemma/analüüs;
        """
        for d in range(len(docs)):
            for w in range(len(docs[d][WORDS])):
                word = docs[d][WORDS][w]
                # Jätame vahele nn peidetud sõnad
                if (d, w) in hiddenWords:
                    continue
                # Vaatame vaid mitmeseks jäänud analüüsidega sõnu
                if len(word[ANALYSIS]) > 1:
                    #  1) Leiame suurima esinemissageduse mitmeste lemmade seas
                    highestFreq = 0
                    for analysis in word[ANALYSIS]:
                        lemma = analysis[ROOT]+'ma' if analysis[POSTAG]=='V' else analysis[ROOT]
                        if lemma in lexicon and lexicon[lemma] > highestFreq:
                            highestFreq = lexicon[lemma]
                    if highestFreq > 0:
                        #  2) Jätame välja kõik analüüsid, mille lemma esinemissagedus
                        #     on väiksem kui suurim esinemissagedus;
                        toDelete = []
                        for analysis in word[ANALYSIS]:
                            lemma = analysis[ROOT]+'ma' if analysis[POSTAG]=='V' else analysis[ROOT]
                            freq = lexicon[lemma] if lemma in lexicon else 0
                            if freq < highestFreq:
                                toDelete.append(analysis)
                        for analysis in toDelete:
                            word[ANALYSIS].remove(analysis)


    def post_disambiguate(self, collections):
        """  Teostab mitmeste analüüside lemma-põhise järelühestamise. Järelühestamine 
            toimub kahes etapis: kõigepealt ühe dokumendikollektsiooni piires ning 
            seejärel üle kõigi dokumendikollektsioonide (kui sisendis on rohkem kui 1
            dokumendikollektsioon);
             Sisuliselt kasutatakse ühestamisel "üks tähendus teksti kohta" idee laiendust:
            kui mitmeseks jäänud lemma esineb ka mujal (samas kollektsioonis või kõigis
            kollektsioonides) ning lõppkokkuvõttes esineb sagedamini kui alternatiivsed
            analüüsid, siis tõenäoliselt see ongi õige lemma/analüüs;
        """
        #
        #  I etapp: ühestame ühe dokumendikollektsiooni piires 
        #           (nt üle kõigi samal päeval ilmunud ajaleheartiklite);
        #
        for docs in collections:
            # 1) Eemaldame analüüside seast duplikaadid ja probleemsed
            self.__remove_duplicate_and_problematic_analyses(docs)
            # 2) Leiame sõnad, mis sisaldavad nn ignoreeritavaid mitmesusi
            #    (selliseid mitmesusi, mida me ühestamisel ei arvesta);
            hiddenWords = self.__find_hidden_analyses(docs)
            # 3) Leiame kaks lemmade sagedusleksikoni: üldise lemmade sagedus-
            #    leksikoni ja mitmeseks jäänud sonade lemmade sagedusleksikoni;
            #    Mitmeste lemmade leksikoni läheb kirja vastavate lemmade yldine 
            #    sagedus korpuses (kuhu arvatud ka sagedus ühestatud sõnades);
            genLemmaLex = dict()
            ambLemmaLex = dict()
            self.__supplement_lemma_frequency_lexicon(docs, hiddenWords, ambLemmaLex, genLemmaLex)
            # 4) Teostame lemmade-p6hise yhestamise: mitmeseks j22nud analyyside 
            #    puhul j2tame alles analyysid, mille lemma esinemisagedus on suurim
            #    (ja kui k6igi esinemissagedus on v6rdne, siis ei tee midagi)
            self.__disambiguate_with_lexicon(docs, ambLemmaLex, hiddenWords)
        #
        #  II etapp: ühestame üle kõikide dokumendikollektsioonide 
        #            (nt üle kõigi ühe aasta ajalehenumbrite, kus
        #             üks ajalehenumber sisaldab kõiki sama päeva artikleid);
        #
        if len(collections) > 1:
            # Genereerime mitmeste sagedusleksikoni
            genLemmaLex = dict()
            ambLemmaLex = dict()
            for docs in collections:
                # *) Leiame sõnad, mis sisaldavad nn ignoreeritavaid mitmesusi
                hiddenWords = self.__find_hidden_analyses(docs)
                # *) Täiendame üldist lemmade sagedusleksikoni ja mitmeseks jäänud
                #    lemmade sagedusleksikoni;
                self.__supplement_lemma_frequency_lexicon(docs, hiddenWords, ambLemmaLex, genLemmaLex)
            # Teostame järelühestamise
            for docs in collections:
                # *) Leiame sõnad, mis sisaldavad nn ignoreeritavaid mitmesusi
                hiddenWords = self.__find_hidden_analyses(docs)
                # *) Teostame lemmade-p6hise yhestamise;
                self.__disambiguate_with_lexicon(docs, ambLemmaLex, hiddenWords)
        return collections

