#
# HFST-based morphological analyser for Estonian. [WORK IN PROGRESS]
# This analyser uses a finite-state transducer to look up morphological 
# analyses of the words. The output of the analysis will be ambiguous.
#
# Source code for the Estonian transducer models can be obtained from here:
#     https://victorio.uit.no/langtech/trunk/experiment-langs/est
# Once you have compiled HFST models of this repository, look for file 
# 'src/analyser-gt-desc.hfstol'. This is the file that can be given to 
# HfstEstMorphAnalyser as the transducer model.
# 
# (!) Currently, if you want to use HfstEstMorphAnalyser, you should always
#     make "import hfst" before importing anything from estnltk, or else, you 
#     will later run into a conflict with the Vabamorf package. 
#     Conflict described: if you import estnltk/Vabamorf, and then import hfst, 
#     and then try to use Vabamorf, the Vabamorf gives you a "Segmentation 
#     fault";
#

from typing import MutableMapping, Any
from collections import OrderedDict

import os.path, re

from estnltk import logger

from estnltk.text import Layer, Span, Text
from estnltk.taggers import Tagger

from estnltk.taggers.morph_analysis.morf_common import _get_word_text

import hfst

class HfstEstMorphAnalyser(Tagger):
    """ Hfst-based morphological analyser for Estonian.
        Note: resulting analyses can be ambiguous.
    """
    output_layer='hfst_gt_morph_analysis'
    output_attributes = ()
    conf_param = ['transducer_file',
                  'output_extractor',
                  # Internal components:
                  '_transducer',
                  '_input_words_layer',
                  '_flag_cleaner_re',
                  # For backward compatibility:
                  'depends_on',
                  'attributes' 
                 ]
    attributes = () # For backward compatibility:

    def __init__(self,
                 output_layer:str='hfst_gt_morph_analysis',
                 input_words_layer:str='words',
                 output_format:str='raw',
                 transducer_file:str=None,
                 transducer:hfst.HfstTransducer=None):
        """Initializes HfstEstMorphAnalyser class.
        
        Parameters
        ----------
        output_layer: str (default: 'hfst_gt_morph_analysis')
            Name of the created morphological analysis layer. 

        input_words_layer: str (default: 'words')
            Name of the input words layer;
        
        output_format: str (default: 'raw')
            Specifies how the results of the hfst morphological 
            analysis will be formatted in the layer. Possible 
            options:
            
            * 'raw' -- there will be only two attributes in the
                       layer: 'raw_analysis', which contains 
                       analyses in raw / unparsed format, and 
                       'weight', which contains corresponding 
                       weights (floating point numbers);
            
            * 'morphemes_lemmas' -- the analysis will be split
                       into  morphemes / lemmas,  and   their 
                       corresponding part-of-speech tags  and
                       form listings. In total, each analysis 
                       will have the following attributes:
                          'morphemes'
                          'postags'
                          'forms'
                          'is_guessed',
                          'has_clitic',
                          'usage',
                          'weight'
            
        transducer_file: str (default: None)
            Path to the ('analyser-gt-desc.hfstol') file, from
            which Estonian morphological analyser can be 
            loaded;
            Note: this argument will be overridden by the 
            argument transducer: if the transducer is specified,
            loading it from file will not be attempted;
        
        transducer: hfst.HfstTransducer (default: None)
            An instance of HfstTransducer, which can be used 
            to analyse words for Estonian morphology.
            Note: if provided, then this argument overrides
            the argument transducer_file.
        """
        # Set output_extractor
        self.output_extractor   = None
        expected_output_formats = ['raw', 'morphemes_lemmas']
        if output_format:
            if output_format.lower() == 'raw':
                self.output_extractor = \
                     RawAnalysesHfstMorphOutputExtractor()
            elif output_format.lower() == 'morphemes_lemmas':
                self.output_extractor = \
                     MorphemesLemmasHfstOutputExtractor()
        if self.output_extractor is None:
            # Failed to create output_extractor: probably because wrong output_format
            raise ValueError('(!) output_format should be one of the following: {!r}'.format(expected_output_formats))
        assert isinstance(self.output_extractor, HfstMorphOutputExtractor)
        self.output_extractor.set_output_attributes(self)
        
        # Set attributes & configuration
        self.output_layer = output_layer
        self.input_layers = [ input_words_layer ]
        self._input_words_layer     = self.input_layers[0]
        self.depends_on = self.input_layers
        self.attributes = self.output_attributes
        
        # Utils: create a flag cleaner
        self._flag_cleaner_re = re.compile('@[PNDRCU][.][^@]*@')
        self._transducer = None
        self.transducer_file = None
        
        if transducer:
            # Validate the type of the transducer
            if isinstance(transducer, hfst.HfstTransducer):
                tr_type = transducer.get_type()
                logger.debug( 'Using a transducer of type: {}'.format( hfst.fst_type_to_string(tr_type)) )
                self._transducer = transducer
            else:
                raise TypeError('(!) Argument transducer should be of type hfst.HfstTransducer')
        elif transducer_file:
            if os.path.exists(transducer_file):
                self.transducer_file = transducer_file
                # Second, try to load the transducer from file
                input_stream = hfst.HfstInputStream(transducer_file)
                transducers = []
                while not (input_stream.is_eof()):
                    tr = input_stream.read()
                    assert isinstance(tr, hfst.HfstTransducer)
                    transducers.append(tr)
                    tr_type = tr.get_type()
                    logger.debug( 'Loaded a transducer of type: {}'.format( hfst.fst_type_to_string(tr_type)) )
                    hfst.set_default_fst_type( tr_type )
                input_stream.close()
                assert len(transducers) == 1, \
                       '(!) Expected only one transducer from file {}, but got {}'.format(transducer_file, len(transducers))
                self._transducer = transducers[0]
            else:
                raise FileNotFoundError('(!) Unable to load transducer_file {!r}'.format(transducer_file))


    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict = None) -> Layer:
        """Applies HFST-based morphological analyser on the words layer, 
           captures the output of analyser with output_extractor,  and  
           creates a new  hfst_gt_morph_analysis  layer  based  on  the 
           output.
           
           Parameters
           ----------
           text: Text
              Text object to be analysed.
              
           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain words layer. 
              The  hfst_gt_morph_analysis  layer will be created.
              
           status: dict
              This can be used to store metadata on layer tagging.
        """
        assert self._transducer is not None, \
               '(!) Transducer was not initialized in the constructor of '+\
               self.__class__.__name__+'. Please create a new instance and '+\
               'initialize transducer properly.'

        new_layer = Layer(name=self.output_layer,
                               parent=self._input_words_layer,
                               text_object=text,
                               ambiguous=True,
                               attributes=self.output_attributes
        )
        for word in layers[ self._input_words_layer ]:
            word_str = _get_word_text(word)
            raw_analyses = self._transducer.lookup( word_str, output='text' )
            # Remove flag diacritics
            cleaned_analyses = self.filter_flags(raw_analyses)
            # Use output_extractor for getting the output
            self.output_extractor.extract_annotation_and_add_to_layer( \
                        word, cleaned_analyses, new_layer )
        return new_layer


    def lookup(self, input_word:str):
        """ Analyses a singe word with the transducer. Returns a list of records 
            (dictionaries), where each record corresponds to a single analysis 
            from the transducer's output.
            In case of an unknown word, returns an empty list;
            
            Use this method if you need to selectively analyse words: e.g. analyse
            only some specific words, but not all words of the text.
        """
        assert self._transducer is not None, \
               '(!) Transducer was not initialized in the constructor of '+\
               self.__class__.__name__+'. Please create a new instance and '+\
               'initialize transducer properly.'
        raw_analyses = self._transducer.lookup( input_word, output='text' )
        # Remove flag diacritics
        cleaned_analyses = self.filter_flags(raw_analyses)
        # Use output_extractor for getting the output
        return self.output_extractor.extract_annotation_records( cleaned_analyses )


    def filter_flags(self, o_str):
        """ Cleans the output string of the transducer from flag diacritics.
        """
        return self._flag_cleaner_re.sub('', o_str)


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
    
    def extract_annotation_records(self, output_text:str ):
        """ Given an output of the HFST transducer, extracts morph analysis records from the 
            output, and returns as a list (of dictionaries). In case of an unknown word, returns 
            an empty list.
        """
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer ):
        """ Given word Span and the corresponding output of the HFST transducer, 
            extracts morph analysis records from the output, and saves as annotatons 
            of the layer. Note: implementations of this method should use extractor's 
            method extract_annotation_records() for getting the records;
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

    def extract_annotation_records(self, output_text:str ):
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
                # Add annotation to the layer
                records.append( record )
            elif len(analysis_weight) > 0:
                # Unknown word
                record['weight'] = float("inf")
                record['raw_analysis'] = None
                # Add annotation to the layer
                records.append( record )
        return records


    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer ):
        records = self.extract_annotation_records( output_text )
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
    "+N", "+N+Prop", "+A", "+A+Comp", "+A+Superl", "+Num+Card", "+Num+Ord", "+Pron", "+ACR",\
    # NonInflectingPOS 
    "+Adv", "+Interj", "+CC", "+CS", "+Adp", "+Pref", "+CLB",\
    # VPOS 
    "+V" ]

# Separates one component of a derivative from another
est_hfst_derivative_strs = ['+Der/', '+Dim/']

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
                locations.append( (start, cid) )
                start = cid+len(cp) # next start position
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
    postags_regexp = '('+ postags_regexp.replace('+','\+') +')'
    return re.compile(postags_regexp)

est_hfst_postags_pattern = _compile_postags_pattern()

def _compile_usage_strs_pattern():
    """ Creates regexp for capturing part-of-speech tags 
        from the output of HFST lookup. """
    sorted_usage_strs = sorted(est_hfst_usage_strs, key=lambda x: (-len(x), x))
    usage_strs_regexp = '|'.join(sorted_usage_strs)
    usage_strs_regexp = '('+ usage_strs_regexp.replace('+','\+') +')'
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
        analysisExtracted = False
        is_guessed = False
        # Try to extract a guessing label
        for guess in est_hfst_guess_strs:
            if chunk_str.endswith(guess):
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
        For each morpheme (or lemma), it also extracts corresponding postag, 
        and a form category. Results are stored in tuples, so that the same 
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
           here may, in some cases, also be a lemma of a word. 
    """

    def set_output_attributes(self, tagger:Tagger):
        # Update Tagger's output attributes
        tagger.output_attributes = ('morphemes','postags','forms','is_guessed','has_clitic','usage','weight')


    def _create_unknown_word_record(self):
        # Creates a record for an unknown word
        features = dict()
        features['morphemes']  = None
        features['postags']    = None
        features['forms']      = None
        features['is_guessed'] = None
        features['has_clitic'] = None
        features['usage']      = None
        return features


    def extract_annotation_records(self, output_text:str ):
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
                        record['morphemes'] = tuple(morpheme_chunk_feats['morphemes'])
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
                # Add record
                records.append( record )
            elif len(analysis_weight) > 0:
                # Unknown word
                record = self._create_unknown_word_record()
                record['weight'] = float("inf")
                # Add record
                records.append( record )
        return records


    def extract_annotation_and_add_to_layer(self, word:Span, output_text:str, layer:Layer ):
        records = self.extract_annotation_records( output_text )
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

