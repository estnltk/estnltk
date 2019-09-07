#
#  Provides Vabamorf-based morphological analysis and disambiguation.
#
#  VabamorfTagger can be used for end-to-end morphological processing.
#  Alternatively, the process can be broken down into substeps, using 
#  VabamorfAnalyzer, PostMorphAnalysisTagger and VabamorfDisambiguator.
# 
from typing import MutableMapping

from estnltk import Annotation
from estnltk.text import Layer, Text
from estnltk.layer.span import Span

from estnltk.taggers import Tagger
from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers import PostMorphAnalysisTagger, Retagger

from estnltk.taggers.morph_analysis.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from estnltk.taggers.morph_analysis.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from estnltk.taggers.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND
from estnltk.taggers.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import IGNORE_ATTR

from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.morph_analysis.morf_common import _span_to_records_excl
from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation

from estnltk.taggers.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.morph_analysis.morf_common import _convert_vm_records_to_morph_analysis_records


class VabamorfTagger(Tagger):
    """Tags morphological analysis on words. Uses Vabamorf's analyzer and disambiguator.

    """
    output_attributes = ESTNLTK_MORPH_ATTRIBUTES

    conf_param = [# VM configuration flags:
                  "guess",
                  "propername",
                  'disambiguate',
                  "compound",
                  "phonetic",
                  # postanalysis tagger
                  'postanalysis_tagger',
                  # Internal stuff: layer names
                  '_input_compound_tokens_layer',
                  '_input_words_layer',
                  '_input_sentences_layer',
                  # Internal stuff: taggers
                  '_vabamorf_analyser',
                  '_corpusbased_disambiguator',
                  '_vabamorf_disambiguator',
                  'converter_module'
    ]

    def __init__(self,
                 output_layer='morph_analysis',
                 input_words_layer='words',
                 input_sentences_layer='sentences',
                 input_compound_tokens_layer='compound_tokens',
                 postanalysis_tagger=None,
                 guess = DEFAULT_PARAM_GUESS,
                 propername = DEFAULT_PARAM_PROPERNAME,
                 disambiguate = DEFAULT_PARAM_DISAMBIGUATE,
                 compound = DEFAULT_PARAM_COMPOUND,
                 phonetic = DEFAULT_PARAM_PHONETIC,
                 converter_module='default_v0'):
        """Initialize VabamorfTagger class.

        Note: Keyword arguments 'disambiguate', 'guess', 'propername',
        'phonetic' and 'compound' can be used to override the default 
        configuration of Vabamorf's morphological analyser. See the 
        description of VabamorfAnalyzer.tag method for details on
        configuration arguments.
        
        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the layer where analysis results are stored.
        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input compound_tokens layer. 
            This layer is required by the default postanalysis_tagger.
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        postanalysis_tagger: estnltk.taggers.Retagger (default: PostMorphAnalysisTagger())
            Retagger that is used to post-process "morph_analysis" layer after
            it is created (and before it is disambiguated).
            This tagger corrects morphological analyses, prepares morpho-
            logical analyses for disambiguation (if required) and fills in 
            values of extra attributes in morph_analysis Spans.
        guess: boolean (default: True)
            Use guessing in case of unknown words.
        propername: boolean (default: True)
            Propose additional analysis variants for proper names 
            (a.k.a. proper name guessing).
        disambiguate: boolean (default: True)
            Disambiguate morphological analyses with Vabamorf's 
            disambiguator.
        compound: boolean (default: True)
            Add compound word markers to root forms.
        phonetic: boolean (default: False)
            Add phonetic information to root forms.
        """
        self.converter_module = converter_module
        # Set VM analysis parameters:
        self.guess        = guess
        self.propername   = propername
        self.disambiguate = disambiguate
        self.compound     = compound
        self.phonetic     = phonetic
        # Set configuration parameters
        self.output_layer = output_layer
        self._input_compound_tokens_layer = input_compound_tokens_layer
        self._input_words_layer = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self.input_layers = [self._input_words_layer, self._input_sentences_layer]
        # Check if the user has provided a custom postanalysis_tagger
        if not postanalysis_tagger:
            # Initialize default postanalysis_tagger
            postanalysis_tagger = PostMorphAnalysisTagger(output_layer=output_layer,\
                                                          input_compound_tokens_layer=input_compound_tokens_layer, \
                                                          input_words_layer=input_words_layer, \
                                                          input_sentences_layer=input_sentences_layer )
        # Initialize postanalysis_tagger;
        if postanalysis_tagger:
            # Check for Retagger
            assert isinstance(postanalysis_tagger, Retagger), \
                '(!) postanalysis_tagger should be of type estnltk.taggers.Retagger.'
            # Check for layer match
            assert hasattr(postanalysis_tagger, 'output_layer'), \
                '(!) postanalysis_tagger does not define output_layer.'
            assert postanalysis_tagger.output_layer == self.output_layer, \
                '(!) postanalysis_tagger should modify layer "'+str(self.output_layer)+'".'+\
                ' Currently, it modifies layer "'+str(postanalysis_tagger.output_layer)+'".'
            #assert hasattr(postanalysis_tagger, 'attributes'), \
            #    '(!) postanalysis_tagger does not define any attributes.'
        self.postanalysis_tagger = postanalysis_tagger
        # Initialize morf analyzer and disambiguator;
        # Also propagate layer names to submodules;
        vm_instance = Vabamorf.instance()
        self._vabamorf_analyser      = VabamorfAnalyzer( vm_instance=vm_instance,
                                                        output_layer=output_layer,
                                                        input_words_layer=self._input_words_layer,
                                                        input_sentences_layer=self._input_sentences_layer,
                                                        guess=self.guess,
                                                        propername=self.propername,
                                                        compound=self.compound,
                                                        phonetic=self.phonetic)
        self._vabamorf_disambiguator = VabamorfDisambiguator( vm_instance=vm_instance,
                                                             output_layer=output_layer,
                                                             input_words_layer=self._input_words_layer,
                                                             input_sentences_layer=self._input_sentences_layer )
        # Update dependencies: add dependencies specific to postanalysis_tagger
        if postanalysis_tagger and postanalysis_tagger.input_layers:
            for postanalysis_dependency in postanalysis_tagger.input_layers:
                if postanalysis_dependency not in self.input_layers and \
                   postanalysis_dependency != self.output_layer:
                    self.input_layers.append( postanalysis_dependency )
        # Updated attributes
        if self.postanalysis_tagger is not None:
            # If disambiguation is not performed, then the default
            # postanalysis_tagger introduces _ignore attribute
            if not self.disambiguate:
                for extra_attribute in postanalysis_tagger.output_attributes:
                    if extra_attribute not in self.output_attributes:
                        self.output_attributes += (extra_attribute, )

    def _make_layer(self, text: Text, layers, status: dict):
        """Analyses given Text object morphologically.

        Note: exact configuration of the analysis (e.g.
        whether guessing of unknown words will be performed,
        or whether analyses will be disambiguated) depends on
        the initialization parameters of the class.

        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed morphologically.
            The Text object must have layers 'words', 'sentences'.

        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the
           name of the layer to the Layer object. Must contain
           words, and sentences;

        status: dict
           This can be used to store metadata on layer tagging.
        """
        # --------------------------------------------
        #   Morphological analysis
        # --------------------------------------------
        morph_layer = self._vabamorf_analyser.make_layer( text, layers, status )
        layers_with_morph = layers.copy()
        layers_with_morph[self.output_layer] = morph_layer
        # TODO: Apply text-based pre-disambiguation of proper names (if required)
        # --------------------------------------------
        #   Post-processing
        # --------------------------------------------
        if self.postanalysis_tagger:
            # Post-analysis tagger is responsible for:
            # 1) Retagging "morph_analysis" layer with post-corrections;
            # 2) Adding and filling in extra_attributes in "morph_analysis" layer;
            self.postanalysis_tagger.change_layer( text, layers_with_morph, status )
        # --------------------------------------------
        #   Morphological disambiguation
        # --------------------------------------------
        if self.disambiguate:
            self._vabamorf_disambiguator.change_layer( text, layers_with_morph, status )
        # TODO: Apply text-based post-disambiguation of proper names (if required)
        morph_layer.dict_converter_module = self.converter_module
        for span in morph_layer:
            for annotation in span.annotations:
                if annotation['root_tokens'] is not None:
                    annotation['root_tokens'] = list(annotation['root_tokens'])
        return morph_layer


# ========================================================
#    Util: find a matching morphological analysis
#          record from a list of records;
# ========================================================

def _find_matching_old_record( new_record, old_records ):
    '''Finds a record from old_records that matches the morphological
       analyses attributes of the new record. Returns the matching
       record, or None, if matching record was not found.
       Two records are considered as matching if all of their 
       VABAMORF_ATTRIBUTES's values are equal;
        
       Parameters
       ----------
       new_record: dict
           a record which match from old_records will be sought;

       old_records: list of dict
           list of old records from which a matching records will 
           be sought;

       Returns
       -------
       dict
           matching record from old_records, or None, if no matching 
           record was found;
    '''
    assert old_records is not None
    for old_record in old_records:
        attr_matches = []
        for attr in VABAMORF_ATTRIBUTES:
            attr_match = \
                 (old_record.get(attr,None) == new_record.get(attr,None))
            attr_matches.append( attr_match )
        if all( attr_matches ):
            # Return matching old record
            return old_record
    return None


# ========================================================
#    Check if the span is to be ignored during 
#          the morphological disambiguation
# ========================================================

def _is_ignore_span(span):
    """ Checks if the given span (from the layer 'morph_analysis')
        has attribute IGNORE_ATTR, and whether all of its values
        are True (which means: the span should be ignored).

        Note: if some values are True, and others are False or None,
        then throws an Exception because partial ignoring is
        currently not implemented.
    """
    ignore_values = [annotation.get(IGNORE_ATTR) for annotation in span.annotations]
    if all(ignore_values):
        return True
    if any(ignore_values):
        # Only some of the Spans have ignore=True, but
        # partial ignoring is currently not implemented
        raise Exception('(!) Partial ignoring is currently not '+\
                        'implemented. Unexpected ignore attribute '+\
                        "values encountered at the 'morph_analysis' "+\
                        'span '+str((span.start,span.end))+'.')
    return False


# ===============================
#    VabamorfAnalyzer
# ===============================

class VabamorfAnalyzer( Tagger ):
    """Performs morphological analysis with Vabamorf's analyzer.
       Note: resulting analyses will be ambiguous."""
    output_layer      = 'morph_analysis'
    output_attributes = VabamorfTagger.output_attributes
    input_layers      = ['words', 'sentences']
    conf_param = [ # Configuration flags:
                   "guess",
                   "propername",
                   "compound",
                   "phonetic",
                   # Internal stuff:
                   '_vm_instance', \
                   # Names of the specific input layers:
                   '_input_words_layer', \
                   '_input_sentences_layer', \
                   # For backward compatibility:
                   'depends_on', 'layer_name', 'attributes',
                   # Extra configuration flags:
                   'extra_attributes', \
                 ]
    layer_name = output_layer       # <- For backward compatibility ...
    depends_on = input_layers       # <- For backward compatibility ...
    attributes = output_attributes  # <- For backward compatibility ...
    
    def __init__(self,
                 output_layer='morph_analysis',
                 input_words_layer='words',
                 input_sentences_layer='sentences',
                 extra_attributes=None,
                 vm_instance=None,
                 guess = DEFAULT_PARAM_GUESS,
                 propername = DEFAULT_PARAM_PROPERNAME,
                 compound = DEFAULT_PARAM_COMPOUND,
                 phonetic = DEFAULT_PARAM_PHONETIC ):
        """Initialize VabamorfAnalyzer class.

        Parameters
        ----------
        layer_name: str (default: 'morph_analysis')
            Name of the layer where morph analysis results 
            will be stored.
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        extra_attributes: list of str (default: None)
            List containing names of extra attributes that will be 
            attached to Spans. All extra attributes will be 
            initialized to None.
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for analysing
            text morphologically.
        propername: boolean (default: True)
            Propose additional analysis variants for proper names 
            (a.k.a. proper name guessing).
        guess: boolean (default: True)
            Use guessing in case of unknown words.
        compound: boolean (default: True)
            Add compound word markers to root forms.
        phonetic: boolean (default: False)
            Add phonetic information to root forms.
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self.input_layers = [input_words_layer, input_sentences_layer]
        self.extra_attributes = extra_attributes
        if self.extra_attributes:
            for extra_attr in self.extra_attributes:
                self.output_attributes += (extra_attr,)
            self.attributes = self.output_attributes  # <- For backward compatibility ...
        if vm_instance:
            self._vm_instance = vm_instance
        else:
            self._vm_instance = Vabamorf.instance()
        # Set analysis parameters:
        self.guess = guess
        self.propername = propername
        self.compound = compound
        self.phonetic = phonetic
        # Other stuff
        self.layer_name = self.output_layer  # <- For backward compatibility ...
        self.depends_on = self.input_layers  # <- For backward compatibility ...

    def _make_layer(self, text: Text, layers, status: dict):
        """Analyses given Text object morphologically. 
        
        Note: disambiguation is not performed, so the results of
        analysis will (most likely) be ambiguous.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed morphologically.
            The Text object must have layers 'words', 'sentences'.
        
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           words, and sentences;
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        # Fetch parameters of the analysis
        current_kwargs = {}
        current_kwargs["disambiguate"] = False # perform analysis without disambiguation
        current_kwargs["guess"]      = self.guess
        current_kwargs["propername"] = self.propername
        current_kwargs["compound"]   = self.compound
        current_kwargs["phonetic"]   = self.phonetic
        # --------------------------------------------
        #   Use Vabamorf for morphological analysis
        # --------------------------------------------
        # Perform morphological analysis sentence by sentence
        word_layer = layers[self._input_words_layer]
        word_span_id = 0
        analysis_results = []
        for sentence in layers[self._input_sentences_layer]:
            # A) Collect all words inside the sentence
            sentence_words = []
            while word_span_id < len(word_layer):
                span = word_layer[word_span_id]
                if sentence.start <= span.start and \
                    span.end <= sentence.end:
                    # Word is inside the sentence
                    sentence_words.append(
                        _get_word_text( span ) 
                    )
                    word_span_id += 1
                elif sentence.end <= span.start:
                    break
            # B) Use Vabamorf for analysis 
            #    (but check length limitations first)
            if len(sentence_words) > 15000:
                # if 149129 < len(wordlist) on Linux,
                # if  15000 < len(wordlist) < 17500 on Windows,
                # then self.instance.analyze(words=wordlist, **self.current_kwargs) raises
                # RuntimeError: CFSException: internal error with vabamorf
                for i in range(0, len(sentence_words), 15000):
                    analysis_results.extend( self._vm_instance.analyze(words=sentence_words[i:i+15000], **current_kwargs) )
            else:
                analysis_results.extend( self._vm_instance.analyze(words=sentence_words, **current_kwargs) )

        # Assert that all words obtained an analysis 
        # ( Note: there must be empty analyses for unknown 
        #         words if guessing is not used )
        assert len(layers[ self._input_words_layer ]) == len(analysis_results), \
            '(!) Unexpectedly the number words ('+str(len(layers[ self._input_words_layer ]))+') '+\
            'does not match the number of obtained morphological analyses ('+str(len(analysis_results))+').'

        # --------------------------------------------
        #   Store analysis results in a new layer     
        # --------------------------------------------
        # A) Create layer
        morph_attributes   = self.output_attributes
        current_attributes = morph_attributes
        morph_layer = Layer(name  =self.output_layer,
                            parent=self._input_words_layer,
                            text_object=text,
                            ambiguous=True,
                            attributes=current_attributes )
        # B) Populate layer
        for word, analyses_dict in zip(layers[ self._input_words_layer ], analysis_results):
            # Convert from Vabamorf dict to a list of Spans
            records = _convert_vm_records_to_morph_analysis_records(analyses_dict, layer_attributes=current_attributes,
                                                                    sort_analyses=True)
            # Attach spans (if word has morphological analyses)
            for record in records:
                # the analyses here are not always unique
                morph_layer.add_annotation(word.base_span, **record)
            if not records:
                # if word has no morphological analyses (e.g.
                # it is an unknown word), then attach an 
                # empty Span as a placeholder
                morph_layer.add_annotation(word.base_span)

        # C) Return the layer
        return morph_layer



# ===============================
#    VabamorfDisambiguator
# ===============================

class VabamorfDisambiguator(Retagger):
    """Disambiguates morphologically analysed texts. 
       Uses Vabamorf for disambiguating.
    """
    attributes    = VabamorfTagger.output_attributes
    conf_param = ['depends_on', '_vm_instance',
                  '_input_words_layer',
                  '_input_sentences_layer' ]

    def __init__(self,
                 output_layer='morph_analysis',
                 input_words_layer='words',
                 input_sentences_layer='sentences',
                 vm_instance=None):
        """Initialize VabamorfDisambiguator class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer. 
            This is the layer where the disambiguation will
            be performed;
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for 
            disambiguating text morphologically;
        """
        # Set attributes & configuration
        self.output_layer = output_layer
        self.output_attributes = self.attributes
        self.input_layers = [input_words_layer, \
                             input_sentences_layer, \
                             output_layer ]
        self._input_words_layer     = self.input_layers[0]
        self._input_sentences_layer = self.input_layers[1]
        self.depends_on = self.input_layers
        if vm_instance:
            self._vm_instance = vm_instance
        else:
            self._vm_instance = Vabamorf.instance()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict = None) -> None:
        """Performs morphological disambiguation, and replaces ambiguous 
           morphological analyses with their disambiguated variants.
           
           Also, removes the temporary attribute '_ignore' from the 
           the morph_analysis layer.

           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which will be 
              morphologically disambiguated;
              
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain words, sentences, and morph_analysis layers. 
              The morph_analysis layer will be retagged.
              
           status: dict
              This can be used to store metadata on layer retagging.
        """
        # --------------------------------------------
        #  Check for existence of required layers     
        #  Collect layer's attributes                 
        # --------------------------------------------
        assert self.output_layer in layers
        assert self._input_sentences_layer in layers
        assert self._input_words_layer in layers
        # Take attributes from the input layer
        current_attributes = layers[self.output_layer].attributes
        # Check if there are any extra attributes to carry over
        # from the old layer
        extra_attributes = []
        for cur_attr in current_attributes:
            if cur_attr not in self.attributes and \
               cur_attr != IGNORE_ATTR:
                extra_attributes.append( cur_attr )
        # Check that len(word_spans) >= len(morph_spans)
        morph_layer = layers[self.output_layer]
        word_spans  = layers[self._input_words_layer]
        assert len(word_spans) >= len(morph_layer), \
            '(!) Unexpectedly, the number of elements at the layer '+\
                 '"'+str(self.output_layer)+'" is greater than the '+\
                 'number of elements at the layer "words". There '+\
                 'should be one to one correspondence between '+\
                 'the layers.'
        # --------------------------------------------
        #  Disambiguate sentence by sentence
        # --------------------------------------------
        sentence_start_morph_span_id = 0
        morph_span_id = 0
        word_span_id  = 0
        for sentence in layers[self._input_sentences_layer]:
            # A) Collect all words/morph_analyses inside the sentence
            #    Assume: len(word_spans) >= len(morph_layer)
            sentence_word_spans  = []
            sentence_morph_spans = []
            sentence_morph_dicts = []
            words_missing_morph  = []
            ignored_word_ids     = set()
            sentence_start_morph_span_id = morph_span_id
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                morph_span = None
                if sentence.start <= word_span.start and \
                    word_span.end <= sentence.end:
                    morphFound = False
                    # Get corresponding morph span
                    if morph_span_id < len(morph_layer):
                        morph_span = morph_layer[morph_span_id]
                        if word_span.start == morph_span.start and \
                           word_span.end == morph_span.end and \
                           not _is_empty_annotation(morph_span.annotations[0]):
                            # Word & morph found: collect items
                            sentence_word_spans.append( word_span )
                            sentence_morph_spans.append( morph_span )
                            if not _is_ignore_span( morph_span ):
                                # Add the dict only if it is not marked as 
                                # to be ignored 
                                word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict( \
                                        morph_span )
                                sentence_morph_dicts.append( word_morph_dict )
                            else:
                                # Remember that this word was ignored during 
                                # the disambiguation
                                ignored_word_ids.add( len(sentence_word_spans)-1 )
                            # Advance positions
                            morph_span_id += 1
                            word_span_id  += 1
                            morphFound = True
                    if not morphFound:
                        # Did not find any morph analysis for the word
                        words_missing_morph.append( word_span )
                        word_span_id  += 1
                        # Advance morph position, if morph was empty
                        if morph_span and _is_empty_annotation(morph_span.annotations[0]):
                            morph_span_id += 1
                elif sentence.end <= word_span.start:
                    # Word falls out of the sentence: break
                    break
            # B) Validate that all words have morphological analyses;
            #    If not (e.g. guessing was switched off while analysing), 
            #    then we cannot perform the disambiguation;
            if words_missing_morph:
                missing_pos = [(w.start, w.end) for w in words_missing_morph]
                raise Exception('(!) Unable to perform morphological disambiguation '+\
                                'because words at positions '+str(missing_pos)+' '+\
                                'have no morphological analyses.')
            # C) Use Vabamorf for disambiguation
            disambiguated_dicts = []
            if sentence_morph_dicts:
                disambiguated_dicts = self._vm_instance.disambiguate(sentence_morph_dicts)
            # D) Convert Vabamorf's results to AmbiguousSpans
            global_morph_span_id = sentence_start_morph_span_id
            wid = 0
            morph_dict_id = 0
            while wid < len(sentence_word_spans):
                # D.0) Find corresponding analysis_dict
                while wid in ignored_word_ids:
                    # Skip the ignored words: they should preserve the 
                    # same analyses as in the input
                    global_morph_span_id += 1
                    wid += 1
                if not wid < len(sentence_word_spans):
                    # Break if ignoring has passed sentence boundaries
                    break
                
                # D.0) Get comparable morphological analyses for the word
                # Old morphological analyses (ambiguous):
                old_morph_records = \
                    [ _span_to_records_excl(span, [IGNORE_ATTR]) for span in sentence_morph_spans[wid].annotations ]
                # New morphological analyses (disambiguated):
                disambiguated_records = disambiguated_dicts[morph_dict_id]['analysis']

                # D.1) Convert records back to AmbiguousSpans
                ambiguous_span = Span(base_span=morph_layer[global_morph_span_id].base_span, layer=morph_layer)
                
                # D.1) Rewrite records into a proper format, and 
                #      add to the span
                
                # Sort analyses ( to assure a fixed order, e.g. for testing purpose )
                disambiguated_records = sorted( disambiguated_records, key = \
                         lambda x: x['root']+x['ending']+x['clitic']+x['partofspeech']+x['form'], 
                         reverse=False )
                for analysis_record in disambiguated_records:
                    new_record = {}
                    # Fill in attributes of the record
                    for attr in current_attributes:
                        if attr in analysis_record:
                            # We have a Vabamorf's attribute
                            if attr == 'root_tokens':
                                # make it hashable for Span.__hash__
                                new_record[attr] = tuple(analysis_record[attr])
                            else:
                                new_record[attr] = analysis_record[attr]
                        else:
                            # We have an extra attribute -- initialize with None
                            new_record[attr] = None
                    if extra_attributes:
                        # Carry over attribute values (if needed)
                        matching_old_record = \
                            _find_matching_old_record( new_record, old_morph_records )
                        if matching_old_record:
                            for ex_attrib in extra_attributes:
                                new_record[ex_attrib] = matching_old_record[ex_attrib]
                        else:
                            raise Exception('(!) Unable to find a matching record for '+\
                                    str(new_record)+' from '+str(old_morph_records))
                    # Add new record to the ambiguous span
                    ambiguous_span.add_annotation(Annotation(ambiguous_span, **new_record))

                # D.2) Rewrite the old span with the new one
                morph_layer[global_morph_span_id] = ambiguous_span
                
                # Advance indices
                global_morph_span_id += 1
                morph_dict_id += 1
                wid += 1
        # --------------------------------------------
        #  Post-processing:
        #  Remove IGNORE_ATTR from the output layer
        # --------------------------------------------
        if IGNORE_ATTR in morph_layer.attributes:
            morph_layer.attributes = [attr for attr in morph_layer.attributes if attr != IGNORE_ATTR]

            for span in morph_layer:
                for annotation in span.annotations:
                    delattr(annotation, IGNORE_ATTR)
