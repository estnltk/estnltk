#
#  Record-based retagger for rewriting morph_analysis layer.
#  Allows manipulating of morph analysis layer by changing 
#  dictionary representations of analyses.
#  

from estnltk import Text
from estnltk.layer.ambiguous_span import AmbiguousSpan

from estnltk.taggers import Retagger

from estnltk.taggers.morph_analysis.morf_common import _create_empty_morph_record
from estnltk.taggers.morph_analysis.morf import VabamorfTagger


class MorphAnalysisRecordBasedRetagger(Retagger):
    """ Retagger for record-based retagging of the morph_analysis layer.

        Disassembles morph analyses into records, which contain a list of 
        analysis dictionaries for each word, and passes the records to the 
        method rewrite_words for changing. Afterwards, converts rewritten 
        records back to annotations of the layer.
        
        This is a base class that can be used  by  retaggers  that  need 
        to manipulate morph analysis layer  in  a  straightforward  manner:
        by changing dictionary representations of analyses.
        Inheriting classes should implement method:
            rewrite_words(...)
    """
    output_attributes = VabamorfTagger.attributes
    conf_param = [ '_input_morph_analysis_layer',
                   # For backward compatibility:
                   'depends_on', 'layer_name', 'attributes' ]
    attributes = output_attributes  # <- For backward compatibility ...
    
    def __init__(self, output_layer:str='morph_analysis', \
                       input_morph_analysis_layer:str='morph_analysis'):
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [input_morph_analysis_layer]
        self.layer_name = self.output_layer  # <- For backward compatibility ...
        self.depends_on = self.input_layers  # <- For backward compatibility ...

    def rewrite_words(self, words:list):
        """ Method responsible for rewriting morph analyses. 
            Inheriting classes should implement this method.
            
            The method should return either:
            1) a list of word analyses -- list that contains a sub
               lists of dictionaries; each dictionary contains a 
               single morphological analysis, and the list of 
               dictionaries represent all analyses of the word;
            
            2) a tuple of two elements, where:
               *) the first element is a list of word analyses (1);
               *) the second element is a  set  of  words  ids, 
                  indicating words  that  were  not  changed  in
                  rewrite_words; this is used to optimize the layer 
                  rewriting -- annotations of unchanged records 
                  will not be modified;
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
         # Take attributes from the input layer
        current_attributes = morph_analysis.attributes
        morph_analysis_records = []
        for wid, word_morph in enumerate( morph_analysis ):
            morph_analysis_records.append( word_morph.to_record() )
        
        # 2) Rewrite records (all words at once)
        results = self.rewrite_words(morph_analysis_records)
        # 3) Disassemble results, and do some initial checks on them
        skip_words = set()
        if isinstance(results, tuple):
            assert len(results) == 2, \
                   '(!) Expected a tuple with 2 elements, but got {!r} instead.'.format(results[1])
            assert isinstance(results[0], list), \
                   '(!) Expected a list, but found {!r} instead.'.format(results[0])
            # new list of analyses
            new_morph_analysis_records = results[0]
            assert isinstance(results[1], set), \
                   '(!) Expected a set, but found {!r} instead.'.format(results[1])
            # words that were not changed:
            skip_words = results[1]
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
            # 4.0) Check if the word can be skipped (no changes were made turing rewrite_words)
            if wid in skip_words:
                continue
            morph_records = new_morph_analysis_records[wid]
            assert isinstance(morph_records, list), \
                   '(!) Expected a list of records, but found {!r}'.format(morph_records)
            # 4.1) Convert records back to AmbiguousSpans
            ambiguous_span = \
                 AmbiguousSpan(layer=morph_spans[wid].layer, \
                               span =morph_spans[wid].span)
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
