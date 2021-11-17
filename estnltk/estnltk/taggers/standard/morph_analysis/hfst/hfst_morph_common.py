#
#  Common resources and utilities for HFST-based morphological analyser of Estonian.
#

from typing import MutableMapping
from collections import OrderedDict

import os.path
import re

from estnltk import logger

from estnltk import Layer, Text
from estnltk import Span
from estnltk.taggers import Tagger

from estnltk.common import PACKAGE_PATH

#
# About the HFST model:
#
# Source code for the Estonian transducer models can be obtained from here:
#     https://victorio.uit.no/langtech/trunk/experiment-langs/est
# Once you have compiled HFST models of this repository, look for file 
# 'src/analyser-gt-desc.hfstol'. This is the file that can be given to 
# HfstEstMorphAnalyser as the transducer model.
#

HFST_MODEL_FILE = \
    os.path.join(PACKAGE_PATH, 'taggers', 'standard', 'morph_analysis', 'hfst', 'models', 'analyser-gt-desc.hfstol')

# ========================================================

class HfstMorphOutputExtractor(object):
    """ Base class for extractors that are responsible for extracting
        morph analysis records from the output of a HFST transducer,
        and saving these as annotatons of a layer.
        
        The following needs to be implemented in a derived class:
            set_output_attributes(...)
            extract_annotation_from_output(...)
    """

    def set_output_attributes(self, tagger:Tagger):
        """ Updates output_attributes of given Tagger according to 
            how attributes will be extracted by this extractor.
            This must be called before calling Tagger's _make_layer method;
        """
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)
    
    def extract_annotation_records(self, output_text:str, remove_guesses:bool ):
        """ Given an output of the HFST transducer, extracts morph analysis records from the 
            output, and returns as a list (of dictionaries). In case of an unknown word, returns 
            an empty list.
            If the parameter remove_guesses is True, then the guessed words will be removed from 
            the output records.
        """
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer, \
                                                  remove_guesses:bool ):
        """ Given word Span and the corresponding output of the HFST transducer, 
            extracts morph analysis records from the output, and saves as annotatons 
            of the layer. Note: implementations of this method should use extractor's 
            method extract_annotation_records() for getting the records;
            If the parameter remove_guesses is True, then the guessed word analyses 
            will not be added to the layer.
        """
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

# ========================================================

class RawAnalysesHfstMorphOutputExtractor(HfstMorphOutputExtractor):
    """ Hfst morph analysis output extractor that keeps analyses in the raw form. 
        This extractor separates analysis from the weight, but does not attempt 
        to do any further separation of details.
        
        In case of unknown words, sets the attribute 'raw_analysis' to None, and 
        the attribute 'weight' to float("inf");
    """

    def set_output_attributes(self, tagger:Tagger):
        # Update Tagger's output attributes
        tagger.output_attributes = ('raw_analysis', 'weight')

    def extract_annotation_records(self, output_text:str, remove_guesses:bool ):
        records = []
        if len(output_text) == 0:
            # Empty analysis == unknown word
            return records
        for analysis_weight in output_text.split('\n'):
            record = {}
            if '\t' in analysis_weight:
                # Known word or guessed word
                analysis, weight = analysis_weight.split('\t')
                record['weight'] = float(weight)
                record['raw_analysis'] = analysis
                add_record = True
                # Remove guesses (if required)
                if remove_guesses:
                    for guess_mark in est_hfst_guess_strs:
                        if guess_mark in analysis:
                            add_record = False
                # Add annotation to the layer
                if add_record:
                    records.append( record )
            elif len(analysis_weight) > 0:
                # Unknown word
                record['weight'] = float("inf")
                record['raw_analysis'] = None
                # Add annotation to the layer
                records.append( record )
        return records


    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer, \
                                                  remove_guesses:bool ):
        records = self.extract_annotation_records( output_text, remove_guesses=remove_guesses )
        # TODO: reorder records by their weights
        if len(records) == 0:
            # Empty analysis == unknown word
            record = {}
            record['weight'] = float("inf")
            record['raw_analysis'] = None
            # Add annotation to the layer
            layer.add_annotation( word, **record )
        else:
            for record in records:
                # Add annotation to the layer
                layer.add_annotation( word, **record )


# ========================================================

# ========================================================
#   Finding structure of hfst analysis
# ========================================================

#  Note: the structure of analysis is described in more 
#  detail in:
#     https://victorio.uit.no/langtech/trunk/experiment-langs/est/src/morphology/lexlang.xfscript

# part-of-speech_tags 
est_hfst_postags = [
    # DeclinablePOS 
    "+N", "+N+Prop", "+A", "+A+Comp", "+A+Superl", "+Num+Card", "+Num+Ord", "+Pron", "+ACR", "+ABBR",\
    # NonInflectingPOS 
    "+Adv", "+Interj", "+CC", "+CS", "+Adp", "+Pref", "+CLB", "+PUNCT",\
    # VPOS 
    "+V" ]

# Separates one component of a derivative from another
est_hfst_derivative_strs = ['+Der/', '+Dim/']

# Special case of derivative: a shortening of stem
est_hfst_shortening_strs = ['+Der/minus']

# Separates one component of a compound word from another
est_hfst_compound_seps = ['#']

# String marking a guessed word
est_hfst_guess_strs = ['+Guess']

# String marking a clitic
est_hfst_clitic_strs = ['+Foc/gi']

# Strings marking usage patterns
est_hfst_usage_strs = ["+Use/Rare", "+Use/Hyp", "+Use/NotNorm", "+Use/CommonNotNorm"]

# -------------------------------------------------

def split_into_morphemes( raw_analysis: str ):
    """ Splits raw analysis of the word into separate chunks of morphemes.
        Note: not all of these chunks are morphemes in the linguistic
        sense.
        
        Uses two kinds of split symbols:
        1) Split by compounding (symbol #):
            udu+N+Sg+Gen#loss+N+Sg+Nom => udu+N+Sg+Gen, loss+N+Sg+Nom

        2) Split by derivatives (symbol /):
            laulma+V+Der/ja+N+Sg+Nom => laulma+V+Der, ja+N+Sg+Nom
           
            An Exception: keep shortenings (+Der/minus) together with lemmas
            
            kohtumine+N+Der/minus#paik+N+Sg+Nom => kohtumine+N+Der/minus, paik+N+Sg+Nom
            käitumine+N+Der/minus#mudel+N+Sg+Nom => käitumine+N+Der/minus, mudel+N+Sg+Nom
        
        Clitics and usage information will also be separated from
        the rest of the morphemes, e.g.
            karu+Guess#tapja+N+Sg+Nom+Foc/gi => karu+Guess, tapja+N+Sg+Nom, +Foc/gi
            miski+Pron+Sg+Ine+Use/NotNorm => miski+Pron+Sg+Ine, +Use/NotNorm
    """
    locations = []
    start = 0
    alen = len(raw_analysis)
    for cid, chr in enumerate(raw_analysis):
        breakpoint_found = False
        # Check for compounding
        for cp in est_hfst_compound_seps:
            if cid+len(cp) <= alen and cp == raw_analysis[cid:cid+len(cp)]:
                if start < cid: # avoid adding empty strings at this point
                    locations.append( (start, cid) )
                start = cid+len(cp) # next start position
                breakpoint_found = True
                break
        if not breakpoint_found:
            # Check for shortening 
            # (this must come before other derivatives)
            for sh in est_hfst_shortening_strs:
                if cid+len(sh) <= alen and sh == raw_analysis[cid:cid+len(sh)]:
                    assert len(sh) > 1 and not sh.endswith('/')
                    locations.append( (start, cid+len(sh)) )
                    start = cid+len(sh) # next start position
                    breakpoint_found = True
                    break
        if not breakpoint_found:
            # Check for derivative
            for dv in est_hfst_derivative_strs:
                if cid+len(dv) <= alen and dv == raw_analysis[cid:cid+len(dv)]:
                    assert len(dv) > 1 and dv.endswith('/')
                    # Exclude only the last symbol of derivative (/)
                    locations.append( (start, cid+len(dv)-1) )
                    start = cid+len(dv) # next start position
                    breakpoint_found = True
                    break
        if not breakpoint_found:
            # Check for clitics
            for cl in est_hfst_clitic_strs:
                if cid+len(cl) <= alen and cl == raw_analysis[cid:cid+len(cl)]:
                    locations.append( (start, cid) )
                    start = cid # next start position
                    breakpoint_found = True
                    break
        if not breakpoint_found:
            # Check for usage information
            for us in est_hfst_usage_strs:
                if cid+len(us) <= alen and us == raw_analysis[cid:cid+len(us)]:
                    locations.append( (start, cid) )
                    start = cid # next start position
                    breakpoint_found = True
                    break
    # Add the last / remaining chunk
    if start < alen:
        locations.append( (start, alen) )
    # Take chunks out
    chunks = [raw_analysis[s:e] for (s,e) in locations]
    return chunks


def _compile_postags_pattern():
    """ Creates regexp for capturing part-of-speech tags 
        from the output of HFST lookup. """
    sorted_postags = sorted(est_hfst_postags, key=lambda x: (-len(x), x)) # Sort (longest first, then alpha)
    postags_regexp = '|'.join(sorted_postags)
    postags_regexp = '('+ postags_regexp.replace('+', r'\+') +')'
    return re.compile(postags_regexp)

est_hfst_postags_pattern = _compile_postags_pattern()

def _compile_usage_strs_pattern():
    """ Creates regexp for capturing part-of-speech tags 
        from the output of HFST lookup. """
    sorted_usage_strs = sorted(est_hfst_usage_strs, key=lambda x: (-len(x), x))
    usage_strs_regexp = '|'.join(sorted_usage_strs)
    usage_strs_regexp = '('+ usage_strs_regexp.replace('+', r'\+') +')'
    usage_strs_pattern = re.compile(usage_strs_regexp)
    return re.compile(usage_strs_pattern)

est_hfst_usage_strs_pattern = _compile_usage_strs_pattern()

def extract_morpheme_features( morpheme_chunks: list, clear_surrounding_plus_signs=True ):
    """ Processes word's  morpheme_chunks,  extracts  their 
        important  features  (for  instance:  morphemes, 
        part-of-speech tags, forms), and writes into an 
        ordered dictionary. 
        Returns resulting dictionary.

        The resulting dictionary has keys:
         * 'morphemes' -- list of morphemes in the word;
         * 'postags'   -- list of part-of-speech tags of 
                          corresponding morphemes;
         * 'forms'     -- list of forms / category markings of 
                          corresponding morphemes;
         * 'has_clitic' -- list of booleans, each indicating 
                           if there is a clitic attached to the 
                           corresponding morpheme.
                           Note: the clitic itself will not be 
                           added to the list morphemes;
         * 'is_guessed' -- list of booleans, each indicating if 
                           the corresponding morpheme contained 
                           a guessed analysis;
         * 'usage'      -- list of strings, each giving a remark
                           about corresponding morpheme's usage
                           (e.g. whether it is a rare word);
                           If the transducer did not output any
                           usage note for a morpheme, then an
                           empty string will fill up the place;
    """
    features = OrderedDict()
    features['morphemes'] = []
    features['postags']   = []
    features['forms']     = []
    features['has_clitic'] = []
    features['is_guessed'] = []
    features['usage']      = []
    for chunk_str in morpheme_chunks:
        is_guessed = False
        analysisExtracted = False
        # Try to extract a guessing label
        for guess in est_hfst_guess_strs:
            if chunk_str.endswith(guess):
                is_guessed = True
                # Remove guessed label
                chunk_str = chunk_str.replace(guess,'')
                break
            # Special case: guessed proper names (Guess+N+Prop)
            elif guess+'+N+Prop' in chunk_str:
                is_guessed = True
                # Remove guessed label
                chunk_str = chunk_str.replace(guess,'')
                break
        # Try to extract a morpheme with postag and form
        firstplus = chunk_str.find('+')
        postag_match = est_hfst_postags_pattern.search(chunk_str)
        if postag_match:
            postag_start = postag_match.start(0)
            postag_end = postag_match.end(0)
            # sanity check: start of the postag must overlap
            # with the first plus;
            if firstplus == postag_start:
                morpheme = chunk_str[0:postag_start]
                postag = chunk_str[postag_start:postag_end]
                form = chunk_str[postag_end:]
                features['morphemes'].append( morpheme )
                features['postags'].append( postag )
                features['forms'].append( form )
                features['has_clitic'].append( False )
                features['is_guessed'].append( is_guessed )
                features['usage'].append( '' )
                analysisExtracted = True
        # Try to extract a note about usage
        if est_hfst_usage_strs_pattern.match(chunk_str):
            assert len(features['usage']) > 0
            features['usage'][-1] += chunk_str
            analysisExtracted = True
        # Try to extract a note about clitic 
        for cl in est_hfst_clitic_strs:
            if cl == chunk_str:
                assert len(features['has_clitic']) > 0
                features['has_clitic'][-1] = True
                analysisExtracted = True
        if not analysisExtracted:
            if firstplus > -1:
                # In case of a plus sign, assume that it separates the 
                # morpheme from the form categories
                features['morphemes'].append( chunk_str[:firstplus] )
                features['postags'].append( '' )
                features['forms'].append( chunk_str[firstplus:] )
            else:
                # Assume a bare morpheme, without any category specification
                features['morphemes'].append( chunk_str )
                features['postags'].append( '' )
                features['forms'].append( '' )
            features['has_clitic'].append( False )
            features['is_guessed'].append( is_guessed )
            features['usage'].append( '' )
    if clear_surrounding_plus_signs:
        features['morphemes'] = [m.strip('+') for m in features['morphemes']]
        features['postags'] = [m.strip('+') for m in features['postags']]
        features['forms'] = [m.strip('+') for m in features['forms']]
        features['usage'] = [m.strip('+') for m in features['usage']]
    return features

# ========================================================

class MorphemesLemmasHfstOutputExtractor(HfstMorphOutputExtractor):
    """ Hfst morph analysis output extractor that splits the analysis into morphemes**.
        For  each  morpheme  or  lemma,  it  extracts corresponding postag, 
        and a form category. Results are stored in tuples,  so that the same 
        index can be used to access features of the morpheme stored in different 
        tuples.
        For instance, tuples of analysis of the word 'vanaema' are:
            morphemes:  ('vana', 'ema')
            postags:    ('A', 'N')
            forms:      ('Sg+Nom', 'Sg+Nom')
        Boolean attributes 'has_clitic', and 'is_guessed' state whether a
        clitic was present in the word, and whether the analysis of a 
        compound contains unknown word morphemes;
        Attribute 'usage' gives (string) remarks about word's usage, e.g. 
        whether it is a rarely used word;
        
        In case of unknown words, all analysis attributes will have value 
        None, and the attribute 'weight' will have value equal to 
        float("inf");
        
        ** morpheme -- the definition of the morpheme here does not 
           follow the linguistic one 100%. What is called a 'morpheme' 
           here may, in some cases, also be a lemma of a word. That is 
           why we use the attribute name 'morphemes_lemmas';
    """

    def set_output_attributes(self, tagger:Tagger):
        # Update Tagger's output attributes
        tagger.output_attributes = ('morphemes_lemmas','postags','forms','is_guessed','has_clitic','usage','weight')


    def _create_unknown_word_record(self):
        # Creates a record for an unknown word
        features = dict()
        features['morphemes_lemmas']  = None
        features['postags']    = None
        features['forms']      = None
        features['is_guessed'] = None
        features['has_clitic'] = None
        features['usage']      = None
        return features


    def extract_annotation_records(self, output_text:str, remove_guesses:bool ):
        records = []
        if len(output_text) == 0:
            # Empty analysis == unknown word
            return records
        for analysis_weight in output_text.split('\n'):
            record = {}
            if '\t' in analysis_weight:
                # Known word or guessed word
                raw_analysis, weight = analysis_weight.split('\t')
                record['weight'] = float(weight)
                morpheme_chunks = split_into_morphemes( raw_analysis )
                morpheme_chunk_feats = extract_morpheme_features( morpheme_chunks )
                for mcf_key in morpheme_chunk_feats.keys():
                    if mcf_key == 'morphemes':
                        # convert list to tuple
                        record['morphemes_lemmas'] = tuple(morpheme_chunk_feats['morphemes'])
                    elif mcf_key == 'is_guessed':
                        # aggregate 'is_guessed' feature
                        record[mcf_key] = any( morpheme_chunk_feats[mcf_key] )
                    elif mcf_key == 'has_clitic':
                        # aggregate 'has_clitic' feature
                        record[mcf_key] = any( morpheme_chunk_feats[mcf_key] )
                    elif mcf_key == 'usage':
                        # aggregate 'usage' feature
                        usage = [u for u in morpheme_chunk_feats[mcf_key] if len(u)>0]
                        record[mcf_key] = tuple( usage )
                    else:
                        # convert list to tuple
                        record[mcf_key] = tuple( morpheme_chunk_feats[mcf_key] )
                # Skip guessed word (if required)
                if remove_guesses and record['is_guessed']:
                    continue
                # Add record
                records.append( record )
            elif len(analysis_weight) > 0:
                # Unknown word
                record = self._create_unknown_word_record()
                record['weight'] = float("inf")
                # Add record
                records.append( record )
        return records


    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer, \
                                                  remove_guesses:bool ):
        records = self.extract_annotation_records( output_text, remove_guesses=remove_guesses )
        # TODO: reorder records by their weights
        if len(records) == 0:
            # Empty analysis == unknown word
            record = self._create_unknown_word_record()
            record['weight'] = float("inf")
            # Add annotation to the layer
            layer.add_annotation( word, **record )
            return
        else:
            for record in records:
                layer.add_annotation( word, **record )

