#
#   Temporal expression tagger identifies temporal expressions 
#  (timexes) in text and normalizes these expressions, providing 
#  corresponding calendrical dates,  times  and  durations. The 
#  normalizing format is based on TimeML's TIMEX3 standard.
#    TimexTagger is a wrapper around CoreTimexTagger (a Java-based 
#  temporal tagger), which provides the main tagging functionality. 
#  The goal of TimexTagger is to provide better tokenization for 
#  CoreTimexTagger, as EstNLTK's standard tokenization contains 
#  some rules not suitable for timex tagging.
# 

from typing import Optional

from estnltk import Text, Layer

from estnltk.taggers import Tagger
from estnltk.taggers import TokensTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import VabamorfTagger
from estnltk.taggers.standard.timexes.timex_tagger_preprocessing import make_adapted_cp_tagger
from estnltk.taggers.standard.timexes.core_timex_tagger import CoreTimexTagger


class TimexTagger( Tagger ):
    """Detects and normalizes temporal expressions (timexes).
    Normalization involves providing calendrical dates, times 
    and durations corresponding to the expressions, based on 
    TimeML's TIMEX3 standard.
    
    This tagger is a wrapper around CoreTimexTagger (a Java-based 
    temporal tagger), which provides the main tagging functionality. 
    The goal of this class is to provide better tokenization for 
    CoreTimexTagger, as EstNLTK's standard tokenization contains 
    some rules not suitable for timex tagging.
    
    Important: after tagging is done and TimexTagger is no 
    longer needed, Java process should be released. 
    This can be done by calling tagger's close() method. 
    Alternatively, you can use TimexTagger inside a with context, 
    so that resources are released after the context automatically:
    
        with TimexTagger() as timex_tagger: 
            ...
            timex_tagger.tag( text )
            ...
    
    TimexTagger creates all the prerequisite layers of CoreTimexTagger 
    (words, sentences, morph_analysis) from the scratch. 
    By default, TimexTagger outputs a flat timexes layer, which 
    is not dependent of any existing segmentation layers of the 
    input Text object.
    
    If enveloped_words_layer is set, then TimexTagger attempts to 
    envelop detected timex phrases around the given words layer. 
    Note, however, that this can produce broken timex phrases 
    due to mismatches between standard and TimexTagger's 
    segmentations. This is indicated in layer's attribute 
    broken_phrase, which is a boolean marking timexes broken 
    because of tokenization errors. Also, layer's metadata will 
    report statistics about conflicts: timexes_discarded 
    (removed from output due to missing standard tokens), 
    timexes_broken (incorrect boundaries due to mismatching 
    segmentations) and timexes_ok (matching boundaries).
    """
    conf_param = [ 'enveloped_words_layer', 
                   'rules_file', 'pick_first_in_overlap', 
                   'mark_part_of_interval', 'output_ordered_dicts', 
                   
                   # Internal taggers
                   '_tokens_tagger',
                   '_cp_tokens_tagger',
                   '_words_tagger',
                   '_sentence_tokenizer',
                   '_morph_analyser',
                   '_timex_tagger'
                  ]

    def __init__(self, output_layer:str='timexes',
                       enveloped_words_layer:Optional[str]=None,
                       rules_file:str=None, \
                       pick_first_in_overlap:bool=True, \
                       mark_part_of_interval:bool=True, \
                       output_ordered_dicts:bool=True ):
        """Initializes temporal expression tagger.
        
        Parameters
        ----------
        output_layer: str (default: 'timexes')
            Name for the timexes layer;
        
        enveloped_words_layer: Optional[str] (default: None)
            Name of the enveloped words layer. If provided, then the output 
            layer will be an enveloping layer around the words layer.
            Otherwise, output layer will be a flat timexes layer. 
        
        rules_file: str (default: 'reeglid.xml')
             Initializes the temporal expression tagger with a custom rules file.
             The expected format of the rules file is described in  more  detail 
             here:
                 https://github.com/soras/Ajavt/blob/master/doc/writingRules.txt
        
        pick_first_in_overlap: boolean (default: True)
             If set, then in case of partially overlapping timexes the first timex
             will be preserved, and the following timex will be discarded. If not
             set, then all overlapping timexes will be preserved (Note: this likely
             creates conflicts with EstNLTK's data structures);
        
        mark_part_of_interval: boolean (default: True)
             If set, then the information about implicit intervals will also be 
             marked in the annotations. More specifically, all timexes will have an 
             additional attribute 'part_of_interval', and DATE and TIME expressions 
             that make up an interval (DURATION) will have their part_of_interval 
             filled in with a dictionary that contains attributes of the timex 
             tag of the corresponding interval.
             Otherwise (if mark_part_of_interval==False), the information about the 
             implicit intervals will be discarded;
        
        output_ordered_dicts: boolean (default: True)
             If set, then dictionaries in the timex attributes begin_point, end_point, 
             and part_of_interval will be converted into OrderedDict-s. Use this to 
             ensure fixed order of elements in the dictionaries (might be useful for
             nbval testing).
        """
        # Initialize required preprocessing taggers
        # Use custom layer names to avoid conflicts with EstNLTK's 
        # default layers
        self._tokens_tagger = TokensTagger( output_layer='timex_tagger_tokens' )
        self._cp_tokens_tagger = make_adapted_cp_tagger( input_tokens_layer='timex_tagger_tokens',
                                                         output_layer='timex_tagger_compound_tokens' )
        self._words_tagger = WordTagger( input_compound_tokens_layer='timex_tagger_compound_tokens',
                                         input_tokens_layer='timex_tagger_tokens',
                                         output_layer='timex_tagger_words' )
        self._sentence_tokenizer = SentenceTokenizer( \
                                input_compound_tokens_layer='timex_tagger_compound_tokens',
                                input_words_layer='timex_tagger_words',
                                output_layer='timex_tagger_sentences' )
        self._morph_analyser = VabamorfTagger( \
                                output_layer='timex_tagger_morph_analysis',
                                input_words_layer='timex_tagger_words',
                                input_sentences_layer='timex_tagger_sentences',
                                input_compound_tokens_layer='timex_tagger_compound_tokens' )
        self._timex_tagger = CoreTimexTagger( \
                                output_layer=output_layer,
                                input_words_layer='timex_tagger_words',
                                input_sentences_layer='timex_tagger_sentences',
                                input_morph_analysis_layer='timex_tagger_morph_analysis',
                                rules_file=rules_file, \
                                pick_first_in_overlap=pick_first_in_overlap, \
                                mark_part_of_interval=mark_part_of_interval, \
                                output_ordered_dicts=output_ordered_dicts, \
                                use_normalized_word_form=True )
        # Set configuration
        if isinstance(enveloped_words_layer, str):
            self.input_layers = [enveloped_words_layer]
            self.enveloped_words_layer = enveloped_words_layer
        else:
            self.input_layers = []
            self.enveloped_words_layer = None
        self.pick_first_in_overlap = self._timex_tagger.pick_first_in_overlap
        self.mark_part_of_interval = self._timex_tagger.mark_part_of_interval
        self.output_ordered_dicts  = self._timex_tagger.output_ordered_dicts
        self.rules_file = self._timex_tagger.rules_file
        self.output_layer = self._timex_tagger.output_layer
        self.output_attributes = self._timex_tagger.output_attributes
        if self.enveloped_words_layer is not None:
            self.output_attributes += ('broken_phrase', )


    def __enter__(self):
        # Initialize Java-based TimexTagger
        self._timex_tagger.__enter__()
        return self


    def __exit__(self, *args):
        # Close Java-based TimexTagger
        self._timex_tagger.__exit__(*args)
        return False


    def close(self):
        # Close Java-based TimexTagger
        self._timex_tagger.close()


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, 
                     text_object=None,
                     enveloping=self.enveloped_words_layer, 
                     attributes=self.output_attributes, 
                     ambiguous=False)


    def _make_layer(self, text, layers, status: dict):
        """Creates timexes layer.
        
        Parameters
        ----------
        text: Text
           Text in which timexes will be annotated;
        
        layers: MutableMapping[str, Layer]
           Layers of the text.  Contains mappings  from the 
           name of the layer to the Layer object. Must contain
           the words, sentences and morph_analysis layers.
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        
        # A) create auxiliary layers that provide custom tokenization
        pipeline = [self._tokens_tagger, self._cp_tokens_tagger, \
                    self._words_tagger, self._sentence_tokenizer, \
                    self._morph_analyser]
        for tagger in pipeline:
            tagger.tag( text )
        self._timex_tagger.tag( text )
        timexes_layer = text[ self._timex_tagger.output_layer ]
        
        # B) Create output layer
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        
        if self.enveloped_words_layer is None:
            # B1) Create flat timexes layer
            for timex in timexes_layer:
                original_annotation = timex.annotations[0]
                new_annotation = \
                    { attr:original_annotation[attr] for attr in timexes_layer.attributes }
                new_layer.add_annotation( (timex.start, timex.end), new_annotation )
        else:
            # B2) Try to align timexes layer with the existing words layer
            #     (which may have different tokenization than timextagger had)
            discarded = 0
            tokenization_mismatch = 0
            tokenization_match = 0
            word_spans = layers[ self.enveloped_words_layer ]
            word_span_id = 0
            for timex in timexes_layer:
                content_words = []
                # find word(s) corresponding to the timex
                while word_span_id < len(word_spans):
                    word = word_spans[word_span_id]
                    partial_match = False
                    if word.start == timex.start:
                        if word.end <= timex.end:
                            content_words.append( (word, True) )
                        elif word.end > timex.end:
                            content_words.append( (word, False) )
                            partial_match = True
                    elif word.start > timex.start:
                        if word.end <= timex.end:
                            if content_words:
                                content_words.append( (word, True) )
                            else:
                                content_words.append( (word, False) )
                                partial_match = True
                        elif word.end > timex.end:
                            content_words.append( (word, False) )
                            partial_match = True
                    if word.end >= timex.end:
                        break
                    word_span_id += 1
                if content_words:
                    base_spans = [wrd.base_span for (wrd, status) in content_words]
                    original_annotation = timex.annotations[0]
                    new_annotation = \
                        { attr:original_annotation[attr] for attr in timexes_layer.attributes }
                    new_annotation['broken_phrase'] = partial_match
                    if not partial_match:
                        tokenization_match += 1
                    else:
                        tokenization_mismatch += 1
                    new_layer.add_annotation( base_spans, new_annotation )
                else:
                    discarded += 1
            new_layer.meta['timexes_discarded'] = discarded
            new_layer.meta['timexes_broken'] = tokenization_mismatch
            new_layer.meta['timexes_ok'] = tokenization_match
        # Remove auxiliary layers
        text.pop_layer( self._tokens_tagger.output_layer )
        text.pop_layer( self._words_tagger.output_layer )
        if self._timex_tagger.output_layer in text.layers:
            text.pop_layer( self._timex_tagger.output_layer )
        for tagger in pipeline + [self._timex_tagger]:
            assert tagger.output_layer not in text.layers
        return new_layer



