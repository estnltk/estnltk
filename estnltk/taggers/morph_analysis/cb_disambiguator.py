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

from estnltk import Text, EnvelopingSpan, Layer
from estnltk.layer.ambiguous_span import AmbiguousSpan
from estnltk.layer.span_operations import nested_aligned_left, left
from estnltk.layer.span_operations import equal as equal_spans

from estnltk.taggers import Tagger, Retagger

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.morf import VabamorfTagger
from estnltk.taggers.morph_analysis.morf import VabamorfDisambiguator
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation
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
                 input_sentences_layer:str='sentences',
                 count_position_duplicates_once:bool=False):
        """Initialize CorpusBasedMorphDisambiguator class.

        Parameters
        ----------
        morph_analysis_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer. 
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        count_position_duplicates_once: bool (default: False)
            If set, then duplicate lemmas appearing in one word 
            position will be only counted once during the post-
            disambiguation. 
            For example: the word 'põhja' is ambiguous between 
            4 analyses:
             [ ('põhi', 'S', 'adt'),  ('põhi', 'S', 'sg g'), 
               ('põhi', 'S', 'sg p'), ('põhja', 'V', 'o') ].
            If count_position_duplicates_once==False (default),
            then the counter will find {'põhi':4, 'põhja':1}, but 
            if count_position_duplicates_once==True, then 
            counts will be: {'põhi':1, 'põhja':1}.
            Note: this is an experimental feature, needs further
            testing;
        """
        # Set attributes & configuration
        self.input_layers = [ input_words_layer, \
                              input_sentences_layer ]
        self.depends_on   = self.input_layers
        self._input_words_layer     = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self._morph_analysis_layer  = morph_analysis_layer
        self._count_position_duplicates_once = \
             count_position_duplicates_once


    def disambiguate(self, docs:list, **kwargs):
        # TODO
        raise NotImplementedError('disambiguate method not implemented in ' + self.__class__.__name__)


    # =========================================================
    # =========================================================
    #     Corpus-based pre-disambiguation of proper names
    # =========================================================
    # =========================================================


    def _create_proper_names_lexicon(self, docs):
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


    def _disambiguate_proper_names_1(self, docs, lexicon):
        """ Step 1 in removal of redundant proper names analyses: 
            if a word has multiple proper name analyses with different 
            frequencies, keep only the analysis that has the highest
            frequency.
        """
        disamb_retagger = ProperNamesDisambiguationStep1Retagger(lexicon,\
                          morph_analysis_layer=self._morph_analysis_layer)
        for doc in docs:
            disamb_retagger.retag( doc )


    def _find_certain_proper_names(self, docs):
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


    def _find_sentence_initial_proper_names(self, docs):
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


    def _find_sentence_central_proper_names(self, docs):
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


    def _remove_redundant_proper_names(self, docs, notProperNames):
        """ Step 2 in removal of redundant proper names analyses: 
            if a word has  multiple  analyses, and  some  of  these 
            are in the lexicon notProperNames, then delete analyses 
            appearing in the lexicon.
         """
        disamb_retagger = ProperNamesDisambiguationStep2Retagger(notProperNames,\
                          morph_analysis_layer=self._morph_analysis_layer)
        for doc in docs:
            disamb_retagger.retag( doc )


    def _disambiguate_proper_names_2(self, docs, lexicon):
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


    def _predisambiguate(self, docs):
        """ Pre-disambiguates proper names based on lemma counts 
            obtained from the corpus (list of docs). 
            General goal is to reduce proper name ambiguities of title
            cased words. 
        """
        # 1) Find frequencies of proper name lemmas
        lexicon = self._create_proper_names_lexicon( docs )
        # 2) First disambiguation: if a word has multiple proper name
        #    analyses with different frequencies, keep only the analysis
        #    with the highest corpus frequency ...
        self._disambiguate_proper_names_1( docs, lexicon )
        # 3) Find certain proper names, sentence-initial proper names,
        #    and sentence-central proper names 
        certainNames     = self._find_certain_proper_names(docs)
        sentInitialNames = self._find_sentence_initial_proper_names(docs)
        sentCentralNames = self._find_sentence_central_proper_names(docs)
        
        # 3.1) Find names only sentence initial, not sentence central
        onlySentenceInitial = sentInitialNames.difference(sentCentralNames)
        # 3.2) From names that are exclusively sentence initial, extract
        #      names that are not certain names (by lexicon);
        #      The remaining names are moste unlikely candidates for 
        #      proper names;
        notProperNames = onlySentenceInitial.difference(certainNames)
        # 3.3) Second disambiguation: remove sentence initial proper names
        #      that are most likely false positives
        self._remove_redundant_proper_names(docs, notProperNames)
        #print( lexicon )
        #print( certainNames )
        #print( 'sentInitial->',sentInitialNames )
        #print( 'sentCentral->',sentCentralNames )
        #print( 'notProperNames->', notProperNames )
        
        # 4) Find frequencies of proper name lemmas once again
        #    ( taking account that frequencies may have been changed )
        lexicon = self._create_proper_names_lexicon( docs )
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
        self._disambiguate_proper_names_2(docs, lexicon)


    # =========================================================
    # =========================================================
    #     Corpus-based post-disambiguation
    # =========================================================
    # =========================================================

    def _remove_duplicate_and_problematic_analyses(self, docs):
        """ Removes duplicate and problematic analyses from the 
            document collection. 
            See RemoveDuplicateAndProblematicAnalysesRetagger for 
            details.
         """
        duplicate_remover = RemoveDuplicateAndProblematicAnalysesRetagger(
                                morph_analysis_layer=self._morph_analysis_layer )
        for doc in docs:
            duplicate_remover.retag( doc )


    def _add_hidden_analyses_layers(self, 
              docs, 
              hidden_words_layer:str='_hidden_morph_analysis',
              remove_old_hidden_words_layer:bool=False):
        """ Finds morphological ambiguities that should be ignored 
            by the post-disambiguator. Adds findings as a temporary 
            hidden_morph_analysis layer.
            See IgnoredByPostDisambiguationTagger for details.
        """
        hidden_words_tagger = IgnoredByPostDisambiguationTagger(
                                     input_morph_analysis_layer = self._morph_analysis_layer,\
                                     output_layer = hidden_words_layer )
        if remove_old_hidden_words_layer:
            # Clean-up old layers (if required)
            self._remove_hidden_analyses_layers( docs, 
                         hidden_words_layer = hidden_words_layer )
        for doc in docs:
            # Create temporary hidden words layer
            hidden_words_tagger.tag( doc )



    def _remove_hidden_analyses_layers(self, docs, 
                                       hidden_words_layer:str='_hidden_morph_analysis'):
        """ Removes temporary hidden_words_layer-s that were 
            created with the method _add_hidden_analyses_layers().
        """
        for doc in docs:
            if hidden_words_layer in doc.layers.keys():
                # Delete existing layer
                doc[ hidden_words_layer ]._bound = False
                delattr(doc, hidden_words_layer)



    def _supplement_lemma_frequency_lexicon(self, docs, lexicon, amb_lexicon,
                                                  hidden_words_layer:str='_hidden_morph_analysis' ):
        """ Counts lemma frequencies in docs, and amends given lexicon and amb_lexicon.
            *) lexicon -- frequencies of all lemmas in the corpus, except lemmas 
               in the hidden_words_layer; 
               If a lemma already exist in the lexicon, the old frequency will be
               increased by the new one;
            *) amb_lexicon -- frequencies of lemmas of ambiguous words, except the lemmas
               in the hidden_words_layer; 
               If a lemma already exist in the lexicon, the old frequency will be
               increased by the new one;
        """
        for d in range( len(docs) ):
            morph_analysis = docs[d][ self._morph_analysis_layer ]
            assert hidden_words_layer in docs[d].layers.keys(), \
                   '(!) Text is missing layer {!r}'.format( hidden_words_layer )
            hidden_words = docs[d][ hidden_words_layer ]
            hidden_words_id = 0
            for w, word_morph in enumerate( morph_analysis ):
                # Skip so-called hidden word / hidden ambiguities
                # ( these are not related to content words, and thus are 
                #   less likely to be (correctly) resolved by the corpus- 
                #   based disambiguation )
                hidden_word = hidden_words[hidden_words_id] if hidden_words_id < len(hidden_words) else []
                if word_morph in hidden_word:
                    # Take the next hidden word id
                    hidden_words_id += 1
                    # Skip the word
                    continue
                # find out whether the word is ambiguous
                isAmbiguous = len(word_morph) > 1
                # keep track of lemmas already seen at this position:
                encounteredLemmas = set() 
                # Record lemma frequencies
                for a in word_morph:
                    # Use -ma ending to distinguish verb lemmas from other lemmas
                    lemma = a.root+'ma' if a.partofspeech=='V' else a.root
                    if self._count_position_duplicates_once and lemma in encounteredLemmas:
                        # Skip the lemma, if it has already appeared in this 
                        # position
                        # For instance, if we have:
                        #     põhja -> [ ('põhi', 'S', 'adt'), ('põhi', 'S', 'sg g'), 
                        #                ('põhi', 'S', 'sg p'), ('põhja', 'V', 'o') ]
                        # then counts will be: {'põhi': 1, 'põhjama': 1}
                        # [ an experimental feature ]
                        continue
                    encounteredLemmas.add( lemma )
                    # 1) Record the general frequency
                    if lemma not in lexicon:
                        lexicon[lemma] = 1
                    else:
                        lexicon[lemma] += 1
                    # 2) Mark the existence of the ambiguous lemma
                    #    (do not mark the frequency yet)
                    if isAmbiguous:
                        amb_lexicon[lemma] = 1
            # Sanity check: all hidden words should be exhausted by now 
            assert hidden_words_id == len(hidden_words)
        # Use the general frequency lexicon to populate the lexicon of ambiguous 
        # lemmas with frequencies
        for lemma in amb_lexicon.keys():
            amb_lexicon[lemma] = lexicon[lemma]



    def _disambiguate_with_lexicon(self, docs, lexicon, \
                      hidden_words_layer:str='_hidden_morph_analysis' ):
        """ Performs lemma-based post-disambiguation. 
            Very roughly uses the idea "one sense per discourse" for lemmas.
            See LemmaBasedPostDisambiguationRetagger for details.
        """
        lemma_based_disambiguator = \
              LemmaBasedPostDisambiguationRetagger(lexicon=lexicon,
                            morph_analysis_layer=self._morph_analysis_layer,\
                            input_hidden_morph_analysis_layer=hidden_words_layer )
        for doc in docs:
            lemma_based_disambiguator.retag( doc )



    def _postdisambiguate(self, collections):
        """ Post-disambiguates ambiguous analyses based on lemma counts 
            obtained from the corpus (list of lists of docs).
            In a nutshell: uses the idea "one sense per discourse" for 
            lemmas. If an ambiguous lemma has a "wide spread" in the corpus
            (it occurs in many places of the corpus), then it will be chosen 
            as the correct lemma among the other (less spread) lemmas.
        """ 
        #
        #  1st phase:  post-disambiguate inside a single document collection
        #     (e.g. disambiguate all news articles published on the same day)
        #
        for docs in collections:
            # 1) Remove duplicate and problematic analyses
            self._remove_duplicate_and_problematic_analyses( docs )
            # 2) Find ambiguities that should be ignored by the post-disambiguator
            #    add results as a new (temporary) layer
            self._add_hidden_analyses_layers( docs )
            # 3) Collect two types of lemma frequencies:
            #    *) general lemma frequencies over all words (except words marked
            #       as ignored words);
            #    *) lemma frequencies of ambiguous words (except words marked
            #       as ignored words);
            genLemmaLex = dict()
            ambLemmaLex = dict()
            self._supplement_lemma_frequency_lexicon(docs, genLemmaLex, ambLemmaLex)
            # 4) Perform lemma-based post-disambiguation;
            #    In case of ambiguous words, keep analyses with the highest lemma 
            #    frequency. An exception: if all lemma frequencies are equal, then 
            #    keep all the analyses;
            self._disambiguate_with_lexicon( docs, ambLemmaLex )
            # 5) Clean-up: remove hidden analyses layers
            self._remove_hidden_analyses_layers( docs )
        #
        #  2nd phase:  post-disambiguate over all document collections
        #              (for instance, disambiguate over all news editions published
        #               in a single year, each edition consists of articles published
        #               on a single day)
        #
        if len(collections) > 1:
            # lexicons over the whole corpus
            genLemmaLex = dict()
            ambLemmaLex = dict()
            for docs in collections:
                # 1) Find ambiguities that should be ignored by the post-
                #    disambiguator; add results as a new (temporary) layer
                self._add_hidden_analyses_layers( docs )
                # 2) Collect two types of lemma frequencies:
                #    *) general lemma frequencies over all words (except words 
                #       marked as ignored words);
                #    *) lemma frequencies of ambiguous words (except words 
                #       marked as ignored words);
                self._supplement_lemma_frequency_lexicon(docs, genLemmaLex, ambLemmaLex)
            # perform the second phase of post-disambiguation
            for docs in collections:
                # 1) Find ambiguities that should be ignored by the post-
                #    disambiguator; add results as a new (temporary) layer
                #    TODO: why it is necessary to add the layer 2nd time?
                self._add_hidden_analyses_layers( docs, remove_old_hidden_words_layer=True )
                # 2) Perform lemma-based post-disambiguation;
                #    In case of ambiguous words, keep analyses with the highest lemma 
                #    frequency. An exception: if all lemma frequencies are equal, then 
                #    keep all the analyses;
                self._disambiguate_with_lexicon( docs, ambLemmaLex )
                # 3) Clean-up: remove hidden analyses layers
                self._remove_hidden_analyses_layers( docs )
            # And we're done! (for now)



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


# =========================================================
# =========================================================
#     Helpers
# =========================================================
# =========================================================

def is_unknown_word( word_morph_analyses ):
    """ Detects whether word's morphological analyses indicate 
        that this is an unknown word. 
    """
    if word_morph_analyses is not None:
        return any( [_is_empty_annotation(a) for a in word_morph_analyses] )
    return True


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
# ----------------------------------------
#   P r e - d i s a m b i g u a t i o n
# ----------------------------------------
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



# ------------------------------------------
# ------------------------------------------
#   P o s t - d i s a m b i g u a t i o n
# ------------------------------------------
# ------------------------------------------

class RemoveDuplicateAndProblematicAnalysesRetagger( CorpusBasedMorphDisambiguationSubstepRetagger ):
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



class IgnoredByPostDisambiguationTagger( Tagger ):
    """ A Tagger that finds and tags morphological ambiguities that 
        should be ignored by the post-disambiguator of lemmas. 
        The following cases will be ignored:
        *) ambiguities between nud, dud, tud forms;
        *) partofspeech ambiguities of non-inflecting words;
        *) the ambiguity of 'olema' in present ('nad on' vs 'ta on');
        *) singular/plural ambiguities of pronouns;
        *) partofspeech ambiguities between numerals and pronouns;
        Results will be formed as a temporary _hidden_morph_analysis 
        layer;
    """
    conf_param = [ # input layers
                   '_input_morph_analysis_layer',\
                   # For backward compatibility:
                   'depends_on', 'layer_name', 'attributes' ]

    def __init__(self, output_layer:str='_hidden_morph_analysis',\
                       input_morph_analysis_layer:str='morph_analysis' ):
        self.output_layer = output_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [ input_morph_analysis_layer ]
        self.output_attributes = ()
        self.attributes = self.output_attributes  # <- For backward compatibility ...
        self.layer_name = self.output_layer       # <- For backward compatibility ...
        self.depends_on = self.input_layers       # <- For backward compatibility ...


    def _make_layer(self, text: Text, layers, status):
        hidden_words = Layer(name=self.output_layer,
                      text_object=text,
                      enveloping=self._input_morph_analysis_layer,
                      attributes=self.output_attributes,
                      ambiguous=False)
        nudTudEndings = re.compile('^.*[ntd]ud$')
        morph_analysis = text[ self._input_morph_analysis_layer ]
        for w, word_morph in enumerate( morph_analysis ):
            if not is_unknown_word( word_morph ) and len( word_morph ) > 1:
                #
                # 1) If most of the analyses indicate nud/tud/dud forms, then hide the ambiguity:
                #    E.g.    kõla+nud //_V_ nud, //    kõla=nud+0 //_A_ //    kõla=nud+0 //_A_ sg n, //    kõla=nud+d //_A_ pl n, //
                nudTud = [ nudTudEndings.match(a.root) != None or \
                           nudTudEndings.match(a.ending) != None \
                           for a in word_morph ]
                if nudTud.count( True ) > 1:
                    hidden_words.add_annotation( EnvelopingSpan(spans=morph_analysis[w:w+1]) )
                #
                # 2) If analyses have same lemma and no form, then hide the ambiguity:
                #    E.g.    kui+0 //_D_ //    kui+0 //_J_ //
                #            nagu+0 //_D_ //    nagu+0 //_J_ //
                lemmas = set([ a.root for a in word_morph ])
                forms  = set([ a.form for a in word_morph ])
                if len(lemmas) == 1 and len(forms) == 1 and (list(forms))[0] == '':
                    hidden_words.add_annotation( EnvelopingSpan(spans=morph_analysis[w:w+1]) )
                #
                # 3) If 'olema' analyses have the same lemma and the same ending, then hide 
                #    the ambiguity:
                #    E.g.    'nad on' vs 'ta on' -- both get the same 'olema'-analysis, 
                #                                   which will remain ambiguous;
                endings = set([ a.ending for a in word_morph ])
                if len(lemmas) == 1 and (list(lemmas))[0] == 'ole' and len(endings) == 1 \
                   and (list(endings))[0] == '0':
                    hidden_words.add_annotation( EnvelopingSpan(spans=morph_analysis[w:w+1]) )
                #
                # 4) If pronouns have the the same lemma and the same ending, then hide the 
                #    singular/plural ambiguity:
                #    E.g.     kõik+0 //_P_ sg n //    kõik+0 //_P_ pl n //
                #             kes+0 //_P_ sg n //    kes+0 //_P_ pl n //
                postags  = set([ a.partofspeech for a in word_morph ])
                if len(lemmas) == 1 and len(postags) == 1 and 'P' in postags and \
                   len(endings) == 1:
                    hidden_words.add_annotation( EnvelopingSpan(spans=morph_analysis[w:w+1]) )
                #
                # 5) If lemmas and endings are exactly the same, then hide the ambiguity 
                #    between numerals and pronouns:
                #    E.g.     teine+0 //_O_ pl n, //    teine+0 //_P_ pl n, //
                #             üks+l //_N_ sg ad, //    üks+l //_P_ sg ad, //
                if len(lemmas) == 1 and 'P' in postags and ('O' in postags or \
                   'N' in postags) and len(endings) == 1:
                    hidden_words.add_annotation( EnvelopingSpan(spans=morph_analysis[w:w+1]) )
        return hidden_words



class LemmaBasedPostDisambiguationRetagger(CorpusBasedMorphDisambiguationSubstepRetagger):
    """A Retagger that performs lemma-based post-disambiguation. 
       Very roughly uses the idea "one sense per discourse" for lemmas.
       If an ambiguous lemma also occurs in other places of the text or in the corpus, 
       and it is more frequent than other lemmas (among ambiguous variants), then it is 
       likely the correct lemma, and it will be chosen. However, if all ambiguous lemmas 
       have the same corpus frequency, no disambiguation choice can be made, and the 
       lemmas will remain as they are.
    """

    def __init__(self, lexicon:dict, 
                       morph_analysis_layer:str='morph_analysis',
                       input_hidden_morph_analysis_layer:str='_hidden_morph_analysis' ):
        super().__init__( morph_analysis_layer=morph_analysis_layer )
        self.conf_param.append('_lexicon')
        self.conf_param.append('_hidden_morph_analysis_layer')
        self._lexicon = lexicon
        self._hidden_morph_analysis_layer = input_hidden_morph_analysis_layer
        self.input_layers.append( input_hidden_morph_analysis_layer )


    def _change_layer(self, text, layers, status: dict):
        morph_analysis_layer = layers[ self._input_morph_analysis_layer ]
        hidden_words = layers[ self._hidden_morph_analysis_layer ]
        hidden_words_id = 0
        for w, word_morph in enumerate( morph_analysis_layer ):
            # Skip so-called hidden word / hidden ambiguities
            # ( these are not related to content words, and thus are 
            #   less likely to be (correctly) resolved by the corpus- 
            #   based disambiguation )
            hidden_word = hidden_words[hidden_words_id] if hidden_words_id < len(hidden_words) else []
            if word_morph in hidden_word:
                # Take the next hidden word id
                hidden_words_id += 1
                # Skip the word
                continue
            # Consider only ambiguous words
            if len( word_morph ) > 1:
                # 1) Find highest among the lemma frequencies
                highestFreq = 0
                for analysis in word_morph:
                    # Use -ma ending to distinguish verb lemmas from other lemmas
                    lemma = analysis.root+'ma' if analysis.partofspeech=='V' else analysis.root
                    if lemma in self._lexicon and self._lexicon[lemma] > highestFreq:
                        highestFreq = self._lexicon[lemma]
                # 2) Remove all analyses that have (the lemma) frequency lower than 
                #    the highest frequency
                if highestFreq > 0:
                    toDelete = []
                    for analysis in word_morph:
                        lemma = analysis.root+'ma' if analysis.partofspeech=='V' else analysis.root
                        freq = self._lexicon[lemma] if lemma in self._lexicon else 0
                        if freq < highestFreq:
                            toDelete.append( analysis )
                    for analysis in toDelete:
                        word_morph.annotations.remove( analysis )
        # Sanity check: all hidden words should be exhausted by now 
        assert hidden_words_id == len( hidden_words )
