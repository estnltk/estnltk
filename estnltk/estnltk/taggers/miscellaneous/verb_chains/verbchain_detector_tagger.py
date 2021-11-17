#
#   Verb chain detector finds main verbs and their extensions 
#  (verb chains) from clauses.
#
#   Note: This is simply a wrapper around the verb chain detector
#   source from EstNLTK v1.4.1. Because of that, it includes
#   some processing overhead as it needs to convert v1.6 data to 
#   the version 1.4.1 data structures (and back).
#

import os.path

# Interface of the version 1.6
from estnltk import Text, Layer
from estnltk.taggers import Tagger

# Converting morphological analysis structures from v1.6 to v1.4.1
from estnltk.taggers.standard.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# Verb chain detector functionality from the version 1.4.1
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.verbchain_detector import VerbChainDetectorV1_4
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import CLAUSE_IDX

# Path to the verb chain detector's resources
from estnltk.common import PACKAGE_PATH
VERB_CHAIN_RES_PATH = os.path.join(PACKAGE_PATH, 'taggers', 'miscellaneous', 'verb_chains', 'v1_4_1', 'res')


class VerbChainDetector( Tagger ):
    """Tags main verbs and their extensions (verb chains) in clauses. ( v1.4.1 )
       Note: this is simply a wrapper around v1.4.1 verb chain 
       detector. Because of that, it includes some processing 
       overhead due to converting v1.6 data to the version 1.4.1 
       data structures (and back).
    """
    output_layer      = 'verb_chains'
    output_attributes = ('pattern', 'roots', 'word_ids', \
                         'mood', 'polarity', 'tense', 'voice', \
                         'remaining_verbs' )
    input_layers      = ['words', 'sentences', 'morph_analysis', 'clauses']
    conf_param = [ # Additional output attributes:
                   'add_morph_attr',
                   'add_analysis_ids_attr',
                   # Detector arguments from the version 1.4.1:
                   'expand2ndTime',      
                   'breakOnPunctuation', 
                   'removeSingleAraEi',  
                   # Names of specific input layers:
                   '_input_words_layer',
                   '_input_clauses_layer',
                   '_input_sentences_layer',
                   '_input_morph_analysis_layer',
                   # Inner parameters:
                   '_resources_dir',
                   '_verb_chain_detector',
                 ]

    def __init__( self,
                  output_layer:str='verb_chains',
                  input_words_layer:str='words',
                  input_clauses_layer:str='clauses',
                  input_sentences_layer:str='sentences',
                  input_morph_analysis_layer:str='morph_analysis',
                  resources_dir:str=VERB_CHAIN_RES_PATH,
                  add_morph_attr:bool=False,
                  add_analysis_ids_attr:bool=False,
                  expand2ndTime:bool=False,
                  breakOnPunctuation:bool=False,
                  removeSingleAraEi:bool=True,
                  vc_detector:VerbChainDetectorV1_4=None):
        """Initializes VerbChainDetector.
        
        Parameters
        ----------
        output_layer: str (default: 'verb_chains')
            Name for the verb chains layer;
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_clauses_layer: str (default: 'clauses')
            Name of the input clauses layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        input_morph_analysis_layer: str (default: 'morph_analysis')
            Name of the input morph_analysis layer;
        resources_dir: str (default: PACKAGE_PATH/taggers/miscellaneous/verb_chains/v1_4_1/res )
            The path to the resource files (path to the 'res' directory);
        add_morph_attr: boolean (default: False)
            If attribute 'morph' will be added to the output layer.
            This attribute contains detailed morphological information
            (part-of-speech + form) for each of the detected words.
        add_analysis_ids_attr: boolean (default: False)
            If attribute 'analysis_ids' will be added to the output 
            layer.
            For each word in the chain, this attribute tells which of 
            the morphological analyses (analysis ID-s) of the word had 
            features of the verb chain. 
            ( this attribute helps to distinguish verb chain's 
              morphological analyses in case of ambiguities )
        expand2ndTime: boolean (default: False)
            If True, regular verb chains (chains not ending with 'olema') are expanded twice.
        breakOnPunctuation: boolean (default: False)
            If True, expansion of regular verb chains will be broken in case of intervening punctuation.
        removeSingleAraEi: boolean (default: True)
            if True, verb chains consisting of a single word, 'ära' or 'ei', will be removed.
        vc_detector: estnltk.taggers.miscellaneous.verb_chains.v1_4_1.verbchain_detector.VerbChainDetector 
            (default: None)
            Overrides the default verb chain detector with the given 
            VerbChainDetector instance. 
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_clauses_layer        = input_clauses_layer
        self._input_sentences_layer      = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [ input_words_layer, input_sentences_layer, \
                              input_morph_analysis_layer, input_clauses_layer ]
        # Configuration
        self.add_morph_attr = add_morph_attr
        self.add_analysis_ids_attr = add_analysis_ids_attr
        cur_output_attributes = ()
        for attr in VerbChainDetector.output_attributes:
            cur_output_attributes += ( attr, )
            if self.add_morph_attr and attr == 'roots':
                # add morph attr (if required)
                cur_output_attributes += ( 'morph', )
            if self.add_analysis_ids_attr and attr == 'word_ids':
                # add analysis_ids attr (if required)
                cur_output_attributes += ( 'analysis_ids', )
        self.expand2ndTime      = expand2ndTime
        self.breakOnPunctuation = breakOnPunctuation
        self.removeSingleAraEi  = removeSingleAraEi
        self.output_attributes = cur_output_attributes
        # Initialize v1.4.1 vc detector
        if vc_detector is None:
            self._resources_dir = resources_dir
            self._verb_chain_detector = \
                VerbChainDetectorV1_4(resourcesPath=self._resources_dir)
        else:
            # Use a custom VerbChainDetector
            assert isinstance(vc_detector, VerbChainDetectorV1_4), \
                '(!) vc_detector should be an instance of VerbChainDetectorV1_4!'
            self._verb_chain_detector = vc_detector

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     enveloping=self._input_words_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     ambiguous=False)

    def _make_layer(self, text, layers, status: dict):
        """Tags verb chains layer.
        
        Parameters
        ----------
        text: Text
           Text in which verb chains will be tagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the words, clauses, sentences and morph_analysis 
           layers.
          
        status: dict
           This can be used to store metadata on layer tagging.

        """
        layer = self._make_layer_template()
        layer.text_object = text

        word_spans    = layers[ self._input_words_layer ]
        morph_spans   = layers[ self._input_morph_analysis_layer ]
        clauses_spans = layers[ self._input_clauses_layer ]
        assert len(morph_spans) == len(word_spans)
        # Process input sentence-by-sentence:
        # *) convert input to v1.4.1 data format;
        # *) detect chains with VerbChainDetector from v1.4.1;
        # *) convert output back to v1.6 data format;
        word_span_id = 0
        clause_id = 0
        for sentence in layers[self._input_sentences_layer]:
            sent_start = sentence.start
            sent_end = sentence.end
            
            # A) Collect all clauses inside the current sentence 
            current_clauses = []
            while clause_id < len(clauses_spans):
                clause   = clauses_spans[clause_id]
                cl_start = clause.start
                cl_end   = clause.end
                if sent_start <= cl_start and cl_end <= sent_end:
                    current_clauses.append( clause )
                    clause_id += 1
                if sent_end <= cl_start:
                    break
            
            # B) Collect all words/morph_analyses inside the sentence
            #    Assume: len(word_spans) == len(morph_spans)
            sentence_morph_dicts = []
            sentence_words       = []
            sentence_word_ids    = []
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                morph_span = None
                if sent_start <= word_span.start and \
                    word_span.end <= sent_end:
                    morphFound = False
                    # Get corresponding morph span
                    if word_span_id < len(morph_spans):
                        morph_span = morph_spans[word_span_id]
                        if word_span.base_span == morph_span.base_span and \
                           len(morph_span.annotations) > 0 and \
                           not _is_empty_annotation(morph_span.annotations[0]):
                            # Convert span to Vabamorf dict
                            word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict(
                                        morph_span )
                            sentence_morph_dicts.append( word_morph_dict )
                            morphFound = True
                    if not morphFound:
                        # No morph found: add an empty Vabamorf dict
                        empty_analysis_dict = { 'text' : word_span.text, \
                                                'analysis' : [] }
                        sentence_morph_dicts.append( empty_analysis_dict )
                    sentence_words.append( word_span )
                    sentence_word_ids.append( word_span_id )
                if sent_end <= word_span.start:
                    # Break (end of the sentence)
                    break
                word_span_id += 1
        
            # C) Add a clause_id to each word 
            #    ( basically: group words by clauses )
            cur_clause_id = 0
            for wid, word_span in enumerate( sentence_words ):
                word_morph_dict = sentence_morph_dicts[wid]
                parent_clause_id = None
                while cur_clause_id < len( current_clauses ):
                    clause   = current_clauses[cur_clause_id]
                    cl_start = clause.start
                    cl_end = clause.end
                    if cl_start <= word_span.start and \
                       word_span.end <= cl_end:
                        parent_clause_id = cur_clause_id
                        break
                    if cl_end <= word_span.start:
                        cur_clause_id += 1
                assert parent_clause_id is not None, \
                    '(!) Unable to find the parent clause of the word: {!r}'.format(word_morph_dict)
                word_morph_dict[CLAUSE_IDX] = parent_clause_id
            
            # D) Detect verb chains (the output will be dicts)
            verb_chain_dicts = \
                self._verb_chain_detector.detectVerbChainsFromSent( sentence_morph_dicts,
                                                expand2ndTime = self.expand2ndTime,
                                                breakOnPunctuation = self.breakOnPunctuation,
                                                removeSingleAraEi = self.removeSingleAraEi)
            
            # E) Convert dictionaries to EnvelopingSpan-s
            for vc in verb_chain_dicts:
                layer.add_annotation([sentence_words[wid].base_span for wid in sorted(vc['phrase'])],
                                     polarity=vc['pol'],
                                     pattern=vc['pattern'],
                                     roots=vc['roots'],
                                     mood=vc['mood'],
                                     tense=vc['tense'],
                                     voice=vc['voice'],
                                     word_ids=[sentence_word_ids[wid] for wid in vc['phrase']],
                                     remaining_verbs=vc['other_verbs'],
                                     morph=vc['morph'],
                                     analysis_ids=vc['analysis_ids'])

        # Small sanity check: all clauses and words should be exhausted by now 
        assert clause_id == len(clauses_spans)
        assert word_span_id == len(word_spans)
        
        return layer

