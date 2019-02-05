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
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.morph_analysis.postanalysis_tagger import PostMorphAnalysisTagger



class CorpusBasedMorphDisambiguator( object ):
    """ Disambiguator that performs morphological analysis along with different 
        morphological disambiguation steps -- pre-disambiguation, vabamorf's 
        disambiguation  and  post-disambiguation --  in  the  input  document 
        collection.
        
        In detail, different morphological disambiguation steps are 
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
                          morph_analysis_layer=self._morph_analysis_layer,\
                          input_words_layer=self._input_words_layer,\
                          input_sentences_layer=self._input_sentences_layer )
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



# ----------------------------------------

class CorpusBasedMorphDisambiguationSubstepRetagger(Retagger):
    """ A general Retagger for a sub step in corpus-based 
        morphological disambiguation.

        Defines common attributes, input and output layers for 
        inheriting classes. Inheriting classes should implement 
        the method:
            change_layer(...)
    """
    output_attributes = VabamorfTagger.attributes
    conf_param = [ # input layers
                   '_input_morph_analysis_layer',\
                   '_input_words_layer',\
                   '_input_sentences_layer',\
                   # For backward compatibility:
                   'depends_on', 'layer_name', 'attributes' ]
    attributes = output_attributes  # <- For backward compatibility ...
    
    def __init__(self, morph_analysis_layer:str='morph_analysis', \
                       requires_words_layer: bool = False, \
                       input_words_layer:str='words',\
                       requires_sentences_layer: bool = False, \
                       input_sentences_layer:str='sentences' ):
        """ Initialize CorpusBasedMorphDisambiguationSubstepRetagger class.
            
            Parameters
            ----------
            morph_analysis_layer: str (default: 'morph_analysis')
                Name of the morphological analysis layer that is to be changed;
            
            requires_words_layer: bool (default: False)
                If True, then words layer will be added to the required input 
                layers;
            
            input_words_layer: str (default: 'words')
                Name of the input words layer;
            
            requires_sentences_layer: bool (default: False)
                If True, then sentences layer will be added to the required input 
                layers;
            
            input_sentences_layer: str (default: 'sentences')
                Name of the input sentences layer;
        """
        # Set input/output layer names
        self.output_layer = morph_analysis_layer
        self._input_morph_analysis_layer = morph_analysis_layer
        self._input_words_layer = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self.input_layers = [morph_analysis_layer]
        if requires_words_layer:
            self.input_layers.append( self._input_words_layer )
        if requires_sentences_layer:
            self.input_layers.append( self._input_sentences_layer )
        self.layer_name = self.output_layer  # <- For backward compatibility ...
        self.depends_on = self.input_layers  # <- For backward compatibility ...

# ----------------------------------------



class ProperNamesDisambiguationStep1Retagger(CorpusBasedMorphDisambiguationSubstepRetagger):
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

    def _change_layer(self, text, layers, status: dict):
        morph_analysis_layer = layers[ self._input_morph_analysis_layer ]
        for morph_analyses in morph_analysis_layer:
            if len(morph_analyses) > 1: # Only consider words that have more than 1 analysis
                # 1) Collect all proper name analyses of the word, and 
                #    get their highest frequency based on the the freq lexicon
                highestFreq = 0
                properNameAnalyses = []
                for analysis in morph_analyses:
                    if analysis.partofspeech == 'H':
                        if analysis.root in self._lexicon:
                            properNameAnalyses.append( analysis )
                            if self._lexicon[analysis.root] > highestFreq:
                                highestFreq = self._lexicon[analysis.root]
                        else:
                            raise Exception( \
                                '(!) Unable to find proper name lemma {!r} from the lexicon.'.format(analysis.root) )
                # 2) Keep only those proper name analyses that have the highest
                #    frequency (in the corpus), delete all others
                if highestFreq > 0:
                    toDelete = []
                    for analysis in properNameAnalyses:
                        if self._lexicon[ analysis.root ] < highestFreq:
                            toDelete.append(analysis)
                    for analysis in toDelete:
                        morph_analyses.annotations.remove(analysis)



class ProperNamesDisambiguationStep2Retagger(CorpusBasedMorphDisambiguationSubstepRetagger):
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

    def _change_layer(self, text, layers, status: dict):
        morph_analysis_layer = layers[ self._input_morph_analysis_layer ]
        for morph_analyses in morph_analysis_layer:
            if len(morph_analyses) > 1: # Only consider words that have more than 1 analysis
                # 1) Gather deletable proper name analyses 
                toDelete = []
                for analysis in morph_analyses:
                    if analysis.partofspeech == 'H' and analysis.root in self._lexicon:
                        toDelete.append(analysis)
                # 2) Perform deletion
                for analysis in toDelete:
                    morph_analyses.annotations.remove(analysis)



class ProperNamesDisambiguationStep3Retagger(CorpusBasedMorphDisambiguationSubstepRetagger):
    """ Third Retagger for removal of redundant proper names analyses.
        -- in case of sentence-central ambiguous proper names, keep only 
           proper name analyses;
        -- in case of sentence-initial ambiguous proper names: if the 
           proper name has corpus frequency greater than 1, then keep only 
           proper name analyses. Otherwise, leave analyses intact;
    """
    def __init__(self, lexicon:dict, \
                       morph_analysis_layer:str='morph_analysis',\
                       input_words_layer:str='words',\
                       input_sentences_layer:str='sentences' ):
        super().__init__( morph_analysis_layer=morph_analysis_layer, \
                          input_words_layer=input_words_layer,\
                          input_sentences_layer=input_sentences_layer,\
                          requires_words_layer=True, \
                          requires_sentences_layer=True )
        self.conf_param.append('_lexicon')
        self._lexicon = lexicon

    def _change_layer(self, text, layers, status: dict):
        morph_analysis_layer = layers[ self._input_morph_analysis_layer ]
        words_layer     = layers[ self._input_words_layer ]
        sentences_layer = layers[ self._input_sentences_layer ]
        assert len(morph_analysis_layer) == len(words_layer)
        cur_sent_id = 0
        nextSentenceInitialPosition = -1
        for wid, word_morph_analyses in enumerate( morph_analysis_layer ):
            word = words_layer[wid]
            # A) Find annotated sentence that contains given word
            cur_sentence = None
            while cur_sent_id < len( sentences_layer ):
                cur_sentence = sentences_layer[cur_sent_id]
                if cur_sentence.start <= word_morph_analyses.start and \
                   word_morph_analyses.end <= cur_sentence.end:
                    # Take the current sentence
                    break
                elif word_morph_analyses.start > cur_sentence.end:
                    # Take the next sentence
                    cur_sent_id += 1
                else:
                    raise Exception('(!) Unable find sentence for the word {!r}; last sentence: {!r}'.format(word,cur_sentence))
            assert cur_sentence and \
                   cur_sentence.start <= word_morph_analyses.start and \
                   word_morph_analyses.end <= cur_sentence.end
            # B) Determine if we are at the sentence start:
            # B.1) Determine the extended sentence start position
            #      (start from annotations + start from heuristics)
            sentence_start = cur_sentence.start == word_morph_analyses.start or \
                             wid == nextSentenceInitialPosition
            # B.2) Heuristic: punctuation that is not comma 
            #      nor semicolon, is before a sentence-initial 
            #      position
            if all([ a.partofspeech == 'Z' for a in word_morph_analyses ]) and \
                   not re.match('^[,;]+$', _get_word_text( word )):
                nextSentenceInitialPosition = wid + 1
            # 
            #  Only consider ambiguous words with proper names analyses
            # 
            if len(word_morph_analyses) > 1 and \
               any([ a.partofspeech == 'H' for a in word_morph_analyses ]):
                if not sentence_start:
                    # In the middle of a sentence, choose only proper name
                    # analyses (assuming that by now, all the remaining proper 
                    # name analyses are correct)
                    toDelete = []
                    for analysis in word_morph_analyses:
                        if analysis.partofspeech not in ['H','G']:
                            toDelete.append( analysis )
                    for analysis in toDelete:
                        word_morph_analyses.annotations.remove( analysis )
                        changed = True
                else:
                    # In the beginning of a sentence: choose only proper name
                    # analysis only if the proper name analysis has corpus 
                    # frequency higher than 1
                    toDelete = []
                    hasRecurringProperName = False
                    for analysis in word_morph_analyses:
                        if analysis.partofspeech == 'H' and \
                           analysis.root in self._lexicon and \
                           self._lexicon[analysis.root] > 1:
                            hasRecurringProperName = True
                        if analysis.partofspeech not in ['H','G']:
                            toDelete.append(analysis)
                    if hasRecurringProperName and toDelete:
                        for analysis in toDelete:
                            word_morph_analyses.annotations.remove(analysis)
                            changed = True



class RemoveDuplicateAndProblematicAnalysesRetagger(CorpusBasedMorphDisambiguationSubstepRetagger):
    """ A Retagger in corpus-based post-disambiguation preparation step. 
        Removes:
        1) duplicate morphological analyses. For instance, word 'palk'
           obtains two analyses: 'palk' (which inflects as 'palk\palgi') 
           and 'palk' (which inflects as 'palk\palga'), but after the 
           removal of duplicates, only one remains;
        2) If verb analyses contain forms '-tama' and '-ma', then keep 
           only '-ma' analyses;
    """
    def __init__(self, morph_analysis_layer:str='morph_analysis'):
        super().__init__( morph_analysis_layer=morph_analysis_layer )

    def _change_layer(self, text, layers, status: dict):
        morph_analysis_layer = layers[ self._input_morph_analysis_layer ]
        for morph_analyses in morph_analysis_layer:
            #
            # 1) Find and remove duplicate analyses
            #
            toDeleteAnalysisIDs = []
            for i1, analysis1 in enumerate(morph_analyses):
                duplicateFound = False
                for i2 in range(i1+1, len(morph_analyses)):
                    analysis2 = morph_analyses[i2]
                    # Check for complete attribute match
                    attr_matches = []
                    for attr in self.output_attributes:
                        attr_match = \
                           getattr(analysis1,attr)==getattr(analysis2,attr)
                        attr_matches.append( attr_match )
                    if all( attr_matches ):
                        duplicateFound = True
                        toDeleteAnalysisIDs.append( i2 )
                        break
            if toDeleteAnalysisIDs:
                for aid in sorted(toDeleteAnalysisIDs, reverse=True):
                    morph_analyses.annotations.pop( aid )
            #
            # 2) If verb analyses contain forms '-tama' and '-ma', 
            #    then keep only '-ma' analyses;
            #
            tamaIDs = []
            maIDs   = []
            for i, analysis in enumerate(morph_analyses):
                if analysis.partofspeech == 'V':
                    if analysis.form == 'ma':
                        maIDs.append(i)
                    elif analysis.form == 'tama':
                        tamaIDs.append(i)
            if len(maIDs)>0 and len(tamaIDs)>0:
                for aid in sorted(tamaIDs, reverse=True):
                    morph_analyses.annotations.pop( aid )

