#
# HFST-based morphological analyser for Estonian. [WORK IN PROGRESS]
# This analyser uses a finite-state transducer to look up morphological 
# analyses of the words. The output of the analysis will be ambiguous.
#
# Source code for the Estonian transducer models can be obtained from here:
#     https://victorio.uit.no/langtech/trunk/experiment-langs/est
# Once you have compiled HFST models in this repository, look for file 
# 'src/analyser-gt-desc.hfstol'. This is the file that can be given to 
# HfstEstMorphAnalyser as the transducer model.
# 
# (!) Currently, if you want to use HfstEstMorphAnalyser, you should always
#     make "import hfst" before importing anything from estnltk, or else, you 
#     will later run into a conflict with the Vabamorf package. 
#     Conflict explained: if you import Vabamorf, then import hfst, and then 
#     try to use Vabamorf, then the Vabamorf gives you a "Segmentation fault";
#

from typing import MutableMapping, Any

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
        expected_output_formats = ['raw']
        if output_format:
            if output_format.lower() == 'raw':
                self.output_extractor = \
                     RawAnalysesHfstMorphOutputExtractor()
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
            self.output_extractor.extract_annotation_from_output( \
                        word, cleaned_analyses, new_layer )
        return new_layer



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
    
    def extract_annotation_from_output(self, word:Span, output_text:str, layer:Layer ):
        """ Given word Span and the corresponding output of the HFST transducer, 
            extracts morph analysis records from the output, and saves as annotatons 
            of the layer.
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

    def extract_annotation_from_output(self, word:Span, output_text:str, layer:Layer ):
        if len(output_text) == 0:
            # Empty analysis == unknown word
            record = {}
            record['weight'] = float("inf")
            record['raw_analysis'] = None
            # Add annotation to the layer
            layer.add_annotation( word, **record )
            return
        for analysis_weight in output_text.split('\n'):
            record = {}
            if '\t' in analysis_weight:
                # Known word
                analysis, weight = analysis_weight.split('\t')
                record['weight'] = float(weight)
                record['raw_analysis'] = analysis
                # Add annotation to the layer
                layer.add_annotation( word, **record )
            elif len(analysis_weight) > 0:
                # Unknown word
                record['weight'] = float("inf")
                record['raw_analysis'] = None
                # Add annotation to the layer
                layer.add_annotation( word, **record )

