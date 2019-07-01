#
#  Record-based retagger for rewriting morph_analysis layer.
#  Allows manipulating of morph analysis layer by changing 
#  dictionary representations of analyses.
#  

from estnltk import Text
from estnltk.layer.ambiguous_span import AmbiguousSpan

from estnltk.taggers import Retagger

from estnltk.taggers.morph_analysis.morf_common import _create_empty_morph_record
from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.morph_analysis.morf import VabamorfTagger


class MorphAnalysisRecordBasedRetagger(Retagger):
    """ Retagger for record-based retagging of the morph_analysis layer.

        Disassembles morph analyses into records, which contain a list of 
        analysis dictionaries for each word, and passes the records to the 
        method rewrite_words for changing. Afterwards, converts rewritten 
        records back to annotations of the layer.
        
        This is a base class that can be used  by  retaggers  that  need 
        to  manipulate  morph  analysis  layer  by  changing  dictionary  
        representations of analyses.
        Inheriting classes should implement method:
            rewrite_words(...)
    """
    output_attributes = VabamorfTagger.output_attributes
    conf_param = [ # configuration
                   'add_normalized_word_form',\
                   'add_sentence_ids',\
                   # input layers
                   '_input_morph_analysis_layer',\
                   '_input_words_layer',\
                   '_input_sentences_layer',\
                   # For backward compatibility:
                   'depends_on', 'layer_name', 'attributes' ]
    attributes = output_attributes  # <- For backward compatibility ...
    
    def __init__(self, morph_analysis_layer:str='morph_analysis', \
                       add_normalized_word_form: bool = False, \
                       input_words_layer:str='words',\
                       add_sentence_ids: bool = False, \
                       input_sentences_layer:str='sentences' ):
        """ Initialize MorphAnalysisRecordBasedRetagger class.
            
            Parameters
            ----------
            morph_analysis_layer: str (default: 'morph_analysis')
                Name of the morphological analysis layer that is to be changed;
            
            add_normalized_word_form: bool (default: False)
                If True, then morphological analyses dictionaries will be 
                populated with normalized word forms (under keys 'word_normal'),
                which will be taken from the input_words_layer;
            
            input_words_layer: str (default: 'words')
                Name of the input words layer. This is the layer from where 
                normalized word forms will be obtained.  Note: this layer will be 
                added to the list of input_layer only if add_normalized_word_form==True;

            add_sentence_ids: bool (default: False)
                If True, then morphological analyses dictionaries will be 
                populated with sentence id-s (under keys 'sentence_id'),
                referring to sentences from which the analyses were taken.
                Sentence id-s will be obtained from the input_sentences_layer;
                
            input_sentences_layer: str (default: 'sentences')
                Name of the input sentences layer. This is the layer from where 
                sentence id-s will be obtained.  Note: this layer will be added to 
                the list of input_layer only if  add_sentence_ids==True;
                
        """
        # Set input/output layer names
        self.output_layer = morph_analysis_layer
        self._input_morph_analysis_layer = morph_analysis_layer
        self._input_words_layer = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self.add_sentence_ids = add_sentence_ids
        self.add_normalized_word_form = add_normalized_word_form
        self.input_layers = [morph_analysis_layer]
        if add_normalized_word_form:
            self.input_layers.append( self._input_words_layer )
        if add_sentence_ids:
            self.input_layers.append( self._input_sentences_layer )
        self.layer_name = self.output_layer  # <- For backward compatibility ...
        self.depends_on = self.input_layers  # <- For backward compatibility ...

    def rewrite_words(self, words:list):
        """ Method responsible for rewriting morph analyses. 
            Inheriting classes should implement this method.
            
            Parameters
            ----------
            words:list
               a list of word analyses: a list that contains sub
               lists of dictionaries; Example structure:
                  [
                    # Analyses of the 1st word:
                    [ {'lemma': ..., 'partofspeech': ..., ... },
                      {'lemma': ..., 'partofspeech': ..., ... },
                      ...
                    ],
                    # Analyses of the 2nd word:
                    [ {'lemma': ..., 'partofspeech': ..., ... },
                      {'lemma': ..., 'partofspeech': ..., ... },
                      ...
                    ],
                    ...
                  ]
               ( each dictionary contains a single morphological 
                 analysis, and the list of dictionaries represent 
                 all analyses of the word )
            
            Returns (2 options)
            --------------------
            1) a list of word analyses. Must be in the same format
               as the input list words.
               (a list that contains sub lists of dictionaries)
            
            2) a tuple of two elements, where:
               2.1) the first element is a list of word analyses (1);
               2.2) the second element is a  set  of  words  ids, 
                    indicating words that were changed in rewrite_words; 
                    this is used to optimize the layer rewriting -- 
                    annotations of unchanged records will not be modified;

        """
        raise NotImplementedError('rewrite_words method not implemented in ' + self.__class__.__name__)

    def _change_layer(self, text, layers, status: dict):
        """Retags morph_analysis layer.
        
        Parameters
        ----------
        text: Text
           Text object that will be retagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must 
           contain morph_analysis layer;
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        # 1) Convert morph analyses to records (dictionaries)
        morph_analysis = layers[ self._input_morph_analysis_layer ]
        words_layer = None
        sentences_layer = None
        if self.add_normalized_word_form:
            words_layer = layers[ self._input_words_layer ]
            assert len(words_layer) == len(morph_analysis)
        if self.add_sentence_ids:
            sentences_layer = layers[ self._input_sentences_layer ]
         # Take attributes from the input layer
        current_attributes = morph_analysis.attributes
        # Convert morph_analysis into records
        morph_analysis_records = []
        sentence_id = 0
        for wid, word_morph in enumerate( morph_analysis ):
            word_records = word_morph.to_records()
            # Add normalized word forms (if required)
            if self.add_normalized_word_form:
                normalized_text = _get_word_text( words_layer[wid] )
                for rec in word_records:
                    rec['word_normal'] = normalized_text
            # Add sentence ids (if required)
            if self.add_sentence_ids:
                cur_sentence = sentences_layer[sentence_id]
                assert cur_sentence.start <= word_morph.start and \
                       word_morph.end <= cur_sentence.end
                for rec in word_records:
                    rec['sentence_id'] = sentence_id
                if word_morph.end == cur_sentence.end:
                    # Take the next sentence
                    sentence_id += 1
            morph_analysis_records.append( word_records )
        
        # 2) Rewrite records (all words at once)
        results = self.rewrite_words(morph_analysis_records)
        # 3) Disassemble results, and do some initial checks on them
        changed_words = set( list(range(len(morph_analysis_records))) )
        if isinstance(results, tuple):
            assert len(results) == 2, \
                   '(!) Expected a tuple with 2 elements, but got {!r} instead.'.format(results[1])
            assert isinstance(results[0], list), \
                   '(!) Expected a list, but found {!r} instead.'.format(results[0])
            # new list of analyses
            new_morph_analysis_records = results[0]
            assert isinstance(results[1], set), \
                   '(!) Expected a set, but found {!r} instead.'.format(results[1])
            # words that were changed:
            changed_words = results[1]
        elif isinstance(results, list):
            # new list of analyses
            new_morph_analysis_records = results
        else:
            raise Exception('(!) Unexpected type of rewriting result: {}'.format(type(results)))
        # Sanity check: all words must still have a record
        morph_spans = layers[self._input_morph_analysis_layer].spans
        assert len(new_morph_analysis_records) == len(morph_spans), \
               ('(!) Number of rewritten morph_analysis records ({}) does not match the initial '+\
                'number of morph analyses ({}).').format( len(new_morph_analysis_records),\
                                                          len(morph_spans) )
        
        # 4) Convert records back to morph analyses
        for wid, morph_word in enumerate( morph_spans ):
            # 4.0) Check if the word can be skipped (no changes were made during rewrite_words)
            if wid not in changed_words:
                continue
            morph_records = new_morph_analysis_records[wid]
            assert isinstance(morph_records, list), \
                   '(!) Expected a list of records, but found {!r}'.format(morph_records)
            # 4.1) Convert records back to AmbiguousSpans
            ambiguous_span = AmbiguousSpan(base_span=morph_spans[wid].base_span, layer=morph_spans[wid].layer)
            annotation_added = False
            for new_record in morph_records:
                assert isinstance(new_record, dict), \
                   '(!) Expected a dictionary, but found {!r}'.format(new_record)
                # Make sure that all current_attributes are present;
                # Perform normalization and initialize missing attribs
                # with None
                for attr in current_attributes:
                    if attr in new_record:
                        if attr == 'root_tokens':
                            # normalize 'root_tokens'
                            new_record[attr] = tuple( new_record[attr] )
                    else:
                        # We have an extra attribute that is missing:
                        # initialize it with None
                        new_record[attr] = None
                ambiguous_span.add_annotation( **new_record )
                annotation_added = True
            if not annotation_added:
                # Create an empty record
                new_record = _create_empty_morph_record(
                                     word=morph_word.parent,
                                     layer_attributes=current_attributes)
                ambiguous_span.add_annotation( **new_record )
            # 4.2) Rewrite the old span with the new one
            morph_spans[wid] = ambiguous_span
        # 5) Return rewritten layer
        return morph_analysis

