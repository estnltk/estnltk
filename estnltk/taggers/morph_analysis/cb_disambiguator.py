#
#  Corpus-based (CB) morphological disambiguator.
#  [ WORK IN PROGRESS ]
#
#  Based on the disambiguator source from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/disambiguator.py
#
#  Idea of the algorithm:     Heiki-Jaan Kaalep
#  Python's implementation:   Siim Orasmaa
#

import re
from collections import defaultdict

from estnltk import Text
from estnltk.layer.ambiguous_span import AmbiguousSpan
from estnltk.layer.span_operations import nested_aligned_left, left

from estnltk.taggers import Retagger

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.morf import VabamorfTagger
from estnltk.taggers.morph_analysis.morf import VabamorfDisambiguator
from estnltk.taggers.morph_analysis.postanalysis_tagger import PostMorphAnalysisTagger

from estnltk.taggers.morph_analysis.recordbased_retagger import MorphAnalysisRecordBasedRetagger


class CorpusBasedMorphDisambiguator( object ):
    """ Disambiguator that performs morphological analysis along with different 
        morphological disambiguation steps -- pre-disambiguation, vabamorf's 
        disambiguation  and  post-disambiguation --  in  the  input  document 
        collection.
        
        In detail, fifferent morphological disambiguation steps are 
        the following:
        *) pre-disambiguation of proper names based on lemma counts 
           in the corpus;
        *) vabamorf's statistical disambiguation;
        *) post-disambiguation of analyses based on lemma counts in 
           the corpus;
    """

    def __init__(self,
                 morph_analysis_layer:str='morph_analysis',
                 input_words_layer:str='words',
                 input_sentences_layer:str='sentences'):
        """Initialize CorpusBasedMorphDisambiguator class.

        Parameters
        ----------
        morph_analysis_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer. 
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        """
        # Set attributes & configuration
        self.input_layers = [ input_words_layer, \
                              input_sentences_layer ]
        self.depends_on   = self.input_layers
        self._input_words_layer     = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self._morph_analysis_layer  = morph_analysis_layer


    def disambiguate(self, docs:list, **kwargs):
        # TODO
        raise NotImplementedError('disambiguate method not implemented in ' + self.__class__.__name__)


    # =========================================================
    # =========================================================
    #     Corpus-based pre-disambiguation of proper names
    # =========================================================
    # =========================================================


    def __create_proper_names_lexicon(self, docs):
        """ Creates a proper name frequency dictionary based on the 
            collection of documents.
            Each entry in the dictionary describes how many times
            given (proper name) lemma appears in the corpus 
            (including ambiguous appearances).
        """
        lemmaFreq = defaultdict(int)
        for doc in docs:
            for word_morph in doc[ self._morph_analysis_layer ]:
                # 1) Find all unique proper name lemmas of
                #    this word 
                uniqLemmas = set()
                for analysis in word_morph:
                    if analysis.partofspeech == 'H':
                        uniqLemmas.add( analysis.root )
                # 2) Record lemma frequencies
                for lemma in uniqLemmas:
                    lemmaFreq[lemma] += 1
        return lemmaFreq


    def __disambiguate_proper_names_1(self, docs, lexicon):
        """ Step 1 in removal of redundant proper names analyses: 
            if a word has multiple proper name analyses with different 
            frequencies, keep only the analysis that has the highest
            frequency.
        """
        disamb_retagger = ProperNamesDisambiguationStep1Retagger(lexicon,\
                          morph_analysis_layer=self._morph_analysis_layer)
        for doc in docs:
            disamb_retagger.retag( doc )


    def __find_certain_proper_names(self, docs):
        """ Creates the list of certain proper names: finds words that 
            only have proper name analyses and, gathers all unique proper 
            name lemmas from there;
        """
        certainNames = set()
        for doc in docs:
            for word_morph in doc[ self._morph_analysis_layer ]:
                # Check if word only has proper name analyses
                if all([ a.partofspeech == 'H' for a in word_morph ]):
                    # If so, record its lemmas as "certain proper name lemmas"
                    for analysis in word_morph:
                        certainNames.add( analysis.root )
        return certainNames


    def __find_sentence_initial_proper_names(self, docs):
        """ Creates the list of sentence-initial proper names.
            Finds words that have ambiguities between proper name and 
            regular analyses, and that are in the beginning of sentence, 
            or of an enumeration. Records and returns proper name lemmas 
            of such words;
        """
        sentInitialNames = set()
        for doc in docs:
            sentences = doc[ self._input_sentences_layer ]
            sentence_id = 0
            nextSentenceInitialPosition = -1
            morph_analysis = doc[ self._morph_analysis_layer ]
            for wid, word_morph in enumerate( morph_analysis ):
                current_sentence = sentences[sentence_id]
                # Check if the word is in sentence-initial position:
                # 1) word in the beginning of annotated sentence
                if current_sentence.start == word_morph.start:
                    nextSentenceInitialPosition = wid
                # 2) punctuation that is not comma neither semicolon, 
                #    is before a sentence-initial position
                elif all([ a.partofspeech == 'Z' for a in word_morph ]) and \
                   not re.match('^[,;]+$', word_morph.text):
                    nextSentenceInitialPosition = wid + 1
                # 3) beginning of an enumeration (a number that does not look 
                #    like a date, and is followed by a period or a parenthesis),
                elif not re.match('^[1234567890]*$', word_morph.text ) and \
                   not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word_morph.text ) and \
                   re.match("^[1234567890.()]*$", word_morph.text ):
                    nextSentenceInitialPosition = wid + 1
                # If we are in an sentence-initial position
                if wid == nextSentenceInitialPosition:
                    # Consider sentence-initial words that have both proper name 
                    # analyses, and also regular (not proper name) analyses
                    h_postags = [ a.partofspeech == 'H' for a in word_morph ]
                    if any( h_postags ) and not all( h_postags ):
                        for analysis in word_morph:
                            # Memorize all unique proper name lemmas
                            if analysis.partofspeech == 'H':
                                sentInitialNames.add( analysis.root )
                # Take the next sentence
                if current_sentence.end == word_morph.end:
                    sentence_id += 1
            assert sentence_id == len(sentences)
        return sentInitialNames


    def __find_sentence_central_proper_names(self, docs):
        """ Creates the list of sentence-central proper names.
            Finds words that have ambiguities between proper name and 
            regular analyses, and that in central position of the 
            sentence. Records and returns proper name lemmas of 
            such words;
        """
        sentCentralNames = set()
        for doc in docs:
            sentences = doc[ self._input_sentences_layer ]
            sentence_id = 0
            nextSentenceInitialPosition = -1
            morph_analysis = doc[ self._morph_analysis_layer ]
            for wid, word_morph in enumerate( morph_analysis ):
                current_sentence = sentences[sentence_id]
                # Check if the word is in sentence-initial position:
                # 1) word in the beginning of annotated sentence
                if current_sentence.start == word_morph.start:
                    nextSentenceInitialPosition = wid
                # 2) punctuation that is not comma neither semicolon, 
                #    is before a sentence-initial position
                elif all([ a.partofspeech == 'Z' for a in word_morph ]) and \
                   not re.match('^[,;]+$', word_morph.text):
                    nextSentenceInitialPosition = wid + 1
                # 3) beginning of an enumeration (a number that does not look 
                #    like a date, and is followed by a period or a parenthesis),
                elif not re.match('^[1234567890]*$', word_morph.text ) and \
                   not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word_morph.text ) and \
                   re.match("^[1234567890.()]*$", word_morph.text ):
                    nextSentenceInitialPosition = wid + 1
                # Assume: if the word is not on a sentence-initial position,
                #         it must be on a sentence-central position;
                if wid != nextSentenceInitialPosition:
                    # Consider sentence-central words that have proper name 
                    # analyses
                    for analysis in word_morph:
                        # Memorize all unique proper name lemmas
                        if analysis.partofspeech == 'H':
                            sentCentralNames.add( analysis.root )
                # Take the next sentence
                if current_sentence.end == word_morph.end:
                    sentence_id += 1
            assert sentence_id == len(sentences)
        return sentCentralNames


    def __remove_redundant_proper_names(self, docs, notProperNames):
        """ Step 2 in removal of redundant proper names analyses: 
            if a word has  multiple  analyses, and  some  of  these 
            are in the lexicon notProperNames, then delete analyses 
            appearing in the lexicon.
         """
        disamb_retagger = ProperNamesDisambiguationStep2Retagger(notProperNames,\
                          morph_analysis_layer=self._morph_analysis_layer)
        for doc in docs:
            disamb_retagger.retag( doc )


    def __disambiguate_proper_names_2(self, docs, lexicon):
        """ Step 3 in removal of redundant proper names analyses: 
            -- in case of sentence-central ambiguous proper names, keep 
               only proper name analyses;
            -- in case of sentence-initial ambiguous proper names: if the 
               proper name has corpus frequency greater than 1, then keep 
               only proper name analyses. 
               Otherwise, leave analyses intact;
         """
        disamb_retagger = ProperNamesDisambiguationStep3Retagger(lexicon,\
                          morph_analysis_layer=self._morph_analysis_layer)
        for doc in docs:
            disamb_retagger.retag( doc )


    def _test_predisambiguation(self, docs):  # Only for testing purposes
        # 1) Find frequencies of proper name lemmas
        lexicon = self.__create_proper_names_lexicon( docs )
        # 2) First disambiguation: if a word has multiple proper name
        #    analyses with different frequencies, keep only the analysis
        #    with the highest corpus frequency ...
        self.__disambiguate_proper_names_1( docs, lexicon )
        # 3) Find certain proper names, sentence-initial proper names,
        #    and sentence-central proper names 
        certainNames     = self.__find_certain_proper_names(docs)
        sentInitialNames = self.__find_sentence_initial_proper_names(docs)
        sentCentralNames = self.__find_sentence_central_proper_names(docs)
        
        # 3.1) Find names only sentence initial, not sentence central
        onlySentenceInitial = sentInitialNames.difference(sentCentralNames)
        # 3.2) From names that are exclusively sentence initial, extract
        #      names that are not certain names (by lexicon);
        #      The remaining names are moste unlikely candidates for 
        #      proper names;
        notProperNames = onlySentenceInitial.difference(certainNames)
        # 3.3) Second disambiguation: remove sentence initial proper names
        #      that are most likely false positives
        self.__remove_redundant_proper_names(docs, notProperNames)
        #print( lexicon )
        #print( certainNames )
        #print( 'sentInitial->',sentInitialNames )
        #print( 'sentCentral->',sentCentralNames )
        #print( 'notProperNames->', notProperNames )
        
        # 4) Find frequencies of proper name lemmas once again
        #    ( taking account that frequencies may have been changed )
        lexicon = self.__create_proper_names_lexicon( docs )
        #print( lexicon )
        
        # 5) Remove redundant proper name analyses from words 
        #    that are ambiguous between proper name analyses 
        #    and regular analyses:
        #    -- in case of sentence-central ambiguous proper names, 
        #       keep only proper name analyses;
        #    -- in case of sentence-initial ambiguous proper names: 
        #       if the proper name has corpus frequency greater than
        #       1, then keep only proper name analyses. 
        #       Otherwise, leave analyses intact;
        self.__disambiguate_proper_names_2(docs, lexicon)
        
        
    
    
    # =========================================================
    # =========================================================
    #     Object representation
    # =========================================================
    # =========================================================
    
    def __repr__(self):
        # TODO
        raise NotImplementedError('__repr__ method not implemented in ' + self.__class__.__name__)

    def _repr_html_(self):
        # TODO
        raise NotImplementedError('_repr_html_ method not implemented in ' + self.__class__.__name__)


class ProperNamesDisambiguationStep1Retagger(MorphAnalysisRecordBasedRetagger):
    """ First Retagger for removal of redundant proper names analyses.
        If a word has multiple proper name analyses with different 
        frequencies, keeps only the analysis that has the highest
        frequency.
    """
    def __init__(self, lexicon:dict, \
                       morph_analysis_layer:str='morph_analysis'):
        super().__init__( morph_analysis_layer=morph_analysis_layer )
        self.conf_param.append('_lexicon')
        self._lexicon = lexicon

    def rewrite_words(self, words:list):
        changed_words = set()
        for wid, word_analyses in enumerate( words ):
            changed = False
            if len(word_analyses) > 1: # Only consider words that have more than 1 analysis
                # 1) Collect all proper name analyses of the word, and 
                #    get their highest frequency based on the the freq lexicon
                highestFreq = 0
                properNameAnalyses = []
                for analysis in word_analyses:
                    if analysis['partofspeech'] == 'H':
                        if analysis['root'] in self._lexicon:
                            properNameAnalyses.append( analysis )
                            if self._lexicon[analysis['root']] > highestFreq:
                                highestFreq = self._lexicon[analysis['root']]
                        else:
                            raise Exception( \
                                '(!) Unable to find lemma {!r} from the lexicon.'.format(analysis['root']) )
                # 2) Keep only those proper name analyses that have the highest
                #    frequency (in the corpus), delete all others
                if highestFreq > 0:
                    toDelete = []
                    for analysis in properNameAnalyses:
                        if self._lexicon[analysis['root']] < highestFreq:
                            toDelete.append(analysis)
                    for analysis in toDelete:
                        word_analyses.remove(analysis)
                        changed = True
            if changed:
                # Keep track of changed words (for optimization purposes)
                changed_words.add( wid )
        return words, changed_words


class ProperNamesDisambiguationStep2Retagger(MorphAnalysisRecordBasedRetagger):
    """ Second Retagger for removal of redundant proper names analyses.
        If a word has multiple analyses, and some of these will be proper
        names listed in the given lexicon, then proper names appearing in 
        the lexicon will be removed.
    """
    def __init__(self, lexicon:dict, \
                       morph_analysis_layer:str='morph_analysis'):
        super().__init__( morph_analysis_layer=morph_analysis_layer )
        self.conf_param.append('_lexicon')
        self._lexicon = lexicon

    def rewrite_words(self, words:list):
        changed_words = set()
        for wid, word_analyses in enumerate( words ):
            changed = False
            if len(word_analyses) > 1: # Only consider words that have more than 1 analysis
                # 1) Gather deletable proper name analyses 
                toDelete = []
                for analysis in word_analyses:
                    if analysis['partofspeech'] == 'H' and analysis['root'] in self._lexicon:
                        toDelete.append(analysis)
                # 2) Perform deletion
                for analysis in toDelete:
                    word_analyses.remove(analysis)
                    changed = True
            if changed:
                # Keep track of changed words (for optimization purposes)
                changed_words.add( wid )
        return words, changed_words


class ProperNamesDisambiguationStep3Retagger(MorphAnalysisRecordBasedRetagger):
    """ Third Retagger for removal of redundant proper names analyses.
        -- in case of sentence-central ambiguous proper names, keep only 
           proper name analyses;
        -- in case of sentence-initial ambiguous proper names: if the 
           proper name has corpus frequency greater than 1, then keep only 
           proper name analyses. Otherwise, leave analyses intact;
    """
    def __init__(self, lexicon:dict, \
                       morph_analysis_layer:str='morph_analysis'):
        super().__init__( morph_analysis_layer=morph_analysis_layer, \
                          add_normalized_word_form=True, \
                          add_sentence_ids=True )
        self.conf_param.append('_lexicon')
        self._lexicon = lexicon

    def rewrite_words(self, words:list):
        changed_words = set()
        last_sent_id = -1
        nextSentenceInitialPosition = -1
        for wid, word_analyses in enumerate( words ):
            # Determine if we are at the sentence start:
            # 1) Regular sentence start
            cur_sent_id = word_analyses[0]['sentence_id']
            sentence_start = cur_sent_id != last_sent_id or \
                             wid == nextSentenceInitialPosition
            # 2) Heuristic: punctuation that is not comma 
            #    nor semicolon, is before a sentence-initial 
            #    position
            if all([ a['partofspeech'] == 'Z' for a in word_analyses ]) and \
                   not re.match('^[,;]+$', word_analyses[0]['word_normal']):
                nextSentenceInitialPosition = wid + 1
            changed = False
            # 
            #  Only consider ambiguous words with proper names analyses
            # 
            if len(word_analyses) > 1 and \
               any([ a['partofspeech'] == 'H' for a in word_analyses ]):
                if not sentence_start:
                    # In the middle of a sentence, choose only proper name
                    # analyses (assuming that by now, all the remaining proper 
                    # name analyses are correct)
                    toDelete = []
                    for analysis in word_analyses:
                        if analysis['partofspeech'] not in ['H','G']:
                            toDelete.append(analysis)
                    for analysis in toDelete:
                        word_analyses.remove(analysis)
                        changed = True
                else:
                    # In the beginning of a sentence: choose only proper name
                    # analysis only if the proper name analysis has corpus 
                    # frequency higher than 1
                    toDelete = []
                    hasRecurringProperName = False
                    for analysis in word_analyses:
                        if analysis['partofspeech'] == 'H' and \
                           analysis['root'] in self._lexicon and \
                           self._lexicon[analysis['root']] > 1:
                            hasRecurringProperName = True
                        if analysis['partofspeech'] not in ['H','G']:
                            toDelete.append(analysis)
                    if hasRecurringProperName and toDelete:
                        for analysis in toDelete:
                            word_analyses.remove(analysis)
                            changed = True
            if changed:
                # Keep track of changed words (for optimization purposes)
                changed_words.add( wid )
            last_sent_id = cur_sent_id
        return words, changed_words

