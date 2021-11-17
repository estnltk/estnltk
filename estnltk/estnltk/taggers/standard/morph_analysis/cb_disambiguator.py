#
#  Corpus-based (CB) morphological disambiguator.
#
#  Based on the disambiguator source from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/disambiguator.py
#
#  Idea of the algorithm:     Heiki-Jaan Kaalep
#  Python's implementation:   Siim Orasmaa
#

from typing import Set

import re
from collections import defaultdict

from estnltk import Text, Layer
from estnltk.taggers import Tagger, Retagger

from estnltk.taggers.standard.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT
from estnltk.taggers.standard.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation


class CorpusBasedMorphDisambiguator( object ):
    """Provides corpus-based pre-disambiguation and post-disambiguation for morphological analysis.
       Unlike ordinary Taggers, this disambiguator operates on a collection of Text objects.
       
       Two steps:
       *) predisambiguate(docs) -- disambiguates proper names based on lemma counts in the 
          corpus (docs); this step should be applied after morphological analysis and before 
          vabamorf's statistical disambiguation;
          (!) Note: this only has an effect when the propername guessing was used during the 
              morphological analysis ( options: guess=True and propername=True );
          
       *) postdisambiguate(docs) -- disambiguates analyses based on lemma counts in the 
          corpus (docs); this step should be applied after vabamorf's statistical 
          disambiguation;
    """

    def __init__(self,
                 output_layer:str='morph_analysis',
                 input_words_layer:str='words',
                 input_sentences_layer:str='sentences',
                 count_position_duplicates_once:bool=False,
                 disamb_compound_words:bool=False,
                 ignore_lemmas_in_compounds:Set=set(['alus','alune','mai','maa']),
                 validate_inputs:bool=True ):
        """Initialize CorpusBasedMorphDisambiguator class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer that will 
            be disambiguated. 
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
        disamb_compound_words: bool (default: False)
            If set, then during the post-disambiguation, an 
            additional attempt is made to disambiguate compound 
            words solely based on their last words. 
            This includes getting additional lemma counts from the 
            last words of compound words , and using this information
            for disambiguating both the regular words and compound
            words.
            Example #1: the word 'edasipääsu' is a compound 
            word ('edasi_pääs') and it can also add to the 
            count of it's last word ('pääs'). This extra 
            information can help to disambiguate the non-compound 
            word 'pääsu', which lemma is ambiguous between 
            'pääs' and 'pääsu'.
            Example #2: the word 'lagi' is unambiguous, and can be 
            used to disambiguate the compound word 'saunalaest', 
            which is ambiguous between lemmas 'sauna_lagi' and 
            'sauna_laad'.
            Note: this is an experimental feature, needs further
            testing;
        ignore_lemmas_in_compounds: Set (default:{'alus','alune','mai','maa'})
            Set of lemmas, which should not be counted (nor disambiguated) 
            as the last words of compound words (if disamb_compound_words is 
            True), because their disambiguation is likely unreliable / 
            erroneous.
        validate_inputs : bool (default: True)
            If set (default), then input document collection will 
            be validated for having the appropriate structure, and 
            all documents will be checked for the existence of 
            required layers.
        """
        # Set attributes & configuration
        self.input_layers = [ input_words_layer, \
                              input_sentences_layer, \
                              output_layer ]
        self.output_layer = output_layer
        self._input_words_layer     = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self._count_position_duplicates_once = \
              count_position_duplicates_once
        self._disamb_compound_words = \
              disamb_compound_words
        self._ignore_lemmas_in_compounds = set()
        if ignore_lemmas_in_compounds is not None:
            if not isinstance(ignore_lemmas_in_compounds, set):
                raise TypeError('(!) ignore_lemmas_in_compounds should be a set of strings (word lemmas).')
            self._ignore_lemmas_in_compounds = ignore_lemmas_in_compounds
        self._validate_inputs  = validate_inputs
        self.output_attributes = (NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES


    # =========================================================
    # =========================================================
    #     Corpus-based pre-disambiguation of proper names
    # =========================================================
    # =========================================================


    def _create_proper_names_lexicon(self, docs, docs_detached_layers):
        """ Creates a proper name frequency dictionary based on the 
            collection of documents.
            Each entry in the dictionary describes how many times
            given (proper name) lemma appears in the corpus 
            (including ambiguous appearances).
        """
        lemmaFreq = defaultdict(int)
        for doc_id, doc in enumerate(docs):
            for word_morph in docs_detached_layers[doc_id][self.output_layer]:
                # 1) Find all unique proper name lemmas of
                #    this word 
                uniqLemmas = set()
                for analysis in word_morph.annotations:
                    if analysis.partofspeech == 'H':
                        uniqLemmas.add( analysis.root )
                # 2) Record lemma frequencies
                for lemma in uniqLemmas:
                    lemmaFreq[lemma] += 1
        return lemmaFreq


    def _disambiguate_proper_names_1(self, docs, docs_detached_layers, lexicon):
        """ Step 1 in removal of redundant proper names analyses: 
            if a word has multiple proper name analyses with different 
            frequencies, keep only the analysis that has the highest
            frequency.
        """
        disamb_retagger = ProperNamesDisambiguationStep1Retagger(lexicon,\
                          morph_analysis_layer=self.output_layer)
        for doc_id, doc in enumerate( docs ):
            disamb_retagger.change_layer( doc, docs_detached_layers[doc_id] )

    def _find_certain_proper_names(self, docs, docs_detached_layers):
        """ Creates the list of certain proper names: finds words that 
            only have proper name analyses and, gathers all unique proper 
            name lemmas from there;
        """
        certain_names = set()
        for doc_id, doc in enumerate( docs ):
            for word_morph in docs_detached_layers[doc_id][self.output_layer]:
                # Check if word only has proper name analyses
                if all([a.partofspeech == 'H' for a in word_morph.annotations]):
                    # If so, record its lemmas as "certain proper name lemmas"
                    for analysis in word_morph.annotations:
                        certain_names.add(analysis.root)
        return certain_names

    def _find_sentence_initial_proper_names(self, docs, docs_detached_layers):
        """ Creates the list of sentence-initial proper names.
            Finds words that have ambiguities between proper name and 
            regular analyses, and that are in the beginning of sentence, 
            or of an enumeration. Records and returns proper name lemmas 
            of such words;
        """
        sentInitialNames = set()
        for doc_id, doc in enumerate( docs ):
            sentences = docs_detached_layers[doc_id][self._input_sentences_layer]
            sentence_id = 0
            nextSentenceInitialPosition = -1
            morph_analysis = docs_detached_layers[doc_id][self.output_layer]
            for wid, word_morph in enumerate( morph_analysis ):
                current_sentence = sentences[sentence_id]
                # Check if the word is in sentence-initial position:
                # 1) word in the beginning of annotated sentence
                if current_sentence.start == word_morph.start:
                    nextSentenceInitialPosition = wid
                # 2) punctuation that is not comma neither semicolon, 
                #    is before a sentence-initial position
                if all([a.partofspeech == 'Z' for a in word_morph.annotations]) \
                     and not re.match('^[,;]+$', word_morph.text):
                    nextSentenceInitialPosition = wid + 1
                # 3) beginning of an enumeration (a number that does not look 
                #    like a date, and is followed by a period or a parenthesis),
                if not re.match('^[1234567890]*$', word_morph.text ) and \
                   not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word_morph.text ) and \
                   re.match("^[1234567890.()]*$", word_morph.text ):
                    nextSentenceInitialPosition = wid + 1
                # If we are in an sentence-initial position
                if wid == nextSentenceInitialPosition:
                    # Consider sentence-initial words that have both proper name 
                    # analyses, and also regular (not proper name) analyses
                    h_postags = [a.partofspeech == 'H' for a in word_morph.annotations]
                    if any(h_postags) and not all(h_postags):
                        for analysis in word_morph.annotations:
                            # Memorize all unique proper name lemmas
                            if analysis.partofspeech == 'H':
                                sentInitialNames.add( analysis.root )
                # Take the next sentence
                if current_sentence.end == word_morph.end:
                    sentence_id += 1
            assert sentence_id == len(sentences)
        return sentInitialNames


    def _find_sentence_central_proper_names(self, docs, docs_detached_layers):
        """ Creates the list of sentence-central proper names.
            Finds words that have ambiguities between proper name and 
            regular analyses, and that in central position of the 
            sentence. Records and returns proper name lemmas of 
            such words;
        """
        sentCentralNames = set()
        for doc_id, doc in enumerate( docs ):
            sentences = docs_detached_layers[doc_id][self._input_sentences_layer]
            sentence_id = 0
            nextSentenceInitialPosition = -1
            morph_analysis = docs_detached_layers[doc_id][self.output_layer]
            for wid, word_morph in enumerate( morph_analysis ):
                current_sentence = sentences[sentence_id]
                # Check if the word is in sentence-initial position:
                # 1) word in the beginning of annotated sentence
                if current_sentence.start == word_morph.start:
                    nextSentenceInitialPosition = wid
                # 2) punctuation that is not comma neither semicolon, 
                #    is before a sentence-initial position
                if all([a.partofspeech == 'Z' for a in word_morph.annotations]) and \
                   not re.match('^[,;]+$', word_morph.text):
                    nextSentenceInitialPosition = wid + 1
                # 3) beginning of an enumeration (a number that does not look 
                #    like a date, and is followed by a period or a parenthesis),
                if not re.match('^[1234567890]*$', word_morph.text ) and \
                   not re.match('^[1234567890]{1,2}.[1234567890]{1,2}.[1234567890]{4}$', word_morph.text ) and \
                   re.match("^[1234567890.()]*$", word_morph.text ):
                    nextSentenceInitialPosition = wid + 1
                # Assume: if the word is not on a sentence-initial position,
                #         it must be on a sentence-central position;
                if wid != nextSentenceInitialPosition:
                    # Consider sentence-central words that have proper name 
                    # analyses
                    for analysis in word_morph.annotations:
                        # Memorize all unique proper name lemmas
                        if analysis.partofspeech == 'H':
                            sentCentralNames.add( analysis.root )
                # Take the next sentence
                if current_sentence.end == word_morph.end:
                    sentence_id += 1
            assert sentence_id == len(sentences)
        return sentCentralNames


    def _remove_redundant_proper_names(self, docs, docs_detached_layers, notProperNames):
        """ Step 2 in removal of redundant proper names analyses: 
            if a word has  multiple  analyses, and  some  of  these 
            are in the lexicon notProperNames, then delete analyses 
            appearing in the lexicon.
         """
        disamb_retagger = ProperNamesDisambiguationStep2Retagger(notProperNames,\
                          morph_analysis_layer=self.output_layer)
        for doc_id, doc in enumerate( docs ):
            disamb_retagger.change_layer( doc, docs_detached_layers[doc_id] )


    def _disambiguate_proper_names_2(self, docs, docs_detached_layers, lexicon):
        """ Step 3 in removal of redundant proper names analyses: 
            -- in case of sentence-central ambiguous proper names, keep 
               only proper name analyses;
            -- in case of sentence-initial ambiguous proper names: if the 
               proper name has corpus frequency greater than 1, then keep 
               only proper name analyses. 
               Otherwise, leave analyses intact;
         """
        disamb_retagger = ProperNamesDisambiguationStep3Retagger(lexicon,\
                          morph_analysis_layer=self.output_layer,\
                          input_words_layer=self._input_words_layer,\
                          input_sentences_layer=self._input_sentences_layer )
        for doc_id, doc in enumerate( docs ):
            disamb_retagger.change_layer( doc, docs_detached_layers[doc_id] )


    def predisambiguate(self, docs):
        """ Pre-disambiguates proper names based on lemma counts 
            obtained from the input corpus. 
            General goal is to reduce proper name ambiguities of 
            title cased words. 
            The input corpus should be either:
              a) a list of Text objects;
              b) a list of lists of Text objects;
        """
        # Determine input structure
        input_format = determine_input_corpus_structure(docs)
        # Collect detached layers
        detached_layers = []
        if input_format in ['I', '0']:
            for doc in docs:
                layers = {}
                for layer in self.input_layers:
                    if layer in doc.layers:
                        layers[layer] = doc[layer]
                detached_layers.append(layers)
        elif input_format == 'II':
            for docs_list in docs:
                detached_layers.append([])
                for doc in docs_list:
                    layers = {}
                    for layer in self.input_layers:
                        if layer in doc.layers:
                            layers[layer] = doc[layer]
                    detached_layers[-1].append(layers)
        # Predisambiguate on docs and detached layers
        self._predisambiguate_detached_layers( docs, detached_layers, input_format_hint=input_format )


    def _predisambiguate_detached_layers(self, docs, detached_layers, input_format_hint=None ):
        """ Pre-disambiguates proper names based on lemma counts 
            obtained from the input corpus. 
            The algorithm is applied on docs with detached_layers;
            Note: this interface mimics the _change_layer interface of Retagger;
        """
        # Determine input structure (if not already determined)
        if input_format_hint is None:
            input_format_hint = determine_input_corpus_structure(docs)
        else:
            if input_format_hint not in ['I', 'II', '0']:
                raise ValueError('(!) Unexpected input_format_hint value {}.'.format(input_format_hint)+\
                                 ' The value should be from the set {"I","II","0"}.')
        # Validate the input collection for required layers
        if self._validate_inputs:
            self._validate_docs_for_required_layers( docs, detached_layers, \
                                                     input_format_hint=input_format_hint)
        # Restructure input (if required)
        flat_docs = []
        flat_detached_layers = []
        if input_format_hint in ['I', '0']:
            flat_docs = docs
            flat_detached_layers = detached_layers
        elif input_format_hint == 'II':
            # Flatten the collection
            flat_docs = \
                 [doc for sub_docs in docs for doc in sub_docs]
            flat_detached_layers = \
                 [layer for sub_layers in detached_layers for layer in sub_layers]
        # Sanity check
        assert len(flat_detached_layers) == len(flat_docs), \
             ' (!) Inconsistent input: the size of detached_layers is not equal to size of flat_docs.'
        # 1) Find frequencies of proper name lemmas
        lexicon = self._create_proper_names_lexicon( flat_docs, flat_detached_layers )
        # 2) First disambiguation: if a word has multiple proper name
        #    analyses with different frequencies, keep only the analysis
        #    with the highest corpus frequency ...
        self._disambiguate_proper_names_1( flat_docs, flat_detached_layers, lexicon )
        # 3) Find certain proper names, sentence-initial proper names,
        #    and sentence-central proper names 
        certainNames     = self._find_certain_proper_names(flat_docs, flat_detached_layers)
        sentInitialNames = self._find_sentence_initial_proper_names(flat_docs, flat_detached_layers)
        sentCentralNames = self._find_sentence_central_proper_names(flat_docs, flat_detached_layers)
        
        # 3.1) Find names only sentence initial, not sentence central
        onlySentenceInitial = sentInitialNames.difference(sentCentralNames)
        # 3.2) From names that are exclusively sentence initial, extract
        #      names that are not certain names (by lexicon);
        #      The remaining names are moste unlikely candidates for 
        #      proper names;
        notProperNames = onlySentenceInitial.difference(certainNames)
        # 3.3) Second disambiguation: remove sentence initial proper names
        #      that are most likely false positives
        self._remove_redundant_proper_names(flat_docs, flat_detached_layers, notProperNames)

        # 4) Find frequencies of proper name lemmas once again
        #    ( taking account that frequencies may have been changed )
        lexicon = self._create_proper_names_lexicon( flat_docs, flat_detached_layers )

        # 5) Remove redundant proper name analyses from words 
        #    that are ambiguous between proper name analyses 
        #    and regular analyses:
        #    -- in case of sentence-central ambiguous proper names, 
        #       keep only proper name analyses;
        #    -- in case of sentence-initial ambiguous proper names: 
        #       if the proper name has corpus frequency greater than
        #       1, then keep only proper name analyses. 
        #       Otherwise, leave analyses intact;
        self._disambiguate_proper_names_2(flat_docs, flat_detached_layers, lexicon)


    # =========================================================
    # =========================================================
    #     Corpus-based post-disambiguation
    # =========================================================
    # =========================================================

    def _remove_duplicate_and_problematic_analyses(self, docs, docs_detached_layers):
        """ Removes duplicate and problematic analyses from the 
            document collection. 
            See RemoveDuplicateAndProblematicAnalysesRetagger for 
            details.
         """
        duplicate_remover = RemoveDuplicateAndProblematicAnalysesRetagger(
                                morph_analysis_layer=self.output_layer )
        for doc_id, doc in enumerate( docs ):
            duplicate_remover.change_layer( doc, docs_detached_layers[doc_id] )


    def _add_hidden_analyses_layers(self, 
              docs, 
              docs_detached_layers, 
              hidden_words_layer:str='_hidden_morph_analysis',
              remove_old_hidden_words_layer:bool=False):
        """ Finds morphological ambiguities that should be ignored 
            by the post-disambiguator. Adds findings as a temporary 
            hidden_morph_analysis layer.
            See IgnoredByPostDisambiguationTagger for details.
        """
        hidden_words_tagger = IgnoredByPostDisambiguationTagger(
                                     input_morph_analysis_layer = self.output_layer,\
                                     output_layer = hidden_words_layer )
        if remove_old_hidden_words_layer:
            # Clean-up old layers (if required)
            self._remove_hidden_analyses_layers( docs, 
                         docs_detached_layers, 
                         hidden_words_layer = hidden_words_layer )
        for doc_id, doc in enumerate( docs ):
            # Create temporary hidden words layer
            new_layer = hidden_words_tagger.make_layer( doc, docs_detached_layers[doc_id] )
            docs_detached_layers[doc_id][hidden_words_layer] = new_layer


    @staticmethod
    def _remove_hidden_analyses_layers(docs, docs_detached_layers, hidden_words_layer: str = '_hidden_morph_analysis'):
        """ Removes temporary hidden_words_layer-s that were 
            created with the method _add_hidden_analyses_layers().
        """
        for doc_id, doc in enumerate( docs ):
            if hidden_words_layer in docs_detached_layers[doc_id]:
                # Delete existing layer
                del docs_detached_layers[doc_id][hidden_words_layer]


    def _supplement_lemma_frequency_lexicon(self, docs, docs_detached_layers, lexicon, amb_lexicon,
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
            layers = docs_detached_layers[d]
            morph_analysis = layers[ self.output_layer ]
            assert hidden_words_layer in layers, \
                   '(!) Text is missing layer {!r}'.format( hidden_words_layer )
            hidden_words = layers[ hidden_words_layer ]
            hidden_words_id = 0
            for w, word_morph in enumerate( morph_analysis ):
                # Skip so-called hidden word / hidden ambiguities
                # ( these are not related to content words, and thus are 
                #   less likely to be (correctly) resolved by the corpus- 
                #   based disambiguation )
                hidden_word = hidden_words[hidden_words_id] if hidden_words_id < len(hidden_words) else []
                if len(hidden_word) > 0 and word_morph.base_span in hidden_word.base_span:
                    # Take the next hidden word id
                    hidden_words_id += 1
                    # Skip the word
                    continue
               # Skip an unknown word
                if is_unknown_word(word_morph):
                    continue
                # find out whether the word is ambiguous
                isAmbiguous = len(word_morph.annotations) > 1
                # keep track of lemmas already seen at this position:
                encounteredLemmas = set() 
                # Record lemma frequencies
                for a in word_morph.annotations:
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
                    # 3) Try to include information from compounds (if required)
                    # For instance: if we have a compound word, such as 
                    # 'edasi_pääs', it can help to disambiguate non-compound 
                    # word like 'pääsu', which is ambiguous between lemmas 
                    # 'pääs' and 'pääsu';
                    # [ an experimental feature ]
                    if self._disamb_compound_words and '_' in lemma:
                        lemma_parts = lemma.split('_')
                        last_word   = lemma_parts[-1]
                        if len(last_word) > 0 and \
                           last_word not in self._ignore_lemmas_in_compounds:
                            encounteredLemmas.add( last_word )
                            if last_word not in lexicon:
                                lexicon[last_word] = 1
                            else:
                                lexicon[last_word] += 1
                            if isAmbiguous:
                                amb_lexicon[last_word] = 1
            # Sanity check: all hidden words should be exhausted by now 
            assert hidden_words_id == len(hidden_words)
        # Use the general frequency lexicon to populate the lexicon of ambiguous 
        # lemmas with frequencies
        for lemma in amb_lexicon.keys():
            amb_lexicon[lemma] = lexicon[lemma]


    def _disambiguate_with_lexicon(self, docs, docs_detached_layers, lexicon, \
                                   hidden_words_layer:str='_hidden_morph_analysis' ):
        """ Performs lemma-based post-disambiguation. 
            Very roughly uses the idea "one sense per discourse" for lemmas.
            See LemmaBasedPostDisambiguationRetagger for details.
        """
        lemma_based_disambiguator = \
              LemmaBasedPostDisambiguationRetagger(lexicon=lexicon,
                            morph_analysis_layer=self.output_layer,\
                            input_hidden_morph_analysis_layer=hidden_words_layer, \
                            disambiguate_last_words_of_compounds=self._disamb_compound_words, \
                            ignore_last_words=self._ignore_lemmas_in_compounds )
        for doc_id, doc in enumerate( docs ):
            lemma_based_disambiguator.change_layer( doc, docs_detached_layers[doc_id] )


    def postdisambiguate(self, in_collections):
        """ Post-disambiguates ambiguous analyses based on lemma counts 
            obtained from the input corpus.
            In a nutshell: uses the idea "one sense per discourse" for 
            lemmas. If an ambiguous lemma has a "wide spread" in the corpus
            (it occurs in many places of the corpus), then it will be chosen 
            as the correct lemma among the other (less spread) lemmas.
            The input corpus should be either:
              a) a list of Text objects;
              b) a list of lists of Text objects;
            Note: if the input corpus is in the format b), then two level
            disambiguation will be performed: first disambiguation is 
            performed within each sub list of Texts, and then performed
            within the whole collection.
        """ 
        # 1) Determine input structure
        input_format = determine_input_corpus_structure(in_collections)
        # 2) Make detached_layers
        detached_layers = []
        if input_format == 'I':
            for doc in in_collections:
                layers = {}
                for layer in self.input_layers:
                    if layer in doc.layers:
                        layers[layer] = doc[layer]
                detached_layers.append(layers)
        elif input_format == 'II':
            for docs_list in in_collections:
                detached_layers.append( [] )
                for doc in docs_list:
                    layers = {}
                    for layer in self.input_layers:
                        if layer in doc.layers:
                            layers[layer] = doc[layer]
                    detached_layers[-1].append(layers)
        # 3) Post-disambiguate
        self._postdisambiguate_detached_layers( in_collections, detached_layers, \
                                                input_format_hint=input_format)


    def _postdisambiguate_detached_layers(self, in_collections, detached_layers, input_format_hint=None):
        """ Post-disambiguates ambiguous analyses based on lemma counts 
            obtained from the input corpus.
            The algorithm is applied on a collection of docs with detached_layers.
            Note: this interface mimics the _change_layer interface of Retagger;
        """
        # Determine input structure (if not already determined)
        if input_format_hint is None:
            input_format_hint=determine_input_corpus_structure(in_collections)
        else:
            if input_format_hint not in ['I', 'II', '0']:
                raise ValueError('(!) Unexpected input_format_hint value {}.'.format(input_format_hint)+\
                                 ' The value should be from the set {"I","II","0"}.')
        # Validate the input collection for required layers
        if self._validate_inputs:
            self._validate_docs_for_required_layers( in_collections, detached_layers, \
                                                     input_format_hint=input_format_hint)
        # Restructure input (if required)
        _in_collections = []
        in_detached_layers = []
        if input_format_hint == 'I':
            _in_collections = [ in_collections ]
            in_detached_layers = [ detached_layers ]
        elif input_format_hint == 'II':
            _in_collections = in_collections
            in_detached_layers = detached_layers
        # Sanity checks on input
        assert len(_in_collections) == len(in_detached_layers)
        assert [len(docs) for docs in _in_collections] == [len(lyrs) for lyrs in in_detached_layers]
        #
        #  1st phase:  post-disambiguate inside a single document collection
        #     (e.g. disambiguate all news articles published on the same day)
        #
        for collection_id, docs in enumerate(_in_collections):
            detached_layers = in_detached_layers[collection_id]
            # 1) Remove duplicate and problematic analyses
            self._remove_duplicate_and_problematic_analyses( docs, detached_layers )
            # 2) Find ambiguities that should be ignored by the post-disambiguator
            #    add results as a new (temporary) layer
            self._add_hidden_analyses_layers( docs, detached_layers )
            # 3) Collect two types of lemma frequencies:
            #    *) general lemma frequencies over all words (except words marked
            #       as ignored words);
            #    *) lemma frequencies of ambiguous words (except words marked
            #       as ignored words);
            genLemmaLex = dict()
            ambLemmaLex = dict()
            self._supplement_lemma_frequency_lexicon(docs, detached_layers, \
                                                     genLemmaLex, ambLemmaLex)
            # 4) Perform lemma-based post-disambiguation;
            #    In case of ambiguous words, keep analyses with the highest lemma 
            #    frequency. An exception: if all lemma frequencies are equal, then 
            #    keep all the analyses;
            self._disambiguate_with_lexicon( docs, detached_layers, ambLemmaLex )
            # 5) Clean-up: remove hidden analyses layers
            self._remove_hidden_analyses_layers( docs, detached_layers )
        #
        #  2nd phase:  post-disambiguate over all document collections
        #              (for instance, disambiguate over all news editions published
        #               in a single year, each edition consists of articles published
        #               on a single day)
        #
        if len(_in_collections) > 1:
            # lexicons over the whole corpus
            genLemmaLex = dict()
            ambLemmaLex = dict()
            for collection_id, docs in enumerate(_in_collections):
                detached_layers = in_detached_layers[collection_id]
                # 1) Find ambiguities that should be ignored by the post-
                #    disambiguator; add results as a new (temporary) layer
                self._add_hidden_analyses_layers( docs, detached_layers )
                # 2) Collect two types of lemma frequencies:
                #    *) general lemma frequencies over all words (except words 
                #       marked as ignored words);
                #    *) lemma frequencies of ambiguous words (except words 
                #       marked as ignored words);
                self._supplement_lemma_frequency_lexicon(docs, detached_layers, \
                                                         genLemmaLex, ambLemmaLex)
            # perform the second phase of post-disambiguation
            for collection_id, docs in enumerate(_in_collections):
                detached_layers = in_detached_layers[collection_id]
                # 1) Find ambiguities that should be ignored by the post-
                #    disambiguator; add results as a new (temporary) layer
                #    TODO: why it is necessary to add the layer 2nd time?
                self._add_hidden_analyses_layers( docs, detached_layers,
                                                  remove_old_hidden_words_layer=True )
                # 2) Perform lemma-based post-disambiguation;
                #    In case of ambiguous words, keep analyses with the highest lemma 
                #    frequency. An exception: if all lemma frequencies are equal, then 
                #    keep all the analyses;
                self._disambiguate_with_lexicon( docs, detached_layers, ambLemmaLex )
                # 3) Clean-up: remove hidden analyses layers
                self._remove_hidden_analyses_layers( docs, detached_layers )
            # And we're done! (for now)


    # =========================================================
    #     Input validation
    # =========================================================

    def _validate_docs_for_required_layers( self, in_collections:list, detached_layers:list, input_format_hint=None):
        """ Checks that all documents' detached_layers include the 
            layers required by this disambiguator.  If one of the 
            documents in the collection misses some of the layers, 
            raises an expection.
        """
        # Determine the input corpus structure
        if input_format_hint is None:
            input_format_hint=determine_input_corpus_structure(in_collections)
        else:
            if input_format_hint not in ['I', 'II', '0']:
                raise ValueError('(!) Unexpected input_format_hint value {}.'.format(input_format_hint)+\
                                 'The value should be from the set {"I","II","0"}.')
        # Validate the structure
        if input_format_hint == 'I':
            assert len(in_collections) == len(detached_layers)
            for doc_id, doc in enumerate(in_collections):
                doc_detached_layers = detached_layers[doc_id]
                assert isinstance(doc, Text)
                assert isinstance(doc_detached_layers, dict)
                missing = []
                not_detached = []
                for layer in self.input_layers:
                    if layer not in doc_detached_layers:
                        if layer in doc.layers:
                            not_detached.append( layer )
                        missing.append( layer )
                if not_detached:
                    raise Exception( '(!) {!r} has layers {!r}, but they are not in detached_layers: {!r}'.\
                          format(doc,not_detached,detached_layers.keys()))
                if missing:
                    raise Exception('(!) {!r} is missing layers {!r} from its detached_layers.'.format(doc, missing))
        elif input_format_hint == 'II':
            assert len(in_collections) == len(detached_layers)
            for cid, docs_list in enumerate(in_collections):
                assert len(docs_list) == len(detached_layers[cid])
                for doc_id, doc in enumerate(docs_list):
                    doc_detached_layers = detached_layers[cid][doc_id]
                    assert isinstance(doc, Text)
                    assert isinstance(doc_detached_layers, dict)
                    missing = []
                    not_detached = []
                    for layer in self.input_layers:
                        if layer not in doc_detached_layers:
                            if layer in doc.layers:
                                not_detached.append( layer )
                            missing.append( layer )
                    if not_detached:
                        raise Exception( '(!) {!r} has layers {!r}, but they are not in detached_layers: {!r}'.\
                              format(doc,not_detached,detached_layers.keys()))
                    if missing:
                        raise Exception('(!) {!r} is missing layers {!r} from its detached_layers.'.format(doc, missing))


    # =========================================================
    # =========================================================
    #     Object representation
    # =========================================================
    # =========================================================
    
    def __repr__(self):
        conf_str = ''
        conf_str = 'input_layers=['+(', '.join([l for l in self.input_layers]))+']'
        conf_str += ', output_layer='+self.output_layer
        return self.__class__.__name__ + '(' + conf_str + ')'

    def _repr_html_(self):
        # Add description
        import pandas
        parameters = {'output layer': self.output_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['output layer', 'output attributes', 'input layers'],
                                 index=[0])
        table = table.to_html(index=False)
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>'+self.__class__.__name__+'</h4>', description, table]
        # Add configuration parameters
        public_param = ['_count_position_duplicates_once', '_disamb_compound_words', '_validate_inputs']
        if self._disamb_compound_words:
            public_param.append('_ignore_lemmas_in_compounds')
        conf_values  = []
        for attr in public_param:
            conf_values.append( str(getattr(self, attr)) )
        conf_table = pandas.DataFrame(conf_values, index=public_param)
        conf_table = conf_table.to_html(header=False)
        conf_table = ('<h4>Configuration</h4>', conf_table)
        table.extend( conf_table )
        return '\n'.join(table)


    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.input_layers) + '*->' + self.output_layer + '*)'


# =========================================================
# =========================================================
#     Helpers
# =========================================================
# =========================================================

def determine_input_corpus_structure( in_collections:list, validate=True ):
    """ Determines which type of structure of the input collection has.
        Returns:
           '0'  -- the input is an empty list;
           'I'  -- the input is a list of Text objects;
           'II' -- the input is a list of list of Text objects;
        If validate=True (default), raises an AssertionError about
        unexpected input structure if the input structure is not 
        one of the 3 aforementioned types.
    """ 
    # Determine the input corpus structure
    input_format_hint=None
    if is_list_of_texts( in_collections ):
        input_format_hint = 'I'
    elif is_list_of_lists_of_texts( in_collections ):
        input_format_hint = 'II'
    if input_format_hint in ['I', 'II'] and len(in_collections) == 0:
        input_format_hint = '0'
    # Validate input structure
    if validate and input_format_hint is None:
        raise AssertionError('(!) Unexpected input structure. The first input argument should be '+\
                             'either a list of Text objects, or a list of lists of Text objects.')
    return input_format_hint

def is_list_of_texts( docs:list ):
    """ Checks that the input list docs is:
        *) an empty list, or
        *) a list of Text objects;
        This is an input structure suitable for 
        corpus-based morphological disambiguator.
    """ 
    is_list = isinstance(docs, list)
    is_empty = is_list and len(docs) == 0
    return is_list and (is_empty or all(isinstance(d, Text) for d in docs))


def is_list_of_lists_of_texts( docs:list ):
    """ Checks that the input list docs is:
        *) an empty list, or
        *) a list of lists of Text objects;
        This is an input structure suitable for 
        corpus-based morphological disambiguator.
    """ 
    is_list = isinstance(docs, list)
    is_empty = is_list and len(docs) == 0
    return is_list and (is_empty or (all(isinstance(ds, list) for ds in docs) and
                                         all([all([isinstance(d, Text) for d in ds]) for ds in docs])) )


def is_unknown_word(word_morph_analyses):
    """ Detects whether word's morphological analyses indicate 
        that this is an unknown word.

    """
    return word_morph_analyses is None \
           or any([_is_empty_annotation(a) for a in word_morph_analyses.annotations])


# ----------------------------------------

class CorpusBasedMorphDisambiguationSubstepRetagger(Retagger):
    """ A general Retagger for a sub step in corpus-based 
        morphological disambiguation.

        Defines common attributes, input and output layers for 
        inheriting classes. Inheriting classes should implement 
        the method:
            change_layer(...)
    """
    output_attributes = (NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES
    conf_param = [ # input layers
                   '_input_morph_analysis_layer',\
                   '_input_words_layer',\
                   '_input_sentences_layer' ]
    
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
        morph_analysis_layer = layers[self._input_morph_analysis_layer]
        for span in morph_analysis_layer:
            annotations = span.annotations
            if len(annotations) > 1: # Only consider words that have more than 1 analysis
                # 1) Collect all proper name analyses of the word, and 
                #    get their highest frequency based on the the freq lexicon
                highestFreq = 0
                properNameAnalyses = []
                for analysis in annotations:
                    if analysis.partofspeech == 'H':
                        if analysis.root in self._lexicon:
                            properNameAnalyses.append( analysis )
                            if self._lexicon[analysis.root] > highestFreq:
                                highestFreq = self._lexicon[analysis.root]
                        else:
                            raise Exception(
                                '(!) Unable to find proper name lemma {!r} from the lexicon.'.format(analysis.root) )
                # 2) Keep only those proper name analyses that have the highest
                #    frequency (in the corpus), delete all others
                if highestFreq > 0:
                    toDelete = []
                    for analysis in properNameAnalyses:
                        if self._lexicon[ analysis.root ] < highestFreq:
                            toDelete.append(analysis)
                    for analysis in toDelete:
                        annotations.remove(analysis)



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
            if len(morph_analyses.annotations) > 1: # Only consider words that have more than 1 analysis
                # 1) Gather deletable proper name analyses 
                to_delete = []
                for analysis in morph_analyses.annotations:
                    if analysis.partofspeech == 'H' and analysis.root in self._lexicon:
                        to_delete.append(analysis)
                # 2) Perform deletion
                for analysis in to_delete:
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
                elif word_morph_analyses.start >= cur_sentence.end:
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
            if all([a.partofspeech == 'Z' for a in word_morph_analyses.annotations]) and \
                   not re.match('^[,;]+$', _get_word_text( word )):
                nextSentenceInitialPosition = wid + 1
            # 
            #  Only consider ambiguous words with proper names analyses
            # 
            if len(word_morph_analyses.annotations) > 1 and \
               any([a.partofspeech == 'H' for a in word_morph_analyses.annotations]):
                if not sentence_start:
                    # In the middle of a sentence, choose only proper name
                    # analyses (assuming that by now, all the remaining proper 
                    # name analyses are correct)
                    to_delete = []
                    for analysis in word_morph_analyses.annotations:
                        if analysis.partofspeech not in ['H','G']:
                            to_delete.append( analysis )
                    for analysis in to_delete:
                        word_morph_analyses.annotations.remove( analysis )
                        changed = True
                else:
                    # In the beginning of a sentence: choose only proper name
                    # analysis only if the proper name analysis has corpus 
                    # frequency higher than 1
                    to_delete = []
                    hasRecurringProperName = False
                    for analysis in word_morph_analyses.annotations:
                        if analysis.partofspeech == 'H' and \
                           analysis.root in self._lexicon and \
                           self._lexicon[analysis.root] > 1:
                            hasRecurringProperName = True
                        if analysis.partofspeech not in ['H','G']:
                            to_delete.append(analysis)
                    if hasRecurringProperName and to_delete:
                        for analysis in to_delete:
                            word_morph_analyses.annotations.remove(analysis)
                            changed = True



# ------------------------------------------
# ------------------------------------------
#   P o s t - d i s a m b i g u a t i o n
# ------------------------------------------
# ------------------------------------------

class RemoveDuplicateAndProblematicAnalysesRetagger( CorpusBasedMorphDisambiguationSubstepRetagger ):
    r""" A Retagger in corpus-based post-disambiguation preparation step. 
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
            for i1, analysis1 in enumerate(morph_analyses.annotations):
                duplicateFound = False
                for i2 in range(i1+1, len(morph_analyses.annotations)):
                    analysis2 = morph_analyses.annotations[i2]
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
                    morph_analyses.annotations.pop(aid)
            #
            # 2) If verb analyses contain forms '-tama' and '-ma', 
            #    then keep only '-ma' analyses;
            #
            tamaIDs = []
            maIDs   = []
            for i, analysis in enumerate(morph_analyses.annotations):
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
                   '_input_morph_analysis_layer' ]

    def __init__(self, output_layer:str='_hidden_morph_analysis',\
                       input_morph_analysis_layer:str='morph_analysis' ):
        self.output_layer = output_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [ input_morph_analysis_layer ]
        self.output_attributes = ()


    def _make_layer(self, text: Text, layers, status):
        hidden_words = Layer(name=self.output_layer,
                      text_object=text,
                      enveloping=self._input_morph_analysis_layer,
                      attributes=self.output_attributes,
                      ambiguous=False)
        nudTudEndings = re.compile('^.*[ntd]ud$')
        morph_analysis = layers[ self._input_morph_analysis_layer ]
        for w, word_morph in enumerate( morph_analysis ):
            if not is_unknown_word(word_morph) and len(word_morph.annotations) > 1:
                #
                # 1) If most of the analyses indicate nud/tud/dud forms, then hide the ambiguity:
                #    E.g.    kõla+nud //_V_ nud, //    kõla=nud+0 //_A_ //    kõla=nud+0 //_A_ sg n, //    kõla=nud+d //_A_ pl n, //
                nudTud = [nudTudEndings.match(a.root) is not None or
                          nudTudEndings.match(a.ending) is not None
                          for a in word_morph.annotations]
                if nudTud.count( True ) > 1:
                    hidden_words.add_annotation(morph_analysis[w:w+1])
                #
                # 2) If analyses have same lemma and no form, then hide the ambiguity:
                #    E.g.    kui+0 //_D_ //    kui+0 //_J_ //
                #            nagu+0 //_D_ //    nagu+0 //_J_ //
                lemmas = set(a.root for a in word_morph.annotations)
                forms  = set(a.form for a in word_morph.annotations)
                if len(lemmas) == 1 and len(forms) == 1 and (list(forms))[0] == '':
                    hidden_words.add_annotation(morph_analysis[w:w+1])
                #
                # 3) If 'olema' analyses have the same lemma and the same ending, then hide 
                #    the ambiguity:
                #    E.g.    'nad on' vs 'ta on' -- both get the same 'olema'-analysis, 
                #                                   which will remain ambiguous;
                endings = set(a.ending for a in word_morph.annotations)
                if len(lemmas) == 1 and (list(lemmas))[0] == 'ole' and len(endings) == 1 \
                   and (list(endings))[0] == '0':
                    hidden_words.add_annotation(morph_analysis[w:w+1])
                #
                # 4) If pronouns have the the same lemma and the same ending, then hide the 
                #    singular/plural ambiguity:
                #    E.g.     kõik+0 //_P_ sg n //    kõik+0 //_P_ pl n //
                #             kes+0 //_P_ sg n //    kes+0 //_P_ pl n //
                postags = set(a.partofspeech for a in word_morph.annotations)
                if len(lemmas) == 1 and len(postags) == 1 and 'P' in postags and \
                   len(endings) == 1:
                    hidden_words.add_annotation(morph_analysis[w:w+1])
                #
                # 5) If lemmas and endings are exactly the same, then hide the ambiguity 
                #    between numerals and pronouns:
                #    E.g.     teine+0 //_O_ pl n, //    teine+0 //_P_ pl n, //
                #             üks+l //_N_ sg ad, //    üks+l //_P_ sg ad, //
                if len(lemmas) == 1 and 'P' in postags and ('O' in postags or
                   'N' in postags) and len(endings) == 1:
                    hidden_words.add_annotation(morph_analysis[w:w+1])
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
                       input_hidden_morph_analysis_layer:str='_hidden_morph_analysis',
                       disambiguate_last_words_of_compounds:bool=False,
                       ignore_last_words:Set=None ):
        super().__init__( morph_analysis_layer=morph_analysis_layer )
        self.conf_param.append('_lexicon')
        self.conf_param.append('_hidden_morph_analysis_layer')
        self.conf_param.append('_disambiguate_last_words_of_compounds')
        self.conf_param.append('_ignore_last_words')
        self._lexicon = lexicon
        self._hidden_morph_analysis_layer = input_hidden_morph_analysis_layer
        self._disambiguate_last_words_of_compounds = disambiguate_last_words_of_compounds
        if ignore_last_words is None:
            ignore_last_words = set()
        else:
            if not isinstance(ignore_last_words, set):
                raise TypeError('(!) ignore_last_words should be a set of strings (word lemmas).')
        self._ignore_last_words = ignore_last_words
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
            if len(hidden_word) > 0 and word_morph.base_span in hidden_word.base_span:
                # Take the next hidden word id
                hidden_words_id += 1
                # Skip the word
                continue
            # Consider only ambiguous words
            if len(word_morph.annotations) > 1:
                # 0) Pre-analysis: find out if all words are compound words
                all_compounds = False
                if self._disambiguate_last_words_of_compounds:
                    all_compounds = \
                        all(['_' in analysis.root for analysis in word_morph.annotations])
                # 1) Find highest among the lemma frequencies
                highestFreq = 0
                lemma_frequencies = []
                for analysis in word_morph.annotations:
                    # Use -ma ending to distinguish verb lemmas from other lemmas
                    lemma = analysis.root+'ma' if analysis.partofspeech=='V' else analysis.root
                    lemma_freq = self._lexicon.get(lemma, 0)
                    lemma_frequencies.append( lemma_freq )
                    # A heuristic for compounds: if the last lemma of a compound has even 
                    # higher frequency, then use it instead 
                    if all_compounds and self._disambiguate_last_words_of_compounds:
                        last_lemma = lemma.split('_')[-1]
                        lemma = last_lemma if len(last_lemma) > 0 else lemma
                        lemma_freq_2 = self._lexicon.get(lemma, 0)
                        if lemma_freq_2 > lemma_freq and \
                           lemma not in self._ignore_last_words:
                            lemma_freq = lemma_freq_2
                            lemma_frequencies[-1] = lemma_freq
                    # Finally, try to update the highest frequency
                    if lemma_freq > highestFreq:
                        highestFreq = lemma_freq
                # 2) Remove all analyses that have (the lemma) frequency lower than 
                #    the highest frequency
                if highestFreq > 0:
                    assert len(lemma_frequencies) == len(word_morph.annotations)
                    toDelete = []
                    for aid, analysis in enumerate(word_morph.annotations):
                        freq = lemma_frequencies[aid]
                        if freq < highestFreq:
                            toDelete.append( analysis )
                    for analysis in toDelete:
                        word_morph.annotations.remove( analysis )
        # Sanity check: all hidden words should be exhausted by now 
        assert hidden_words_id == len( hidden_words )
