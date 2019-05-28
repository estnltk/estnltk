#
#  VabamorfTagger that operates on a corpus of Text objects, and includes corpus-based disambiguation.
#  Includes the following substeps of morphological processing:
#    1) Vabamorf's morphological analysis (VabamorfAnalyzer);
#    2) post-corrections to morphological analysis (PostMorphAnalysisTagger);
#    3) corpus-based pre-disambiguation (CorpusBasedMorphDisambiguator);
#    4) Vabamorf's statistical disambiguation (VabamorfDisambiguator);
#    5) corpus-based post-disambiguation (CorpusBasedMorphDisambiguator);
#

import re
from collections import defaultdict, OrderedDict

from estnltk.text import Text, Layer
from estnltk.taggers import Tagger, Retagger

from estnltk.layer.ambiguous_attribute_tuple_list import to_str

from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.morf import VabamorfDisambiguator
from estnltk.taggers.morph_analysis.postanalysis_tagger import PostMorphAnalysisTagger
from estnltk.taggers.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES

from estnltk.taggers.morph_analysis.cb_disambiguator import CorpusBasedMorphDisambiguator
from estnltk.taggers.morph_analysis.cb_disambiguator import is_list_of_texts
from estnltk.taggers.morph_analysis.cb_disambiguator import is_list_of_lists_of_texts


class VabamorfCorpusTagger( object ):
    """ VabamorfTagger that operates on a corpus of Text objects, and includes corpus-based disambiguation.
        
        Includes the following substeps of morphological processing:
         1) Vabamorf's morphological analysis (VabamorfAnalyzer);
         2) post-corrections to morphological analysis (PostMorphAnalysisTagger);
         3) corpus-based pre-disambiguation (CorpusBasedMorphDisambiguator);
         4) Vabamorf's statistical disambiguation (VabamorfDisambiguator);
         5) corpus-based post-disambiguation (CorpusBasedMorphDisambiguator);
    """
    
    def __init__(self,
                 morph_analysis_layer:str='morph_analysis',
                 input_words_layer:str='words',
                 input_sentences_layer:str='sentences',
                 input_compound_tokens_layer='compound_tokens',
                 validate_inputs:bool=True,
                 # switch analysis steps on/off
                 use_predisambiguation:bool=True,
                 use_postanalysis:bool=True,
                 use_vabamorf_disambiguator:bool=True,
                 use_postdisambiguation:bool=True,
                 # customize taggers
                 vabamorf_analyser:VabamorfAnalyzer=None, 
                 postanalysis_tagger:Retagger=None, 
                 vabamorf_disambiguator:VabamorfDisambiguator=None,
                 cb_disambiguator:CorpusBasedMorphDisambiguator=None ):
        """Initialize CorpusBasedMorphDisambiguator class.

        Parameters
        ----------
        morph_analysis_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer. 
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input compound_tokens layer. 
            This layer is required by the default postanalysis_tagger.
        validate_inputs : bool (default: True)
            If set (default), then input document collection will 
            be validated for having the appropriate structure, and 
            all documents will be checked for the existence of 
            required layers.
        use_predisambiguation : bool (default: True)
            If set (default), then corpus-based pre-disambiguation 
            of proper names will be applied;
        use_postanalysis : bool (default: True)
            If set (default), then postanalysis corrections will 
            be applied using the given postanalysis_tagger (if set),
            or the default PostMorphAnalysisTagger().
            Otherwise, not postanalysis corrections will be made.
        use_vabamorf_disambiguator : bool (default: True)
            If set (default), then vabamorf's statistical disambiguation
            will be applied using the given vabamorf_disambiguator
            (if set), or the default VabamorfDisambiguator.
            Otherwise, vabamorf's statistical disambiguation will not 
            be applied at all.
        use_postdisambiguation : bool (default: True)
            If set (default), then corpus-based post-disambiguation 
            step will be applied;
        vabamorf_analyser : VabamorfAnalyzer (default: VabamorfAnalyzer())
            Argument for overriding the default vabamorf analyser used
            by this corpus tagger;
            If not set (default), then the default vabamorf analyser is 
            initialized and used for the process.
        postanalysis_tagger: estnltk.taggers.Retagger (default: PostMorphAnalysisTagger())
            Argument for overriding the default post-analysis tagger used
            by this corpus tagger;
            It must be a Retagger that corrects morphological analyses, and 
            prepares morphological analyses for vabamorf's disambiguation 
            (if required).
            If not set (default), then the default post-analysis tagger is 
            initialized and used for the process.
            Note: the tagger will only be applied if use_postanalysis==True,
            regardless the value of this setting;
        vabamorf_disambiguator : VabamorfDisambiguator (default: VabamorfDisambiguator())
            Argument for overriding the default vabamorf disambiguator used
            by this corpus tagger;
            If not set (default), then the default vabamorf disambiguator is 
            initialized and used for the process.
            Note: the disambiguator will only be applied if 
            use_vabamorf_disambiguator==True, regardless the value of this setting;
        cb_disambiguator : CorpusBasedMorphDisambiguator (default: CorpusBasedMorphDisambiguator())
            Argument for overriding the default corpus-based disambiguator used
            by this corpus tagger;
            If not set (default), then the default corpus-based disambiguator is 
            initialized and used for the process.
            Note: the disambiguator will only be applied if either
            use_postdisambiguation or use_predisambiguation is True, regardless 
            the value of this setting;
        """
        # Set attributes & configuration
        self.input_layers = [ input_words_layer, \
                              input_sentences_layer ]
        self._input_words_layer      = input_words_layer
        self._input_sentences_layer  = input_sentences_layer
        self._morph_analysis_layer   = morph_analysis_layer
        self._use_predisambiguation  = use_predisambiguation
        self._use_postdisambiguation = use_postdisambiguation
        self._validate_inputs        = validate_inputs
        self.output_attributes       = ESTNLTK_MORPH_ATTRIBUTES
        # Initialize required taggers
        #
        # A) VabamorfAnalyzer (we always need it)
        #
        vm_instance = None
        self._vabamorf_analyser = None
        if not vabamorf_analyser:
            vm_instance = Vabamorf.instance()
            self._vabamorf_analyser = VabamorfAnalyzer( vm_instance=vm_instance,
                                                        layer_name=morph_analysis_layer,
                                                        input_words_layer=input_words_layer,
                                                        input_sentences_layer=input_sentences_layer)
        else:
            # Use given VabamorfAnalyzer
            assert isinstance(vabamorf_analyser, VabamorfAnalyzer)
            assert vabamorf_analyser.layer_name == morph_analysis_layer, \
                '(!) vabamorf_analyser should modify layer "'+str(morph_analysis_layer)+'".'+\
                ' Currently, it modifies layer "'+str(vabamorf_analyser.layer_name)+'".'
            self._vabamorf_analyser = vabamorf_analyser
            # Get vm instance from VabamorfAnalyzer
            vm_instance = self._vabamorf_analyser.vm_instance
        # Add new dependencies from VabamorfAnalyzer (if there are any)
        if self._vabamorf_analyser is not None:
            for vm_dependency in self._vabamorf_analyser.depends_on:
                if vm_dependency not in self.input_layers and \
                   vm_dependency != morph_analysis_layer:
                    self.input_layers.append( vm_dependency )
        #
        # B) PostMorphAnalysisTagger (can be turned off)
        #
        if use_postanalysis and not postanalysis_tagger:
            # Initialize default postanalysis_tagger
            self._postanalysis_tagger = PostMorphAnalysisTagger(output_layer=morph_analysis_layer,\
                                                 input_compound_tokens_layer=input_compound_tokens_layer, \
                                                 input_words_layer=input_words_layer, \
                                                 input_sentences_layer=input_sentences_layer )
        elif use_postanalysis and postanalysis_tagger:
            # Use a custom PostMorphAnalysisTagger
            # Check for Retagger
            assert isinstance(postanalysis_tagger, Retagger), \
                '(!) postanalysis_tagger should be of type estnltk.taggers.Retagger.'
            # Check for layer match
            assert hasattr(postanalysis_tagger, 'output_layer'), \
                '(!) postanalysis_tagger does not define output_layer.'
            assert postanalysis_tagger.output_layer == morph_analysis_layer, \
                '(!) postanalysis_tagger should modify layer "'+str(morph_analysis_layer)+'".'+\
                ' Currently, it modifies layer "'+str(postanalysis_tagger.output_layer)+'".'
            self._postanalysis_tagger = postanalysis_tagger
        else:
            # Sry, no post analysis this time
            self._postanalysis_tagger = None
        # Add new dependencies from post-analysis tagger
        if self._postanalysis_tagger is not None:
            for postanalysis_dependency in self._postanalysis_tagger.input_layers:
                if postanalysis_dependency not in self.input_layers and \
                   postanalysis_dependency != morph_analysis_layer:
                    self.input_layers.append( postanalysis_dependency )
        #
        # C) VabamorfDisambiguator (can be turned off for testing purposes)
        #
        if use_vabamorf_disambiguator and not vabamorf_disambiguator:
            # Initialize default vabamorf disambiguator
            self._vabamorf_disambiguator = VabamorfDisambiguator( vm_instance=vm_instance,
                                                                  output_layer=morph_analysis_layer,
                                                                  input_words_layer=input_words_layer,
                                                                  input_sentences_layer=input_sentences_layer )
        elif use_vabamorf_disambiguator and vabamorf_disambiguator:
            # Use custom vabamorf disambiguator
            assert isinstance(vabamorf_disambiguator, VabamorfDisambiguator), \
                '(!) vabamorf_disambiguator should be an instance of VabamorfDisambiguator.'
            assert vabamorf_disambiguator.output_layer == morph_analysis_layer, \
                '(!) vabamorf_disambiguator should modify layer "'+str(morph_analysis_layer)+'".'+\
                ' Currently, it modifies layer "'+str(vabamorf_disambiguator.output_layer)+'".'
            self._vabamorf_disambiguator = vabamorf_disambiguator
        else:
            # Sry, no vm disambiguation this time
            self._vabamorf_disambiguator = None
        # Add new dependencies from VabamorfDisambiguator (if there are any)
        if self._vabamorf_disambiguator is not None:
            for vm_dependency in self._vabamorf_disambiguator.input_layers:
                if vm_dependency not in self.input_layers and \
                   vm_dependency != morph_analysis_layer:
                    self.input_layers.append( vm_dependency )
        #
        # D) CorpusBasedMorphDisambiguator
        #
        if cb_disambiguator is None:
            # Initialize default CorpusBasedMorphDisambiguator
            self._cb_disambiguator = \
                 CorpusBasedMorphDisambiguator( 
                       morph_analysis_layer  = morph_analysis_layer,
                       input_words_layer     = self._input_words_layer,
                       input_sentences_layer = self._input_sentences_layer,
                       validate_inputs = validate_inputs )
        else:
            # Use custom CorpusBasedMorphDisambiguator
            assert isinstance(cb_disambiguator, CorpusBasedMorphDisambiguator), \
                '(!) cb_disambiguator should be an instance of CorpusBasedMorphDisambiguator.'
            assert cb_disambiguator.morph_analysis_layer == morph_analysis_layer, \
                '(!) cb_disambiguator should modify layer "'+str(morph_analysis_layer)+'".'+\
                ' Currently, it modifies layer "'+str(cb_disambiguator.morph_analysis_layer)+'".'
            self._cb_disambiguator = cb_disambiguator
        # Add new dependencies from CorpusBasedMorphDisambiguator (if there are any)
        if self._cb_disambiguator is not None:
            for cbd_dependency in self._cb_disambiguator.input_layers:
                if cbd_dependency not in self.input_layers and \
                   cbd_dependency != morph_analysis_layer:
                    self.input_layers.append( cbd_dependency )



    def tag( self, docs:list ):
        """ Processes given corpus of documents morphologically.
            By default, the morphological processing includes: 
            1) Vabamorf's morphological analysis;
            2) post-corrections to morphological analysis;
            3) corpus-based pre-disambiguation;
            4) Vabamorf's statistical disambiguation;
            5) corpus-based post-disambiguation;
            The corpus can be either:
              a) a list of Text objects;
              b) a list of lists of Text objects;
        """
        # 0) Determine input structure & validate inputs
        in_docs = []
        input_format = None
        if is_list_of_texts( docs ):
            input_format = 'I'
        elif is_list_of_lists_of_texts( docs ):
            input_format = 'II'
        if input_format in ['I', 'II'] and len(docs) == 0:
            input_format = '0'
        if input_format == 'I':
            in_docs = [ docs ]
        else:
            in_docs = docs
        if self._validate_inputs:
            # Validate input structure
            assert input_format is not None, \
                   '(!) Unexpected input structure. Input argument collections should be '+\
                   'either a list of Text objects, or a list of lists of Text objects.'
            # Validate input Texts for required layers
            for c_docs in in_docs:
                self._validate_docs_for_required_layers( c_docs )
        # 1) Perform regular morphological analysis and post-analysis
        for collection in in_docs:
            for doc in collection:
                self._vabamorf_analyser.tag( doc )
                if self._postanalysis_tagger is not None:
                    self._postanalysis_tagger.retag( doc )
        # 2) Perform corpus-based pre-disambiguation
        if self._use_predisambiguation:
            self._cb_disambiguator.predisambiguate( in_docs )
        # 3) Perform vabamorf's disambiguation
        if self._vabamorf_disambiguator:
            for collection in in_docs:
                for doc in collection:
                    self._vabamorf_disambiguator.retag( doc )
        # 4) Perform corpus-based post-disambiguation
        if self._use_postdisambiguation:
            self._cb_disambiguator.postdisambiguate( in_docs )
        return docs



    def _validate_docs_for_required_layers( self, docs:list ):
        """ Checks that all documens have the layers required
            by this corpus tagger.  If  one  of  the documents 
            in the collection misses some of the layers, raises
            an expection.
        """
        assert isinstance(docs, list)
        required_layers = self.input_layers
        for doc_id, doc in enumerate( docs ):
            assert isinstance(doc, Text)
            missing = []
            for layer in required_layers:
                if layer not in doc.layers.keys():
                    missing.append( layer )
            if missing:
                raise Exception('(!) {!r} is missing layers: {!r}'.format(doc, missing))


    def _get_morph_pipeline_taggers(self):
        """ Returns taggers and components that are applied in the morphological
            analysis pipeline of this corpus tagger.
            Parameters are returned in an OrderedDict, which roughly represents 
            the order in which taggers and components are applied.
        """
        conf_mappings = OrderedDict()
        conf_mappings['vabamorf_analyser'] = self._vabamorf_analyser
        conf_mappings['postanalysis_tagger'] = self._postanalysis_tagger
        conf_mappings['vabamorf_disambiguator'] = self._vabamorf_disambiguator
        conf_mappings['cb_disambiguator'] = self._cb_disambiguator
        return conf_mappings


    def _reconstruct_morph_pipeline_params(self):
        """ Reconstructs parameters that turn on/off steps in the morphological
            analysis pipeline of this corpus tagger.
            Parameters are returned in an OrderedDict, which represent the order 
            of steps.
            Note: returns also a parameter named '*use_analysis', but this cannot
            be changed in the constructor;
        """
        conf_mappings = OrderedDict()
        conf_mappings['*use_analysis'] = self._vabamorf_analyser is not None
        conf_mappings['use_postanalysis'] = self._postanalysis_tagger is not None
        conf_mappings['use_predisambiguation'] = self._use_predisambiguation
        conf_mappings['use_vabamorf_disambiguator'] = self._vabamorf_disambiguator is not None
        conf_mappings['use_postdisambiguation'] = self._use_postdisambiguation
        return conf_mappings


    def __repr__(self):
        conf_str = ''
        conf_str = 'input_layers=['+(', '.join([l for l in self.input_layers]))+']'
        conf_str += ', output_layer='+self._morph_analysis_layer
        return self.__class__.__name__ + '(' + conf_str + ')'


    def _repr_html_(self):
        # Add description
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        parameters = {'output layer': self._morph_analysis_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['output layer', 'output attributes', 'input layers'],
                                 index=[0])
        table = table.to_html(index=False)
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>'+self.__class__.__name__+'</h4>', description, table]
        # Add configuration parameters
        # 1) add general parameters
        public_param = ['validate_inputs']
        conf_values  = []
        for attr in public_param:
            conf_values.append( str(getattr(self, '_'+attr)) )
        # 2) add pipeline's configuration parameters
        pipeline_parameters = self._reconstruct_morph_pipeline_params()
        for (key, value) in pipeline_parameters.items():
            if not key.startswith('*'):
                public_param.append(key)
                conf_values.append(value)
        # 3) add tagger's and components
        pipeline_components = self._get_morph_pipeline_taggers()
        for (key, value) in pipeline_components.items():
            public_param.append(key)
            conf_values.append(to_str(value))
        conf_table = pandas.DataFrame(conf_values, index=public_param)
        conf_table = conf_table.to_html(header=False)
        conf_table = ('<h4>Configuration</h4>', conf_table)
        table.extend( conf_table )
        return '\n'.join(table)


    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.input_layers) + '*->' + self._morph_analysis_layer + '*)'

