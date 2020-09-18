#
# Hfst morphological analyser for Estonian (based on HFST Python bindings)
# This analyser uses a finite-state transducer to look up morphological 
# analyses of the words. The output of the analysis will be ambiguous.
#

import hfst

from typing import MutableMapping
from collections import OrderedDict

import os.path
import re

from estnltk import logger

from estnltk.text import Layer, Text
from estnltk.layer.span import Span
from estnltk.taggers import Tagger

from estnltk.taggers.morph_analysis.morf_common import _get_word_texts

from estnltk.taggers.morph_analysis.hfst.hfst_morph_common import HFST_MODEL_FILE
from estnltk.taggers.morph_analysis.hfst.hfst_morph_common import HfstMorphOutputExtractor
from estnltk.taggers.morph_analysis.hfst.hfst_morph_common import RawAnalysesHfstMorphOutputExtractor
from estnltk.taggers.morph_analysis.hfst.hfst_morph_common import MorphemesLemmasHfstOutputExtractor


class HfstMorphAnalyser(Tagger):
    """ Hfst morphological analyser for Estonian (based on HFST Python bindings)
        Note: resulting analyses can be ambiguous.
    """
    output_layer='hfst_gt_morph_analysis'
    output_attributes = ()
    conf_param = ['transducer_file',
                  'output_extractor',
                  'remove_guesses',
                  # Internal components:
                  '_transducer',
                  '_input_words_layer',
                  '_flag_cleaner_re',
                 ]

    def __init__(self,
                 output_layer:str='hfst_gt_morph_analysis',
                 input_words_layer:str='words',
                 output_format:str='morphemes_lemmas',
                 transducer_file:str=HFST_MODEL_FILE,
                 transducer:hfst.HfstTransducer=None,
                 remove_guesses:bool=False):
        """Initializes HfstMorphAnalyser class.
        
        Parameters
        ----------
        output_layer: str (default: 'hfst_gt_morph_analysis')
            Name of the created morphological analysis layer. 

        input_words_layer: str (default: 'words')
            Name of the input words layer;
        
        output_format: str (default: 'morphemes_lemmas')
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
                          'morphemes_lemmas'
                          'postags'
                          'forms'
                          'is_guessed',
                          'has_clitic',
                          'usage',
                          'weight'
            
        transducer_file: str
            Path to the ('analyser-gt-desc.hfstol') file, from
            which Estonian morphological analyser can be 
            loaded;
            Note: this argument will be overridden by the 
            argument transducer: if the transducer is specified
            (default), then loading it from file will not be 
            attempted;
            ( default file: 
                estnltk\taggers\morph_analysis\hfst\models\analyser-gt-desc.hfstol )
        
        transducer: hfst.HfstTransducer (default: None)
            An instance of HfstTransducer, which can be used 
            to analyse words for Estonian morphology.
            Note: if provided, then this argument overrides
            the argument transducer_file.
        
        remove_guesses:bool (default: False)
            Specifies if guessed analyses need to be removed 
            from the output.
            By default, the guessed analyses will be kept in 
            the output, but this also depends on the transducer.
            ( our default transducer model has the guesser 
              component, so it produces guesses. but you can 
              also compile a model without the component )
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
        self.remove_guesses = remove_guesses
        
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
            # Collect analyses for all normalized variants of the word
            all_raw_analyses = []
            for word_str in _get_word_texts(word):
                raw_analyses = self._transducer.lookup( word_str, output='text' )
                all_raw_analyses.append( raw_analyses )
            # Remove flag diacritics
            cleaned_analyses = self.filter_flags( '\n'.join(all_raw_analyses) )
            # Use output_extractor for getting the output
            self.output_extractor.extract_annotation_and_add_to_layer( \
                                word, cleaned_analyses, new_layer, \
                                remove_guesses = self.remove_guesses )
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
        return self.output_extractor.extract_annotation_records( cleaned_analyses, \
                                             remove_guesses = self.remove_guesses  )


    def filter_flags(self, o_str):
        """ Cleans the output string of the transducer from flag diacritics.
        """
        return self._flag_cleaner_re.sub('', o_str)


